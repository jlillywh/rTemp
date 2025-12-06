"""
Main RTempModel class for water temperature modeling.

This module contains the main orchestrator class that manages model execution,
state management, and coordinates all calculation components.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import pandas as pd

from rtemp.atmospheric.emissivity import (
    EmissivityBrunt,
    EmissivityBrutsaert,
    EmissivityIdsoJackson,
    EmissivityKoberg,
    EmissivitySatterlund,
    EmissivitySwinbank,
)
from rtemp.atmospheric.longwave import LongwaveRadiation
from rtemp.config import (
    DiagnosticOutput,
    HeatFluxComponents,
    ModelConfiguration,
    ModelState,
)
from rtemp.constants import (
    CAL_CM2_DAY_TO_WATTS_M2,
    WATTS_M2_TO_CAL_CM2_DAY,
    CELSIUS_TO_KELVIN,
    LARGE_TIMESTEP_RESET_HOURS,
    LARGE_TIMESTEP_WARNING_HOURS,
    METERS_TO_CM,
    WATER_DENSITY,
    WATER_SPECIFIC_HEAT,
    WATTS_M2_TO_CAL_CM2_DAY,
)
from rtemp.heat_flux.calculator import HeatFluxCalculator
from rtemp.solar.corrections import SolarRadiationCorrections
from rtemp.solar.position import NOAASolarPosition
from rtemp.solar.radiation_bird import SolarRadiationBird
from rtemp.solar.radiation_bras import SolarRadiationBras
from rtemp.solar.radiation_iqbal import SolarRadiationIqbal
from rtemp.solar.radiation_ryan import SolarRadiationRyanStolz
from rtemp.utils.atmospheric import AtmosphericHelpers
from rtemp.utils.conversions import UnitConversions
from rtemp.utils.validation import InputValidator
from rtemp.wind.adjustment import WindAdjustment
from rtemp.wind.functions import (
    WindFunctionBradyGravesGeyer,
    WindFunctionEastMesa,
    WindFunctionHelfrich,
    WindFunctionMarcianoHarbeck,
    WindFunctionRyanHarleman,
)

logger = logging.getLogger(__name__)


class RTempModel:
    """
    Main rTemp water temperature model class.

    This class orchestrates the calculation of water temperature using a
    comprehensive heat budget approach with configurable calculation methods.
    """

    def __init__(self, config: ModelConfiguration):
        """
        Initialize the rTemp model with configuration.

        Args:
            config: ModelConfiguration object containing all model parameters

        Raises:
            ValueError: If configuration parameters are invalid
        """
        # Validate configuration
        validated_config, warnings = InputValidator.validate_site_parameters(
            self._config_to_dict(config)
        )
        
        for warning in warnings:
            logger.warning(warning)
        
        self.config = config
        self.results: List[Dict] = []
        self.diagnostics: List[Dict] = []
        
        # Initialize method selectors
        self._init_solar_method()
        self._init_longwave_method()
        self._init_wind_function_method()

    def _config_to_dict(self, config: ModelConfiguration) -> Dict:
        """Convert ModelConfiguration to dictionary for validation."""
        return {
            'water_depth': config.water_depth,
            'effective_shade': config.effective_shade,
            'wind_height': config.wind_height,
            'effective_wind_factor': config.effective_wind_factor,
            'groundwater_temperature': config.groundwater_temperature,
            'groundwater_inflow': config.groundwater_inflow,
            'sediment_thermal_conductivity': config.sediment_thermal_conductivity,
            'sediment_thermal_diffusivity': config.sediment_thermal_diffusivity,
            'sediment_thickness': config.sediment_thickness,
            'hyporheic_exchange_rate': config.hyporheic_exchange_rate,
        }

    def _init_solar_method(self):
        """Initialize solar radiation calculation method."""
        method = self.config.solar_method
        if method == "Bras":
            self.solar_calculator = SolarRadiationBras()
        elif method == "Bird":
            self.solar_calculator = SolarRadiationBird()
        elif method == "Ryan-Stolzenbach":
            self.solar_calculator = SolarRadiationRyanStolz()
        elif method == "Iqbal":
            self.solar_calculator = SolarRadiationIqbal()
        else:
            raise ValueError(
                f"Unknown solar method: {method}. "
                f"Valid options: Bras, Bird, Ryan-Stolzenbach, Iqbal"
            )

    def _init_longwave_method(self):
        """Initialize longwave radiation emissivity method."""
        method = self.config.longwave_method
        if method == "Brunt":
            self.emissivity_calculator = EmissivityBrunt()
        elif method == "Brutsaert":
            self.emissivity_calculator = EmissivityBrutsaert(
                coefficient=self.config.brutsaert_coefficient
            )
        elif method == "Satterlund":
            self.emissivity_calculator = EmissivitySatterlund()
        elif method == "Idso-Jackson":
            self.emissivity_calculator = EmissivityIdsoJackson()
        elif method == "Swinbank":
            self.emissivity_calculator = EmissivitySwinbank()
        elif method == "Koberg":
            self.emissivity_calculator = EmissivityKoberg()
        else:
            raise ValueError(
                f"Unknown longwave method: {method}. "
                f"Valid options: Brunt, Brutsaert, Satterlund, Idso-Jackson, Swinbank, Koberg"
            )

    def _init_wind_function_method(self):
        """Initialize wind function calculation method."""
        method = self.config.wind_function_method
        if method == "Brady-Graves-Geyer":
            self.wind_function = WindFunctionBradyGravesGeyer()
        elif method == "Marciano-Harbeck":
            self.wind_function = WindFunctionMarcianoHarbeck()
        elif method == "Ryan-Harleman":
            self.wind_function = WindFunctionRyanHarleman()
        elif method == "East Mesa":
            self.wind_function = WindFunctionEastMesa()
        elif method == "Helfrich":
            self.wind_function = WindFunctionHelfrich()
        else:
            raise ValueError(
                f"Unknown wind function method: {method}. "
                f"Valid options: Brady-Graves-Geyer, Marciano-Harbeck, "
                f"Ryan-Harleman, East Mesa, Helfrich"
            )

    def run(self, met_data: pd.DataFrame) -> pd.DataFrame:
        """
        Run the model for the provided meteorological data.

        Args:
            met_data: DataFrame containing meteorological inputs with columns:
                - datetime: timestamp
                - air_temperature: air temperature (°C)
                - dewpoint_temperature: dewpoint temperature (°C)
                - wind_speed: wind speed (m/s)
                - cloud_cover: cloud cover fraction (0-1)
                - Optional: water_depth_override, effective_shade_override, etc.

        Returns:
            DataFrame with calculated water temperatures and heat fluxes

        Raises:
            RuntimeError: If numerical instability is detected
        """
        # Validate and clean meteorological data
        validated_data, warnings = InputValidator.validate_meteorological_data(met_data)
        for warning in warnings:
            logger.warning(warning)
        
        # Initialize state
        state = ModelState(
            datetime=validated_data.iloc[0]['datetime'],
            water_temperature=self.config.initial_water_temp,
            sediment_temperature=self.config.initial_sediment_temp,
            water_depth=self.config.water_depth,
            effective_shade=self.config.effective_shade,
        )
        
        # Clear previous results
        self.results = []
        self.diagnostics = []
        
        # Main execution loop
        previous_datetime = None
        for idx, row in validated_data.iterrows():
            current_datetime = row['datetime']
            
            # Check timestep
            if previous_datetime is not None:
                warning, timestep_days = InputValidator.check_timestep(current_datetime, previous_datetime)
                if warning:
                    logger.warning(warning)
                    
                    # Calculate timestep in hours
                    timestep_hours = (current_datetime - previous_datetime).total_seconds() / 3600.0
                    
                    # Reset temperatures if timestep is too large
                    if timestep_hours > LARGE_TIMESTEP_RESET_HOURS:
                        midpoint_temp = (row['air_temperature'] + row['dewpoint_temperature']) / 2.0
                        state.water_temperature = midpoint_temp
                        state.sediment_temperature = midpoint_temp
                        logger.warning(
                            f"Large timestep detected ({timestep_hours:.2f} hours). "
                            f"Resetting temperatures to {midpoint_temp:.2f}°C"
                        )
                    
                    # Skip update if timestep is zero (duplicate data)
                    if timestep_hours == 0:
                        logger.warning("Zero timestep detected (duplicate data). Skipping update.")
                        previous_datetime = current_datetime
                        continue
            
            # Calculate timestep
            new_state = self._calculate_timestep(row, state, previous_datetime)
            
            # Check stability
            if previous_datetime is not None:
                self._check_stability(new_state.water_temperature, state.water_temperature)
            
            # Update state
            state = new_state
            previous_datetime = current_datetime
        
        # Convert results to DataFrame
        results_df = pd.DataFrame(self.results)
        
        if self.config.enable_diagnostics and self.diagnostics:
            diagnostics_df = pd.DataFrame(self.diagnostics)
            results_df = pd.concat([results_df, diagnostics_df], axis=1)
        
        return results_df

    def _calculate_timestep(
        self, 
        met_row: pd.Series, 
        previous_state: ModelState,
        previous_datetime: Optional[datetime]
    ) -> ModelState:
        """
        Calculate one timestep of the model.

        Args:
            met_row: Meteorological data for current timestep
            previous_state: State from previous timestep
            previous_datetime: Datetime of previous timestep (None for first timestep)

        Returns:
            New ModelState after timestep calculation
        """
        current_datetime = met_row['datetime']
        
        # Update time-varying parameters if provided
        water_depth = met_row.get('water_depth_override', self.config.water_depth)
        effective_shade = met_row.get('effective_shade_override', self.config.effective_shade)
        
        # Extract meteorological data
        air_temp = met_row['air_temperature']
        dewpoint = met_row['dewpoint_temperature']
        wind_speed = met_row['wind_speed']
        cloud_cover = met_row['cloud_cover']
        
        # Calculate solar position
        azimuth, elevation, earth_sun_distance = NOAASolarPosition.calc_solar_position(
            self.config.latitude,
            self.config.longitude,
            current_datetime,
            self.config.timezone,
            self.config.daylight_savings
        )
        
        # Calculate solar radiation
        solar_radiation = self._calculate_solar_radiation(
            elevation, earth_sun_distance, air_temp, dewpoint, 
            cloud_cover, effective_shade, met_row
        )
        
        # Calculate atmospheric properties
        vapor_pressure_air = AtmosphericHelpers.saturation_vapor_pressure(dewpoint)
        vapor_pressure_water = AtmosphericHelpers.saturation_vapor_pressure(
            previous_state.water_temperature
        )
        
        # Calculate longwave radiation
        emissivity = self.emissivity_calculator.calculate(
            air_temp, vapor_pressure_air
        )
        longwave_atm = LongwaveRadiation.calculate_atmospheric(
            emissivity, air_temp, cloud_cover,
            self.config.longwave_cloud_method,
            self.config.longwave_cloud_kcl3,
            self.config.longwave_cloud_kcl4
        )
        longwave_back = LongwaveRadiation.calculate_back_radiation(
            previous_state.water_temperature
        )
        
        # Adjust wind speed for height
        wind_2m = WindAdjustment.adjust_for_height(
            wind_speed, self.config.wind_height, 2.0
        )
        wind_7m = WindAdjustment.adjust_for_height(
            wind_speed, self.config.wind_height, 7.0
        )
        
        # Apply effective wind factor
        wind_2m *= self.config.effective_wind_factor
        wind_7m *= self.config.effective_wind_factor
        
        # Calculate wind function
        wind_func = self.wind_function.calculate(
            wind_2m if hasattr(self.wind_function, 'target_height') and 
                     self.wind_function.target_height == 2.0 else wind_7m,
            air_temp,
            previous_state.water_temperature,
            vapor_pressure_air,
            vapor_pressure_water
        )
        
        # Calculate heat fluxes
        evap = HeatFluxCalculator.calculate_evaporation(
            wind_func, vapor_pressure_water, vapor_pressure_air
        )
        conv = HeatFluxCalculator.calculate_convection(
            wind_func, previous_state.water_temperature, air_temp
        )
        sediment_cond = HeatFluxCalculator.calculate_sediment_conduction(
            previous_state.water_temperature,
            previous_state.sediment_temperature,
            self.config.sediment_thermal_conductivity,
            self.config.sediment_thickness
        )
        hyporheic = HeatFluxCalculator.calculate_hyporheic_exchange(
            previous_state.water_temperature,
            previous_state.sediment_temperature,
            self.config.hyporheic_exchange_rate,
            water_depth
        )
        groundwater = HeatFluxCalculator.calculate_groundwater_flux(
            previous_state.water_temperature,
            self.config.groundwater_temperature,
            self.config.groundwater_inflow,
            water_depth
        )
        
        # Convert longwave from W/m² to cal/(cm²·day) for temperature calculations
        # LongwaveRadiation methods return W/m², but temperature change needs cal/(cm²·day)
        # Note: longwave_back is returned as positive but represents heat loss, so negate it
        longwave_atm_cal = longwave_atm * WATTS_M2_TO_CAL_CM2_DAY
        longwave_back_cal = -longwave_back * WATTS_M2_TO_CAL_CM2_DAY
        
        # Convert fluxes to W/m² for output
        solar_watts = solar_radiation * CAL_CM2_DAY_TO_WATTS_M2
        longwave_atm_watts = longwave_atm  # Already in W/m²
        longwave_back_watts = -longwave_back  # Negate because it's heat loss
        evap_watts = evap * CAL_CM2_DAY_TO_WATTS_M2
        conv_watts = conv * CAL_CM2_DAY_TO_WATTS_M2
        sediment_watts = sediment_cond * CAL_CM2_DAY_TO_WATTS_M2
        hyporheic_watts = hyporheic * CAL_CM2_DAY_TO_WATTS_M2
        groundwater_watts = groundwater * CAL_CM2_DAY_TO_WATTS_M2
        
        # Calculate net flux
        net_flux_watts = (
            solar_watts + longwave_atm_watts + longwave_back_watts +
            evap_watts + conv_watts + sediment_watts + 
            hyporheic_watts + groundwater_watts
        )
        
        # Calculate temperature change rates (°C/day)
        water_depth_cm = water_depth * METERS_TO_CM
        
        # Heat capacity per unit area: C = ρ * Cp * depth
        # where ρ is in g/cm³, Cp in cal/(g·°C), depth in cm
        # Result is in cal/(cm²·°C)
        rho_g_cm3 = WATER_DENSITY / 1000.0  # Convert kg/m³ to g/cm³
        # Convert J/(kg·°C) to cal/(g·°C): divide by 4.184 J/cal and by 1000 g/kg
        cp_cal_g_c = WATER_SPECIFIC_HEAT / (4.184 * 1000.0)
        
        water_heat_capacity = rho_g_cm3 * cp_cal_g_c * water_depth_cm
        sediment_heat_capacity = rho_g_cm3 * cp_cal_g_c * self.config.sediment_thickness
        
        # Temperature change rate = flux / heat_capacity
        # flux in cal/(cm²·day), capacity in cal/(cm²·°C), result in °C/day
        water_temp_change_rate = (
            (solar_radiation + longwave_atm_cal + longwave_back_cal + evap + conv + 
             sediment_cond + hyporheic + groundwater) /
            water_heat_capacity
        )
        
        sediment_temp_change_rate = -sediment_cond / sediment_heat_capacity
        
        # Calculate timestep in days
        if previous_datetime is not None:
            timestep_days = (current_datetime - previous_datetime).total_seconds() / 86400.0
        else:
            timestep_days = 0.0
        
        # Update temperatures
        new_water_temp = previous_state.water_temperature + (
            water_temp_change_rate * timestep_days
        )
        new_sediment_temp = previous_state.sediment_temperature + (
            sediment_temp_change_rate * timestep_days
        )
        
        # Enforce minimum temperature
        new_water_temp = self._enforce_minimum_temperature(new_water_temp)
        new_sediment_temp = self._enforce_minimum_temperature(new_sediment_temp)
        
        # Store results
        result = {
            'datetime': current_datetime,
            'solar_azimuth': azimuth,
            'solar_elevation': elevation,
            'solar_radiation': solar_watts,
            'longwave_atmospheric': longwave_atm_watts,
            'longwave_back': longwave_back_watts,
            'evaporation': evap_watts,
            'convection': conv_watts,
            'sediment_conduction': sediment_watts,
            'hyporheic_exchange': hyporheic_watts,
            'groundwater': groundwater_watts,
            'net_flux': net_flux_watts,
            'water_temperature': new_water_temp,
            'sediment_temperature': new_sediment_temp,
            'air_temperature': air_temp,
            'dewpoint_temperature': dewpoint,
        }
        self.results.append(result)
        
        # Store diagnostics if enabled
        if self.config.enable_diagnostics:
            diagnostic = {
                'vapor_pressure_water': vapor_pressure_water,
                'vapor_pressure_air': vapor_pressure_air,
                'atmospheric_emissivity': emissivity,
                'wind_speed_2m': wind_2m,
                'wind_speed_7m': wind_7m,
                'wind_function': wind_func,
                'water_temp_change_rate': water_temp_change_rate,
                'sediment_temp_change_rate': sediment_temp_change_rate,
            }
            self.diagnostics.append(diagnostic)
        
        # Return new state
        return ModelState(
            datetime=current_datetime,
            water_temperature=new_water_temp,
            sediment_temperature=new_sediment_temp,
            water_depth=water_depth,
            effective_shade=effective_shade,
        )

    def _calculate_solar_radiation(
        self,
        elevation: float,
        earth_sun_distance: float,
        air_temp: float,
        dewpoint: float,
        cloud_cover: float,
        effective_shade: float,
        met_row: pd.Series
    ) -> float:
        """
        Calculate solar radiation using selected method and apply corrections.

        Args:
            elevation: Solar elevation angle (degrees)
            earth_sun_distance: Earth-Sun distance (AU)
            air_temp: Air temperature (°C)
            dewpoint: Dewpoint temperature (°C)
            cloud_cover: Cloud cover fraction (0-1)
            effective_shade: Effective shade fraction (0-1)
            met_row: Meteorological data row for optional parameters

        Returns:
            Solar radiation in cal/cm²/day
        """
        # Return zero if sun is below horizon (Requirement 17.1)
        if elevation <= 0:
            return 0.0
        
        # Check if measured solar radiation is provided
        if 'solar_radiation' in met_row and met_row['solar_radiation'] is not None and not pd.isna(met_row['solar_radiation']):
            # Use measured solar radiation (already in W/m²)
            solar = met_row['solar_radiation']
        else:
            
            zenith = 90.0 - elevation
            
            # Calculate solar radiation based on method
            if self.config.solar_method == "Bras":
                solar = self.solar_calculator.calculate(
                    elevation, earth_sun_distance, self.config.atmospheric_turbidity
                )
            elif self.config.solar_method == "Bird":
                # Get Bird parameters from met_row or use defaults
                pressure_mb = met_row.get('pressure_mb', 
                    AtmosphericHelpers.pressure_from_altitude(self.config.elevation))
                ozone_cm = met_row.get('ozone_cm', 0.35)
                water_vapor_cm = met_row.get('water_vapor_cm', 1.5)
                aod_500nm = met_row.get('aod_500nm', 0.1)
                aod_380nm = met_row.get('aod_380nm', 0.15)
                forward_scatter = met_row.get('forward_scatter', 0.84)
                ground_albedo = met_row.get('ground_albedo', 0.2)
                
                result = self.solar_calculator.calculate(
                    zenith, earth_sun_distance, pressure_mb, ozone_cm,
                    water_vapor_cm, aod_500nm, aod_380nm, forward_scatter, ground_albedo
                )
                solar = result['global_hz']
            elif self.config.solar_method == "Ryan-Stolzenbach":
                solar = self.solar_calculator.calculate(
                    elevation, earth_sun_distance,
                    self.config.atmospheric_transmission_coeff,
                    self.config.elevation
                )
            elif self.config.solar_method == "Iqbal":
                # Get Iqbal parameters from met_row or use defaults
                pressure_mb = met_row.get('pressure_mb', 
                    AtmosphericHelpers.pressure_from_altitude(self.config.elevation))
                ozone_cm = met_row.get('ozone_cm', 0.35)
                temperature_k = air_temp + CELSIUS_TO_KELVIN
                # Calculate relative humidity from dewpoint
                rh = AtmosphericHelpers.relative_humidity_from_dewpoint(air_temp, dewpoint)
                visibility_km = met_row.get('visibility_km', 23.0)
                ground_albedo = met_row.get('ground_albedo', 0.2)
                
                result = self.solar_calculator.calculate(
                    zenith, earth_sun_distance, pressure_mb, ozone_cm,
                    temperature_k, rh, visibility_km, ground_albedo,
                    self.config.elevation
                )
                solar = result['global_hz']
            else:
                solar = 0.0
        
        # Convert to cal/cm²/day
        solar_cal = solar * WATTS_M2_TO_CAL_CM2_DAY
        
        # Apply corrections
        # Apply cloud correction (for both measured and calculated data)
        solar_cal = SolarRadiationCorrections.apply_cloud_correction(
            solar_cal, cloud_cover,
            self.config.solar_cloud_kcl1,
            self.config.solar_cloud_kcl2
        )
        
        # Apply shade correction
        solar_cal = SolarRadiationCorrections.apply_shade_correction(solar_cal, effective_shade)
        
        # Apply albedo correction
        albedo = SolarRadiationCorrections.calculate_anderson_albedo(cloud_cover, elevation)
        solar_cal = SolarRadiationCorrections.apply_albedo_correction(solar_cal, albedo)
        
        return solar_cal

    def _check_stability(self, new_temp: float, old_temp: float) -> None:
        """
        Check for numerical stability.

        Args:
            new_temp: New temperature (°C)
            old_temp: Previous temperature (°C)

        Raises:
            RuntimeError: If temperature change exceeds stability criteria
        """
        temp_change = abs(new_temp - old_temp)
        if temp_change > self.config.stability_criteria:
            raise RuntimeError(
                f"Numerical instability detected: temperature change of "
                f"{temp_change:.2f}°C exceeds stability criteria of "
                f"{self.config.stability_criteria:.2f}°C. "
                f"Consider using smaller timestep or resampling meteorological data."
            )

    def _enforce_minimum_temperature(self, temperature: float) -> float:
        """
        Enforce minimum temperature constraint.

        Args:
            temperature: Calculated temperature (°C)

        Returns:
            Temperature constrained to minimum value
        """
        return max(temperature, self.config.minimum_temperature)

    def export_results(self, output_path: str, include_diagnostics: bool = False) -> None:
        """
        Export model results to file.

        Args:
            output_path: Path to output CSV file
            include_diagnostics: Whether to include diagnostic information

        Raises:
            ValueError: If no results are available to export
        """
        if not self.results:
            raise ValueError("No results available to export. Run the model first.")
        
        results_df = pd.DataFrame(self.results)
        
        if include_diagnostics and self.diagnostics:
            diagnostics_df = pd.DataFrame(self.diagnostics)
            results_df = pd.concat([results_df, diagnostics_df], axis=1)
        
        results_df.to_csv(output_path, index=False)
        logger.info(f"Results exported to {output_path}")
