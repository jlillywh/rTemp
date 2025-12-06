"""
Physical and mathematical constants used throughout the rTemp model.

This module contains all physical constants, conversion factors, and
mathematical constants required for heat budget calculations.
"""

import math

# Mathematical constants
PI = math.pi

# Physical constants
STEFAN_BOLTZMANN = 5.67e-8  # Stefan-Boltzmann constant (W/m²/K⁴)
WATER_DENSITY = 1000.0  # Density of water (kg/m³)
WATER_SPECIFIC_HEAT = 4186.0  # Specific heat of water (J/kg/°C)
WATER_EMISSIVITY = 0.97  # Emissivity of water surface
ATMOSPHERIC_REFLECTION = 0.03  # Atmospheric reflection factor for longwave

# Bowen ratio (ratio of sensible to latent heat)
# Note: VBA implementation uses 0.47, which differs from the commonly cited
# value of 0.61. Using 0.47 to match VBA reference implementation.
BOWEN_RATIO = 0.47  # mmHg/°C

# Gas constant for water vapor
GAS_CONSTANT_WATER_VAPOR = 461.5  # J/(kg·K)

# Standard atmospheric conditions
STANDARD_PRESSURE_MB = 1013.25  # Standard atmospheric pressure (mb)
STANDARD_PRESSURE_PA = 101325.0  # Standard atmospheric pressure (Pa)
STANDARD_TEMPERATURE_K = 288.15  # Standard temperature (K) = 15°C

# Earth and solar constants
SOLAR_CONSTANT = 1367.0  # Solar constant (W/m²)
AU = 1.496e11  # Astronomical Unit (meters)
EARTH_RADIUS = 6371000.0  # Earth radius (meters)

# Conversion factors
WATTS_M2_TO_CAL_CM2_DAY = 86400.0 / (4.183076 * 10000.0)
CAL_CM2_DAY_TO_WATTS_M2 = (4.183076 * 10000.0) / 86400.0
DEG_TO_RAD = PI / 180.0
RAD_TO_DEG = 180.0 / PI
CELSIUS_TO_KELVIN = 273.15
METERS_TO_CM = 100.0
CM_TO_METERS = 0.01
M_S_TO_MPH = 3600.0 / 1609.344
MPH_TO_M_S = 1609.344 / 3600.0

# Thermal conductivity conversion: W/(m·°C) to cal/(s·cm·°C)
W_M_C_TO_CAL_S_CM_C = 1.0 / (4.183076 * 100.0)

# Time conversions
SECONDS_PER_DAY = 86400.0
MINUTES_PER_DAY = 1440.0
HOURS_PER_DAY = 24.0
DAYS_PER_HOUR = 1.0 / 24.0

# Magnus formula constants for saturation vapor pressure
MAGNUS_A = 17.27
MAGNUS_B = 237.7  # °C

# Lowe polynomial coefficients for water vapor saturation pressure
# For liquid water (T > 0°C)
LOWE_WATER_COEFFS = [
    6.107799961,
    4.436518521e-1,
    1.428945805e-2,
    2.650648471e-4,
    3.031240396e-6,
    2.034080948e-8,
    6.136820929e-11,
]

# For ice (T < 0°C)
LOWE_ICE_COEFFS = [
    6.109177956,
    5.034698970e-1,
    1.886013408e-2,
    4.176223716e-4,
    5.824720280e-6,
    4.838803174e-8,
    1.838826904e-10,
]

# US Standard Atmosphere constants
US_STD_ATM_LAPSE_RATE = -0.0065  # K/m (temperature lapse rate)
US_STD_ATM_EXPONENT = 5.2559  # Exponent for pressure calculation

# TVA wind adjustment exponent
TVA_WIND_EXPONENT = 0.15

# Default atmospheric parameters
DEFAULT_TURBIDITY = 2.0  # Atmospheric turbidity factor (Bras method)
DEFAULT_TRANSMISSION_COEFF = 0.8  # Atmospheric transmission coefficient
DEFAULT_BRUTSAERT_COEFF = 1.24  # Brutsaert coefficient for longwave

# Default cloud correction parameters
DEFAULT_SOLAR_KCL1 = 1.0  # Solar cloud correction parameter 1
DEFAULT_SOLAR_KCL2 = 2.0  # Solar cloud correction parameter 2
DEFAULT_LONGWAVE_KCL3 = 1.0  # Longwave cloud correction parameter 3
DEFAULT_LONGWAVE_KCL4 = 2.0  # Longwave cloud correction parameter 4

# Bird-Hulstrom default parameters
DEFAULT_OZONE_CM = 0.35  # Ozone layer thickness (cm)
DEFAULT_WATER_VAPOR_CM = 1.5  # Precipitable water (cm)
DEFAULT_AOD_500NM = 0.1  # Aerosol optical depth at 500nm
DEFAULT_AOD_380NM = 0.15  # Aerosol optical depth at 380nm
DEFAULT_FORWARD_SCATTER = 0.84  # Forward scattering fraction
DEFAULT_GROUND_ALBEDO = 0.2  # Ground albedo

# Iqbal default parameters
DEFAULT_VISIBILITY_KM = 23.0  # Visibility (km)

# Numerical stability and validation
DEFAULT_STABILITY_CRITERIA = 5.0  # Maximum temperature change per timestep (°C)
DEFAULT_MINIMUM_TEMPERATURE = 0.0  # Minimum water temperature (°C)
MISSING_DATA_FLAG = -999.0  # Flag for missing meteorological data
LARGE_TIMESTEP_WARNING_HOURS = 2.0  # Warn if timestep exceeds this
LARGE_TIMESTEP_RESET_HOURS = 4.0  # Reset temperatures if timestep exceeds this

# Default replacement values for missing data
DEFAULT_AIR_TEMP = 20.0  # °C
DEFAULT_DEWPOINT = 10.0  # °C
DEFAULT_WIND_SPEED = 0.0  # m/s
DEFAULT_CLOUD_COVER = 0.0  # fraction

# Sediment default parameters
DEFAULT_SEDIMENT_THICKNESS = 10.0  # cm
DEFAULT_SEDIMENT_CONDUCTIVITY = 0.0  # W/(m·°C) - will use water properties
DEFAULT_SEDIMENT_DIFFUSIVITY = 0.0  # cm²/s - will use water properties

# Latitude clamping for sunrise/sunset calculations
MAX_LATITUDE = 89.8  # degrees
MIN_LATITUDE = -89.8  # degrees

# Solar radiation thresholds
MIN_SOLAR_ELEVATION = 0.0  # degrees - below this, solar radiation is zero
MAX_ZENITH_FOR_TRANSMISSION = 89.0  # degrees - above this, transmittance is zero

# Atmospheric refraction correction
REFRACTION_CORRECTION = 0.0  # degrees (can be adjusted if needed)

# J2000 epoch for solar calculations
J2000_EPOCH = 2451545.0  # Julian Day for January 1, 2000, 12:00 UT
