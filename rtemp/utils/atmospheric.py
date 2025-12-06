"""
Atmospheric helper functions for vapor pressure, humidity, and pressure calculations.

This module provides utility functions for calculating atmospheric properties
including saturation vapor pressure, dewpoint temperature, relative humidity,
and atmospheric pressure at different altitudes.
"""

import math
from typing import Optional

from rtemp.constants import (
    MAGNUS_A,
    MAGNUS_B,
    LOWE_WATER_COEFFS,
    LOWE_ICE_COEFFS,
    STANDARD_PRESSURE_MB,
    STANDARD_TEMPERATURE_K,
    US_STD_ATM_LAPSE_RATE,
    US_STD_ATM_EXPONENT,
    CELSIUS_TO_KELVIN,
)


class AtmosphericHelpers:
    """
    Helper functions for atmospheric calculations.
    
    This class provides static methods for calculating various atmospheric
    properties including vapor pressure, humidity, and pressure variations
    with altitude.
    """

    @staticmethod
    def saturation_vapor_pressure(temp_c: float) -> float:
        """
        Calculate saturation vapor pressure using the Magnus formula.
        
        The Magnus formula is a simplified approximation of the Clausius-Clapeyron
        equation for calculating saturation vapor pressure over liquid water.
        
        Args:
            temp_c: Temperature in degrees Celsius
            
        Returns:
            Saturation vapor pressure in mmHg
            
        References:
            Magnus formula: es = 6.1094 * exp((17.27 * T) / (T + 237.7))
            where T is temperature in °C and es is in hPa (mb)
            Converted to mmHg by multiplying by 0.750062
        """
        # Calculate saturation vapor pressure in hPa (mb)
        es_hpa = 6.1094 * math.exp((MAGNUS_A * temp_c) / (temp_c + MAGNUS_B))
        
        # Convert from hPa to mmHg (1 hPa = 0.750062 mmHg)
        es_mmhg = es_hpa * 0.750062
        
        return es_mmhg

    @staticmethod
    def dewpoint_from_rh(air_temp: float, relative_humidity: float) -> float:
        """
        Calculate dewpoint temperature from air temperature and relative humidity.
        
        This function inverts the Magnus formula to calculate dewpoint from
        relative humidity.
        
        Args:
            air_temp: Air temperature in degrees Celsius
            relative_humidity: Relative humidity as a fraction (0-1)
            
        Returns:
            Dewpoint temperature in degrees Celsius
            
        References:
            Inverted Magnus formula:
            Td = (b * ln(RH) + (a * T) / (b + T)) / (a - ln(RH) - (a * T) / (b + T))
            where a = 17.27, b = 237.7°C
        """
        # Ensure relative humidity is in valid range
        rh = max(0.0, min(1.0, relative_humidity))
        
        # Handle edge case of zero relative humidity
        if rh <= 0.0:
            return air_temp - 50.0  # Return a very low dewpoint
        
        # Calculate using inverted Magnus formula
        ln_rh = math.log(rh)
        numerator = MAGNUS_B * (ln_rh + (MAGNUS_A * air_temp) / (MAGNUS_B + air_temp))
        denominator = MAGNUS_A - ln_rh - (MAGNUS_A * air_temp) / (MAGNUS_B + air_temp)
        
        dewpoint = numerator / denominator
        
        return dewpoint

    @staticmethod
    def relative_humidity_from_dewpoint(air_temp: float, dewpoint: float) -> float:
        """
        Calculate relative humidity from air temperature and dewpoint temperature.
        
        Relative humidity is the ratio of actual vapor pressure to saturation
        vapor pressure at the air temperature.
        
        Args:
            air_temp: Air temperature in degrees Celsius
            dewpoint: Dewpoint temperature in degrees Celsius
            
        Returns:
            Relative humidity as a fraction (0-1)
        """
        # Calculate saturation vapor pressure at air temperature
        es_air = AtmosphericHelpers.saturation_vapor_pressure(air_temp)
        
        # Calculate actual vapor pressure at dewpoint temperature
        e_actual = AtmosphericHelpers.saturation_vapor_pressure(dewpoint)
        
        # Calculate relative humidity
        rh = e_actual / es_air
        
        # Clamp to valid range [0, 1]
        rh = max(0.0, min(1.0, rh))
        
        return rh

    @staticmethod
    def pressure_from_altitude(altitude_m: float) -> float:
        """
        Calculate atmospheric pressure at a given altitude using the US Standard Atmosphere.
        
        This function uses the barometric formula from the US Standard Atmosphere
        model to calculate pressure as a function of altitude.
        
        Args:
            altitude_m: Altitude above sea level in meters
            
        Returns:
            Atmospheric pressure in millibars (mb)
            
        References:
            US Standard Atmosphere formula:
            P = P0 * (1 + L * h / T0)^(-g * M / (R * L))
            where:
            - P0 = standard pressure at sea level (1013.25 mb)
            - L = temperature lapse rate (-0.0065 K/m)
            - h = altitude (m)
            - T0 = standard temperature at sea level (288.15 K)
            - g = gravitational acceleration (9.80665 m/s²)
            - M = molar mass of air (0.0289644 kg/mol)
            - R = universal gas constant (8.31447 J/(mol·K))
            - The exponent simplifies to approximately 5.2559
        """
        # Calculate pressure using barometric formula
        pressure_mb = STANDARD_PRESSURE_MB * (
            1.0 + (US_STD_ATM_LAPSE_RATE * altitude_m / STANDARD_TEMPERATURE_K)
        ) ** US_STD_ATM_EXPONENT
        
        return pressure_mb

    @staticmethod
    def water_vapor_saturation_lowe(temp_k: float, ice: bool = False) -> float:
        """
        Calculate saturated water vapor pressure using Lowe polynomials.
        
        The Lowe polynomials provide accurate calculations of saturation vapor
        pressure over liquid water or ice using polynomial approximations.
        
        Args:
            temp_k: Temperature in Kelvin
            ice: If True, calculate over ice; if False, calculate over liquid water
            
        Returns:
            Saturated water vapor pressure in hPa (mb)
            
        References:
            Lowe, P.R. (1977). An approximating polynomial for the computation
            of saturation vapor pressure. Journal of Applied Meteorology, 16, 100-103.
            
            Polynomial form: es = a0 + a1*T + a2*T² + a3*T³ + a4*T⁴ + a5*T⁵ + a6*T⁶
            where T is temperature in °C
        """
        # Convert temperature from Kelvin to Celsius
        temp_c = temp_k - CELSIUS_TO_KELVIN
        
        # Select appropriate coefficients
        coeffs = LOWE_ICE_COEFFS if ice else LOWE_WATER_COEFFS
        
        # Calculate using polynomial
        es_hpa = sum(coeff * (temp_c ** i) for i, coeff in enumerate(coeffs))
        
        return es_hpa

    @staticmethod
    def koberg_brunt_coefficient(
        air_temp_c: float, clearness: Optional[float] = None
    ) -> float:
        """
        Calculate Koberg Brunt coefficient using interpolation from Koberg Figure 34.
        
        This function interpolates the Brunt coefficient based on air temperature
        and atmospheric clearness for use in longwave radiation calculations.
        
        Args:
            air_temp_c: Air temperature in degrees Celsius
            clearness: Atmospheric clearness factor (optional)
            
        Returns:
            Koberg Brunt coefficient for longwave radiation calculations
            
        Note:
            This is a simplified implementation. The full Koberg method requires
            interpolation from Figure 34 in Koberg (1964), which shows the
            relationship between air temperature, clearness, and the Brunt coefficient.
        """
        # Simplified implementation - returns a reasonable default
        # Full implementation would require detailed interpolation tables
        # from Koberg Figure 34
        
        # Base coefficient varies with temperature
        # Typical range is 0.5-0.7 for the Brunt coefficient
        base_coeff = 0.55 + 0.001 * air_temp_c
        
        # Adjust for clearness if provided
        if clearness is not None:
            # Higher clearness (clearer skies) reduces the coefficient
            base_coeff *= (1.0 - 0.1 * clearness)
        
        # Clamp to reasonable range
        return max(0.4, min(0.7, base_coeff))
