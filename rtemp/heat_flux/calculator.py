"""
Heat flux calculation module for the rTemp model.

This module implements the HeatFluxCalculator class which computes all
heat flux components in the water temperature model including:
- Evaporation
- Convection
- Sediment conduction
- Hyporheic exchange
- Groundwater flux
- Longwave back radiation

All calculations follow the requirements specified in Requirements 6.1-6.7.
"""

from rtemp.constants import (
    BOWEN_RATIO,
    STEFAN_BOLTZMANN,
    WATER_EMISSIVITY,
    WATER_DENSITY,
    WATER_SPECIFIC_HEAT,
    CELSIUS_TO_KELVIN,
    SECONDS_PER_DAY,
    METERS_TO_CM,
    W_M_C_TO_CAL_S_CM_C,
)
from rtemp.utils.conversions import UnitConversions


class HeatFluxCalculator:
    """
    Calculator for all heat flux components in the water temperature model.
    
    This class provides static methods for calculating individual heat flux
    components. All fluxes are calculated in cal/(cm²·day) internally and
    can be converted to W/m² for output.
    
    Sign convention:
    - Positive flux = heat gain by water (warming)
    - Negative flux = heat loss from water (cooling)
    """
    
    @staticmethod
    def calculate_evaporation(
        wind_function: float,
        vapor_pressure_water: float,
        vapor_pressure_air: float
    ) -> float:
        """
        Calculate evaporation heat flux.
        
        Evaporation is the heat loss due to water evaporating from the surface.
        The latent heat of vaporization is carried away with the evaporated water.
        
        This method implements Requirement 6.1: WHEN the system calculates 
        evaporation flux THEN the system SHALL compute as negative product of 
        wind function and vapor pressure difference.
        
        Parameters
        ----------
        wind_function : float
            Wind function value in cal/(cm²·day·mmHg)
        vapor_pressure_water : float
            Saturation vapor pressure at water temperature (mmHg)
        vapor_pressure_air : float
            Actual vapor pressure of air (mmHg)
            
        Returns
        -------
        float
            Evaporation flux in cal/(cm²·day)
            Negative value indicates heat loss (cooling)
            
        Notes
        -----
        Formula: evap = -f(W) * (e_water - e_air)
        
        When e_water > e_air (typical), evaporation occurs and flux is negative.
        When e_water < e_air (rare), condensation occurs and flux is positive.
        """
        # Calculate vapor pressure difference
        vapor_pressure_diff = vapor_pressure_water - vapor_pressure_air
        
        # Calculate evaporation flux (negative for heat loss)
        evaporation_flux = -wind_function * vapor_pressure_diff
        
        return evaporation_flux
    
    @staticmethod
    def calculate_convection(
        wind_function: float,
        water_temp: float,
        air_temp: float,
        bowen_ratio: float = BOWEN_RATIO
    ) -> float:
        """
        Calculate convection (sensible heat) flux.
        
        Convection is the heat exchange between water and air due to temperature
        difference. The Bowen ratio relates sensible heat flux to latent heat flux.
        
        This method implements Requirement 6.2: WHEN the system calculates 
        convection flux THEN the system SHALL compute as negative product of 
        Bowen ratio, wind function, and temperature difference.
        
        Parameters
        ----------
        wind_function : float
            Wind function value in cal/(cm²·day·mmHg)
        water_temp : float
            Water surface temperature (°C)
        air_temp : float
            Air temperature (°C)
        bowen_ratio : float, optional
            Bowen ratio (mmHg/°C), default is 0.61
            
        Returns
        -------
        float
            Convection flux in cal/(cm²·day)
            Negative value indicates heat loss (cooling)
            
        Notes
        -----
        Formula: conv = -Bowen * f(W) * (T_water - T_air)
        
        When T_water > T_air (typical), convection cools the water (negative flux).
        When T_water < T_air (rare), convection warms the water (positive flux).
        """
        # Calculate temperature difference
        temp_diff = water_temp - air_temp
        
        # Calculate convection flux (negative for heat loss)
        convection_flux = -bowen_ratio * wind_function * temp_diff
        
        return convection_flux
    
    @staticmethod
    def calculate_longwave_back(water_temp: float) -> float:
        """
        Calculate longwave back radiation from water surface.
        
        The water surface emits thermal radiation according to the Stefan-Boltzmann
        law. This is always a heat loss (negative flux).
        
        This method implements Requirement 6.3: WHEN the system calculates 
        longwave back radiation THEN the system SHALL compute as negative 
        Stefan-Boltzmann emission from water surface.
        
        Parameters
        ----------
        water_temp : float
            Water surface temperature (°C)
            
        Returns
        -------
        float
            Longwave back radiation in cal/(cm²·day)
            Always negative (heat loss)
            
        Notes
        -----
        Formula: back = -ε * σ * T⁴
        where:
        - ε = water emissivity (0.97)
        - σ = Stefan-Boltzmann constant (5.67e-8 W/(m²·K⁴))
        - T = water temperature in Kelvin
        
        Result is converted from W/m² to cal/(cm²·day)
        """
        # Convert temperature to Kelvin
        water_temp_k = water_temp + CELSIUS_TO_KELVIN
        
        # Calculate Stefan-Boltzmann emission in W/m²
        back_radiation_w_m2 = WATER_EMISSIVITY * STEFAN_BOLTZMANN * (water_temp_k ** 4)
        
        # Convert to cal/(cm²·day)
        back_radiation = UnitConversions.watts_m2_to_cal_cm2_day(back_radiation_w_m2)
        
        # Return as negative (heat loss)
        return -back_radiation
    
    @staticmethod
    def calculate_sediment_conduction(
        water_temp: float,
        sediment_temp: float,
        thermal_conductivity: float,
        sediment_thickness: float
    ) -> float:
        """
        Calculate heat flux due to conduction between water and sediment.
        
        Heat is conducted between water and sediment based on their temperature
        difference, the thermal conductivity of the sediment, and the thickness
        of the sediment layer.
        
        This method implements Requirement 6.4: WHEN the system calculates 
        sediment conduction THEN the system SHALL compute heat flux based on 
        temperature difference, thermal conductivity, and sediment thickness.
        
        Parameters
        ----------
        water_temp : float
            Water temperature (°C)
        sediment_temp : float
            Sediment temperature (°C)
        thermal_conductivity : float
            Sediment thermal conductivity in W/(m·°C)
        sediment_thickness : float
            Sediment layer thickness (cm)
            
        Returns
        -------
        float
            Sediment conduction flux in cal/(cm²·day)
            Positive when sediment is warmer than water (heat gain)
            Negative when water is warmer than sediment (heat loss)
            
        Notes
        -----
        Formula: Jsedcond = k * (T_sediment - T_water) / thickness
        where:
        - k = thermal conductivity in cal/(s·cm·°C)
        - thickness = sediment thickness in cm
        
        Result is multiplied by seconds per day to get cal/(cm²·day)
        """
        # Convert thermal conductivity from W/(m·°C) to cal/(s·cm·°C)
        k_cal = thermal_conductivity * W_M_C_TO_CAL_S_CM_C
        
        # Calculate temperature difference (sediment - water)
        temp_diff = sediment_temp - water_temp
        
        # Calculate conduction flux in cal/(cm²·s)
        flux_per_second = k_cal * temp_diff / sediment_thickness
        
        # Convert to cal/(cm²·day)
        sediment_flux = flux_per_second * SECONDS_PER_DAY
        
        return sediment_flux
    
    @staticmethod
    def calculate_hyporheic_exchange(
        water_temp: float,
        sediment_temp: float,
        exchange_rate: float,
        water_depth: float
    ) -> float:
        """
        Calculate heat flux due to hyporheic exchange.
        
        Hyporheic exchange is the movement of water between the stream and
        the sediment pore spaces. This exchanges heat based on the temperature
        difference and the exchange rate.
        
        This method implements Requirement 6.5: WHEN the system calculates 
        hyporheic exchange THEN the system SHALL compute heat flux based on 
        temperature difference, water properties, and exchange rate.
        
        Parameters
        ----------
        water_temp : float
            Water temperature (°C)
        sediment_temp : float
            Sediment temperature (°C)
        exchange_rate : float
            Hyporheic exchange rate (cm/day)
        water_depth : float
            Water depth (meters)
            
        Returns
        -------
        float
            Hyporheic exchange flux in cal/(cm²·day)
            Positive when sediment is warmer than water (heat gain)
            Negative when water is warmer than sediment (heat loss)
            
        Notes
        -----
        Formula: Jhyp = ρ * Cp * Q * (T_sediment - T_water) / depth
        where:
        - ρ = water density (g/cm³)
        - Cp = specific heat of water (cal/(g·°C))
        - Q = exchange rate (cm/day)
        - depth = water depth (cm)
        """
        # Convert water depth from meters to cm
        depth_cm = water_depth * METERS_TO_CM
        
        # Convert water density from kg/m³ to g/cm³
        density_g_cm3 = WATER_DENSITY / 1000.0
        
        # Convert specific heat from J/(kg·°C) to cal/(g·°C)
        # 1 cal = 4.184 J, so J/(kg·°C) / 4.184 = cal/(g·°C)
        specific_heat_cal = WATER_SPECIFIC_HEAT / 4.184
        
        # Calculate temperature difference (sediment - water)
        temp_diff = sediment_temp - water_temp
        
        # Calculate hyporheic exchange flux
        hyporheic_flux = (
            density_g_cm3 * specific_heat_cal * exchange_rate * temp_diff / depth_cm
        )
        
        return hyporheic_flux
    
    @staticmethod
    def calculate_groundwater_flux(
        water_temp: float,
        groundwater_temp: float,
        inflow_rate: float,
        water_depth: float
    ) -> float:
        """
        Calculate heat flux due to groundwater inflow.
        
        Groundwater entering the water body brings heat based on its temperature
        relative to the water temperature and the inflow rate.
        
        This method implements Requirement 6.6: WHEN the system calculates 
        groundwater flux THEN the system SHALL compute heat flux based on 
        temperature difference, water properties, and groundwater inflow rate.
        
        Parameters
        ----------
        water_temp : float
            Water temperature (°C)
        groundwater_temp : float
            Groundwater temperature (°C)
        inflow_rate : float
            Groundwater inflow rate (cm/day)
        water_depth : float
            Water depth (meters)
            
        Returns
        -------
        float
            Groundwater flux in cal/(cm²·day)
            Positive when groundwater is warmer than water (heat gain)
            Negative when water is warmer than groundwater (heat loss)
            
        Notes
        -----
        Formula: Jgw = ρ * Cp * Q * (T_gw - T_water) / depth
        where:
        - ρ = water density (g/cm³)
        - Cp = specific heat of water (cal/(g·°C))
        - Q = inflow rate (cm/day)
        - depth = water depth (cm)
        """
        # Convert water depth from meters to cm
        depth_cm = water_depth * METERS_TO_CM
        
        # Convert water density from kg/m³ to g/cm³
        density_g_cm3 = WATER_DENSITY / 1000.0
        
        # Convert specific heat from J/(kg·°C) to cal/(g·°C)
        specific_heat_cal = WATER_SPECIFIC_HEAT / 4.184
        
        # Calculate temperature difference (groundwater - water)
        temp_diff = groundwater_temp - water_temp
        
        # Calculate groundwater flux
        groundwater_flux = (
            density_g_cm3 * specific_heat_cal * inflow_rate * temp_diff / depth_cm
        )
        
        return groundwater_flux

