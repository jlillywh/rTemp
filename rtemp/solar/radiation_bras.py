"""
Bras solar radiation model implementation.

This module implements the Bras atmospheric attenuation model for calculating
clear-sky solar radiation based on extraterrestrial radiation, optical air mass,
and atmospheric turbidity.
"""

import math
from typing import Optional

from rtemp.constants import SOLAR_CONSTANT, DEG_TO_RAD


class SolarRadiationBras:
    """
    Bras solar radiation model.
    
    Implements the Bras atmospheric attenuation model for calculating
    clear-sky solar radiation. This model uses extraterrestrial radiation
    corrected for Earth-Sun distance, optical air mass (Kasten-Young formula),
    molecular scattering coefficient, and atmospheric turbidity factor.
    
    Reference:
        Bras, R.L. (1990). Hydrology: An Introduction to Hydrologic Science.
        Addison-Wesley.
    """
    
    @staticmethod
    def calculate(
        elevation: float,
        earth_sun_distance: float,
        turbidity: float = 2.0
    ) -> float:
        """
        Calculate clear-sky solar radiation using Bras method.
        
        Args:
            elevation: Solar elevation angle in degrees above horizon
            earth_sun_distance: Earth-Sun distance in astronomical units (AU)
            turbidity: Atmospheric turbidity factor (typically 2-5, default 2.0)
                      Lower values = clearer atmosphere
        
        Returns:
            Clear-sky solar radiation in W/m²
            
        Note:
            Returns 0.0 if solar elevation is zero or negative (nighttime).
        """
        # If sun is below horizon, no solar radiation (Requirement 17.1)
        if elevation <= 0.0:
            return 0.0
        
        # Convert elevation to radians
        elevation_rad = elevation * DEG_TO_RAD
        
        # Calculate extraterrestrial radiation corrected for Earth-Sun distance
        # Formula: I0 = (Solar_Constant / distance²) * sin(elevation)
        # This matches VBA implementation in rTemp_python.py line 176
        extraterrestrial_radiation = (SOLAR_CONSTANT / (earth_sun_distance ** 2)) * math.sin(elevation_rad)
        
        # Calculate optical air mass using simplified Kasten-Young formula
        # This accounts for the path length of sunlight through the atmosphere
        # Formula matches VBA: m = (sin(el) + 0.15 * (el + 3.885)^-1.253)^-1
        air_mass = SolarRadiationBras._calc_optical_air_mass(elevation)
        
        # Calculate molecular scattering coefficient
        # This represents the fraction of radiation scattered by air molecules
        # Formula: a1 = 0.128 - 0.054 * log10(m)
        # This matches VBA implementation in rTemp_python.py line 182
        scattering_coeff = SolarRadiationBras._calc_molecular_scattering_coeff(air_mass)
        
        # Calculate clear-sky radiation with turbidity factor
        # The turbidity factor accounts for aerosols and water vapor
        # Formula: I = I0 * exp(-turbidity * scattering_coeff * air_mass)
        # This matches VBA implementation in rTemp_python.py line 185
        clear_sky_radiation = extraterrestrial_radiation * math.exp(-turbidity * scattering_coeff * air_mass)
        
        return clear_sky_radiation
    
    @staticmethod
    def _calc_optical_air_mass(elevation: float) -> float:
        """
        Calculate optical air mass using simplified Kasten-Young formula.
        
        The optical air mass represents the relative path length of sunlight
        through the atmosphere compared to the vertical path at zenith.
        
        Args:
            elevation: Solar elevation angle in degrees above horizon
        
        Returns:
            Optical air mass (dimensionless, >= 1.0)
            
        Reference:
            VBA implementation in rTemp_python.py line 179
            Simplified Kasten-Young: m = (sin(el) + 0.15 * (el + 3.885)^-1.253)^-1
        """
        if elevation <= 0.0:
            # Return a large value for below-horizon sun
            return 38.0  # Approximate air mass at horizon
        
        # Simplified Kasten-Young formula matching VBA
        # m = (sin(elevation) + 0.15 * (elevation + 3.885)^-1.253)^-1
        elevation_rad = elevation * DEG_TO_RAD
        air_mass = 1.0 / (
            math.sin(elevation_rad) + 
            0.15 * ((elevation + 3.885) ** -1.253)
        )
        
        return air_mass
    
    @staticmethod
    def _calc_molecular_scattering_coeff(air_mass: float) -> float:
        """
        Calculate molecular scattering coefficient.
        
        This coefficient represents the fraction of solar radiation scattered
        by air molecules (Rayleigh scattering) as a function of air mass.
        
        Args:
            air_mass: Optical air mass (dimensionless)
        
        Returns:
            Molecular scattering coefficient (dimensionless)
            
        Reference:
            VBA implementation in rTemp_python.py line 182
            Formula: a1 = 0.128 - 0.054 * log10(m)
        """
        # Molecular scattering coefficient depends on air mass
        # Formula: a1 = 0.128 - 0.054 * log10(air_mass)
        # This matches VBA implementation
        scattering_coeff = 0.128 - 0.054 * math.log10(air_mass)
        
        return scattering_coeff
