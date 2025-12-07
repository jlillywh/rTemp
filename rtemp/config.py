"""
Configuration and data model classes for the rTemp model.

This module contains dataclasses for model configuration, state management,
and input/output data structures.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Literal, Optional


@dataclass
class ModelConfiguration:
    """
    Configuration parameters for the rTemp model.

    Contains all site parameters, initial conditions, method selections,
    and model parameters required for model execution.
    """

    # Site parameters
    latitude: float
    longitude: float
    elevation: float  # meters
    timezone: float  # hours from UTC (positive for west)
    daylight_savings: int = 0  # 0 or 1

    # Initial conditions
    initial_water_temp: float = 20.0  # °C
    initial_sediment_temp: float = 20.0  # °C
    minimum_temperature: float = 0.0  # °C

    # Water body parameters
    water_depth: float = 1.0  # meters
    effective_shade: float = 0.0  # 0-1
    wind_height: float = 2.0  # meters
    effective_wind_factor: float = 1.0  # 0-1

    # Sediment parameters
    sediment_thermal_conductivity: float = 0.0  # W/(m·°C)
    sediment_thermal_diffusivity: float = 0.0  # cm²/s
    sediment_thickness: float = 10.0  # cm
    hyporheic_exchange_rate: float = 0.0  # cm/day

    # Groundwater parameters
    groundwater_temperature: float = 15.0  # °C
    groundwater_inflow: float = 0.0  # cm/day

    # Method selections
    solar_method: str = "Bras"  # 'Bras', 'Bird', 'Ryan-Stolzenbach', 'Iqbal'
    longwave_method: str = "Brunt"  # 'Brunt', 'Brutsaert', 'Satterlund', etc.
    wind_function_method: str = "Brady-Graves-Geyer"

    # Model parameters
    atmospheric_turbidity: float = 2.0  # for Bras (2-5)
    atmospheric_transmission_coeff: float = 0.8  # for Ryan-Stolzenbach (0.7-0.91)
    brutsaert_coefficient: float = 1.24  # for Brutsaert longwave

    # Cloud correction parameters
    solar_cloud_kcl1: float = 1.0  # 0-1
    solar_cloud_kcl2: float = 2.0  # 0-5
    longwave_cloud_method: Literal["Eqn 1", "Eqn 2"] = "Eqn 1"  # 'Eqn 1' or 'Eqn 2'
    longwave_cloud_kcl3: float = 1.0  # 0-1
    longwave_cloud_kcl4: float = 2.0  # 0-5

    # Stability checking
    stability_criteria: float = 5.0  # °C

    # Output options
    enable_diagnostics: bool = False


@dataclass
class ModelState:
    """
    Runtime state of the model at a given timestep.

    Tracks current water and sediment temperatures and time-varying parameters.
    """

    datetime: datetime
    water_temperature: float  # °C
    sediment_temperature: float  # °C
    water_depth: float  # meters (can vary with time)
    effective_shade: float = 0.0  # 0-1 (can vary with time)


@dataclass
class MeteorologicalData:
    """
    Meteorological input data for a single timestep.

    Contains required and optional meteorological parameters.
    """

    datetime: datetime
    air_temperature: float  # °C
    dewpoint_temperature: float  # °C
    wind_speed: float  # m/s
    cloud_cover: float  # 0-1

    # Optional measured solar radiation
    solar_radiation: Optional[float] = None  # W/m²

    # Optional Bird-Hulstrom parameters
    pressure_mb: Optional[float] = None
    ozone_cm: Optional[float] = None
    water_vapor_cm: Optional[float] = None
    aod_500nm: Optional[float] = None
    aod_380nm: Optional[float] = None
    forward_scatter: Optional[float] = None
    ground_albedo: Optional[float] = None

    # Optional Iqbal parameters
    visibility_km: Optional[float] = None

    # Optional time-varying parameters
    water_depth_override: Optional[float] = None  # meters
    effective_shade_override: Optional[float] = None  # 0-1


@dataclass
class HeatFluxComponents:
    """
    Heat flux components for a single timestep.

    All fluxes in W/m².
    """

    solar_radiation: float
    longwave_atmospheric: float
    longwave_back: float
    evaporation: float
    convection: float
    sediment_conduction: float
    hyporheic_exchange: float
    groundwater: float
    net_flux: float


@dataclass
class SolarPositionResult:
    """
    Solar position calculation results.
    """

    azimuth: float  # degrees from north
    elevation: float  # degrees above horizon
    zenith: float  # degrees from vertical
    earth_sun_distance: float  # AU
    sunrise_time: float  # fraction of day
    sunset_time: float  # fraction of day
    photoperiod: float  # hours


@dataclass
class DiagnosticOutput:
    """
    Extended diagnostic output for debugging and analysis.
    """

    # Solar diagnostics
    solar_potential: float  # W/m² before corrections
    solar_after_cloud: float  # W/m² after cloud correction
    solar_after_shade: float  # W/m² after shade correction
    albedo: float  # surface reflection fraction

    # Atmospheric diagnostics
    vapor_pressure_water: float  # mmHg
    vapor_pressure_air: float  # mmHg
    atmospheric_emissivity: float  # 0-1

    # Wind diagnostics
    wind_speed_2m: float  # m/s
    wind_speed_7m: float  # m/s
    wind_function: float  # cal/cm²/day/mmHg

    # Temperature change rates
    water_temp_change_rate: float  # °C/day
    sediment_temp_change_rate: float  # °C/day
