"""
Ryan-Stolzenbach solar radiation model implementation.

This module implements the Ryan-Stolzenbach atmospheric attenuation model
for calculating clear-sky solar radiation. This model uses an atmospheric
transmission coefficient adjusted for site elevation and relative air mass.

Reference:
    Ryan, P.J., and K.D. Stolzenbach (1972). Engineering Aspects of Heat
    Disposal from Power Generation. MIT Press.
"""

import math
from typing import Optional

from rtemp.constants import SOLAR_CONSTANT, DEG_TO_RAD


class SolarRadiationRyanStolz:
    """
    Ryan-Stolzenbach solar radiation model.
    
    Implements the Ryan-Stolzenbach atmospheric attenuation model for
    calculating clear-sky solar radiation. This model applies an atmospheric
    transmission coefficient adjusted for site elevation and computes relative
    air mass corrected for elevation.
    
    Reference:
        Ryan, P.J., and K.D. Stolzenbach (1972). Engineering Aspects of Heat
        Disposal from Power Generation. MIT Press.
    """
    
    @staticmethod
    def calculate(
        elevation: float,
        earth_sun_distance: float,
        atmospheric_transmission_coeff: float = 0.8,
        site_elevation_m: float = 0.0
    ) -> float:
        """
        Calculate clear-sky solar radiation using Ryan-Stolzenbach method.
        
        Args:
            elevation: Solar elevation angle in degrees above horizon
            earth_sun_distance: Earth-Sun distance in astronomical units (AU)
            atmospheric_transmission_coeff: Atmospheric transmission coefficient
                                           (typically 0.70-0.91, default 0.8)
            site_elevation_m: Site elevation above sea level in meters (default 0.0)
        
        Returns:
            Clear-sky solar radiation in W/m²
            
        Note:
            Returns 0.0 if solar elevation is zero or negative (nighttime).
        """
        # If sun is below horizon, no solar radiation (Requirement 17.1)
        if elevation <= 0.0:
            return 0.0
        
        # Convert elevation angle to radians
        elevation_rad = elevation * DEG_TO_RAD
        sin_elevation = math.sin(elevation_rad)
        
        # Calculate extraterrestrial radiation corrected for Earth-Sun distance
        # Solar constant adjusted by inverse square of distance
        extraterrestrial_radiation = SOLAR_CONSTANT / (earth_sun_distance ** 2)
        
        # Calculate top-of-atmosphere radiation on horizontal surface
        # This accounts for the angle of incidence
        radiation_toa = extraterrestrial_radiation * sin_elevation
        
        # Calculate relative air mass corrected for site elevation
        # This uses a modified Kasten-Young formula that accounts for
        # atmospheric pressure reduction at altitude
        relative_air_mass = SolarRadiationRyanStolz._calc_relative_air_mass(
            elevation, site_elevation_m
        )
        
        # Apply atmospheric transmission with elevation-corrected air mass
        # Formula: I = I_toa * (at^rm)
        # where at is the atmospheric transmission coefficient
        # and rm is the relative air mass
        clear_sky_radiation = radiation_toa * (
            atmospheric_transmission_coeff ** relative_air_mass
        )
        
        return clear_sky_radiation
    
    @staticmethod
    def _calc_relative_air_mass(
        elevation: float,
        site_elevation_m: float
    ) -> float:
        """
        Calculate relative air mass corrected for site elevation.
        
        This method computes the relative path length of sunlight through
        the atmosphere, accounting for both the solar elevation angle and
        the reduction in atmospheric pressure at altitude.
        
        Args:
            elevation: Solar elevation angle in degrees above horizon
            site_elevation_m: Site elevation above sea level in meters
        
        Returns:
            Relative air mass (dimensionless, >= 0)
            
        Reference:
            Ryan-Stolzenbach method uses a pressure correction based on
            the US Standard Atmosphere and a modified Kasten-Young formula
            for air mass calculation.
        """
        if elevation <= 0.0:
            # Return a large value for below-horizon sun
            return 38.0
        
        # Convert elevation to radians
        elevation_rad = elevation * DEG_TO_RAD
        sin_elevation = math.sin(elevation_rad)
        
        # Calculate pressure ratio using US Standard Atmosphere
        # P/P0 = (T/T0)^5.256 where T/T0 = (288 - 0.0065*z) / 288
        # This accounts for the reduction in atmospheric density with altitude
        temperature_ratio = (288.0 - 0.0065 * site_elevation_m) / 288.0
        pressure_ratio = temperature_ratio ** 5.256
        
        # Calculate air mass using modified Kasten-Young formula
        # AM = (P/P0) / (sin(elevation) + 0.15 * (elevation + 3.885)^-1.253)
        # The pressure ratio scales the air mass to account for reduced
        # atmospheric density at altitude
        air_mass_denominator = (
            sin_elevation + 
            0.15 * ((elevation + 3.885) ** -1.253)
        )
        
        relative_air_mass = pressure_ratio / air_mass_denominator
        
        return relative_air_mass
