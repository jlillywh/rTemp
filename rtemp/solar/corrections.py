"""
Solar radiation corrections module.

This module implements corrections to solar radiation calculations including:
- Anderson albedo calculation (cloud-dependent surface reflection)
- Cloud cover correction (reduces radiation based on cloud fraction)
- Shade correction (reduces radiation based on effective shade)
- Albedo/reflection correction (reduces radiation by surface reflection)

These corrections are applied after the base solar radiation is calculated
by one of the solar radiation models (Bras, Bird, Ryan-Stolzenbach, Iqbal).
"""

import math
from typing import Optional


class SolarRadiationCorrections:
    """
    Solar radiation corrections.
    
    This class provides static methods for applying various corrections
    to calculated solar radiation values. These corrections account for
    cloud cover, shade, and surface reflection (albedo).
    """
    
    @staticmethod
    def apply_cloud_correction(
        solar_radiation: float,
        cloud_cover: float,
        kcl1: float = 1.0,
        kcl2: float = 2.0
    ) -> float:
        """
        Apply cloud cover correction to solar radiation.
        
        This correction reduces solar radiation based on cloud cover fraction
        using an empirical formula with user-specified parameters.
        
        Formula: I_corrected = I * (1 - KCL1 * cloud_cover^KCL2)
        
        Args:
            solar_radiation: Clear-sky solar radiation in W/m²
            cloud_cover: Cloud cover fraction (0-1)
                        0 = clear sky, 1 = completely overcast
            kcl1: Cloud correction parameter 1 (typically 0-1, default 1.0)
                 Controls the magnitude of cloud effect
            kcl2: Cloud correction parameter 2 (typically 0-5, default 2.0)
                 Controls the shape of cloud effect curve
        
        Returns:
            Cloud-corrected solar radiation in W/m²
            
        Note:
            - Cloud cover should be clamped to [0, 1] before calling
            - Result is guaranteed to be non-negative
            - Higher cloud cover reduces radiation more
            
        Validates: Requirements 3.17
        """
        # Ensure cloud cover is in valid range
        cloud_cover = max(0.0, min(1.0, cloud_cover))
        
        # Apply cloud correction formula
        # The formula reduces radiation as cloud cover increases
        # KCL2 exponent creates non-linear relationship
        correction_factor = 1.0 - kcl1 * (cloud_cover ** kcl2)
        
        # Ensure correction factor is non-negative
        correction_factor = max(0.0, correction_factor)
        
        # Apply correction
        corrected_radiation = solar_radiation * correction_factor
        
        return max(0.0, corrected_radiation)
    
    @staticmethod
    def apply_shade_correction(
        solar_radiation: float,
        effective_shade: float
    ) -> float:
        """
        Apply shade correction to solar radiation.
        
        This correction reduces solar radiation based on the effective shade
        fraction, which represents the portion of the water surface that is
        shaded by vegetation, structures, or topography.
        
        Formula: I_corrected = I * (1 - effective_shade)
        
        Args:
            solar_radiation: Solar radiation before shade correction in W/m²
            effective_shade: Effective shade fraction (0-1)
                           0 = no shade, 1 = completely shaded
        
        Returns:
            Shade-corrected solar radiation in W/m²
            
        Note:
            - Effective shade should be clamped to [0, 1] before calling
            - Result is guaranteed to be non-negative
            - Higher shade reduces radiation linearly
            
        Validates: Requirements 3.18
        """
        # Ensure effective shade is in valid range
        effective_shade = max(0.0, min(1.0, effective_shade))
        
        # Apply shade correction
        # Simple linear reduction based on shade fraction
        corrected_radiation = solar_radiation * (1.0 - effective_shade)
        
        return max(0.0, corrected_radiation)
    
    @staticmethod
    def calculate_anderson_albedo(
        cloud_cover: float,
        solar_elevation: float
    ) -> float:
        """
        Calculate surface albedo using Anderson method.
        
        The Anderson method calculates water surface albedo (reflection fraction)
        as a function of solar elevation angle and cloud cover. Albedo increases
        at low solar elevations (sun near horizon) and is affected by cloud cover.
        
        This is an empirical relationship based on observations of water surface
        reflection characteristics.
        
        Args:
            cloud_cover: Cloud cover fraction (0-1)
            solar_elevation: Solar elevation angle in degrees above horizon
        
        Returns:
            Surface albedo fraction (0-1)
            
        Note:
            - Albedo is higher when sun is low on horizon
            - Cloud cover affects albedo calculation
            - Result is clamped to [0, 1]
            
        Reference:
            Anderson, E.R. (1954). Energy Budget Studies, Water Loss
            Investigations: Lake Hefner Studies. U.S. Geological Survey
            Professional Paper 269.
            
        Validates: Requirements 3.19
        """
        # Ensure inputs are in valid ranges
        cloud_cover = max(0.0, min(1.0, cloud_cover))
        solar_elevation = max(0.0, solar_elevation)
        
        # If sun is below horizon, albedo is not meaningful
        # Return a default value
        if solar_elevation <= 0.0:
            return 0.0
        
        # Anderson method for water surface albedo
        # The formula accounts for:
        # 1. Solar elevation angle (lower elevation = higher albedo)
        # 2. Cloud cover (affects the albedo calculation)
        
        # Calculate base albedo from solar elevation
        # Albedo increases as elevation decreases (sun near horizon)
        # Using empirical relationship from Anderson (1954)
        
        # For clear sky conditions
        # Albedo varies from ~0.03 at high sun to ~0.4 at low sun
        if solar_elevation >= 30.0:
            # High sun: low albedo
            albedo_clear = 0.03
        else:
            # Low sun: albedo increases
            # Empirical formula: albedo increases as 1/sin(elevation)
            elevation_rad = solar_elevation * (math.pi / 180.0)
            sin_elevation = math.sin(elevation_rad)
            
            # Prevent division by very small numbers
            if sin_elevation < 0.01:
                sin_elevation = 0.01
            
            # Calculate albedo with empirical coefficients
            # This gives albedo ranging from ~0.03 to ~0.4
            albedo_clear = 0.03 + 0.37 * (1.0 - sin_elevation) ** 2
        
        # Adjust for cloud cover
        # Clouds tend to reduce the variation in albedo
        # Under overcast conditions, albedo is more uniform (~0.05-0.08)
        albedo_overcast = 0.06
        
        # Blend clear-sky and overcast albedo based on cloud cover
        albedo = albedo_clear * (1.0 - cloud_cover) + albedo_overcast * cloud_cover
        
        # Ensure albedo is in valid range
        albedo = max(0.0, min(1.0, albedo))
        
        return albedo
    
    @staticmethod
    def apply_albedo_correction(
        solar_radiation: float,
        albedo: float
    ) -> float:
        """
        Apply albedo (surface reflection) correction to solar radiation.
        
        This correction reduces solar radiation by the fraction that is
        reflected from the water surface. The reflected radiation does not
        contribute to heating the water.
        
        Formula: I_absorbed = I * (1 - albedo)
        
        Args:
            solar_radiation: Solar radiation before albedo correction in W/m²
            albedo: Surface albedo fraction (0-1)
                   Typically calculated using calculate_anderson_albedo()
        
        Returns:
            Absorbed solar radiation in W/m² (after reflection)
            
        Note:
            - Albedo should be in range [0, 1]
            - Result is guaranteed to be non-negative
            - Higher albedo means more reflection, less absorption
            
        Validates: Requirements 3.19
        """
        # Ensure albedo is in valid range
        albedo = max(0.0, min(1.0, albedo))
        
        # Apply albedo correction
        # Subtract the reflected portion
        absorbed_radiation = solar_radiation * (1.0 - albedo)
        
        return max(0.0, absorbed_radiation)
    
    @staticmethod
    def apply_all_corrections(
        solar_radiation: float,
        cloud_cover: float,
        effective_shade: float,
        solar_elevation: float,
        kcl1: float = 1.0,
        kcl2: float = 2.0,
        use_anderson_albedo: bool = True
    ) -> dict:
        """
        Apply all solar radiation corrections in sequence.
        
        This convenience method applies corrections in the proper order:
        1. Cloud cover correction
        2. Shade correction
        3. Albedo correction (using Anderson method)
        
        Args:
            solar_radiation: Clear-sky solar radiation in W/m²
            cloud_cover: Cloud cover fraction (0-1)
            effective_shade: Effective shade fraction (0-1)
            solar_elevation: Solar elevation angle in degrees
            kcl1: Cloud correction parameter 1 (default 1.0)
            kcl2: Cloud correction parameter 2 (default 2.0)
            use_anderson_albedo: Whether to apply Anderson albedo correction
                                (default True)
        
        Returns:
            Dictionary containing:
                - 'final': Final corrected radiation (W/m²)
                - 'after_cloud': Radiation after cloud correction (W/m²)
                - 'after_shade': Radiation after shade correction (W/m²)
                - 'albedo': Calculated albedo fraction
                - 'original': Original radiation (W/m²)
        """
        result = {
            'original': solar_radiation,
            'after_cloud': 0.0,
            'after_shade': 0.0,
            'albedo': 0.0,
            'final': 0.0
        }
        
        # Apply cloud correction
        after_cloud = SolarRadiationCorrections.apply_cloud_correction(
            solar_radiation, cloud_cover, kcl1, kcl2
        )
        result['after_cloud'] = after_cloud
        
        # Apply shade correction
        after_shade = SolarRadiationCorrections.apply_shade_correction(
            after_cloud, effective_shade
        )
        result['after_shade'] = after_shade
        
        # Apply albedo correction if requested
        if use_anderson_albedo:
            albedo = SolarRadiationCorrections.calculate_anderson_albedo(
                cloud_cover, solar_elevation
            )
            result['albedo'] = albedo
            
            final = SolarRadiationCorrections.apply_albedo_correction(
                after_shade, albedo
            )
            result['final'] = final
        else:
            result['albedo'] = 0.0
            result['final'] = after_shade
        
        return result
