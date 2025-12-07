"""
Bird-Hulstrom solar radiation model implementation.

This module implements the Bird & Hulstrom clear sky model for calculating
direct beam, direct horizontal, diffuse, and global horizontal irradiance.
This model accounts for atmospheric transmittances due to Rayleigh scattering,
ozone absorption, uniformly mixed gases, water vapor, and aerosols.

Reference:
    Bird, R.E., and R.L. Hulstrom (1981). A Simplified Clear Sky Model for
    Direct and Diffuse Insolation on Horizontal Surfaces. SERI Technical
    Report SERI/TR-642-761.
"""

import math
from typing import Dict

from rtemp.constants import SOLAR_CONSTANT, DEG_TO_RAD


class SolarRadiationBird:
    """
    Bird & Hulstrom clear sky solar radiation model.

    Implements the Bird & Hulstrom simplified clear sky model for calculating
    solar radiation components. This model computes atmospheric transmittances
    for various atmospheric constituents and calculates direct beam, direct
    horizontal, diffuse, and global horizontal irradiance.

    Reference:
        Bird, R.E., and R.L. Hulstrom (1981). A Simplified Clear Sky Model for
        Direct and Diffuse Insolation on Horizontal Surfaces. SERI Technical
        Report SERI/TR-642-761.
    """

    @staticmethod
    def calculate(
        zenith: float,
        earth_sun_distance: float,
        pressure_mb: float,
        ozone_cm: float,
        water_cm: float,
        aod_500nm: float,
        aod_380nm: float,
        forward_scatter: float,
        albedo: float,
    ) -> Dict[str, float]:
        """
        Calculate solar radiation components using Bird-Hulstrom method.

        Args:
            zenith: Solar zenith angle in degrees from vertical
            earth_sun_distance: Earth-Sun distance in astronomical units (AU)
            pressure_mb: Atmospheric pressure in millibars
            ozone_cm: Ozone layer thickness in cm-atm
            water_cm: Precipitable water in cm
            aod_500nm: Aerosol optical depth at 500nm
            aod_380nm: Aerosol optical depth at 380nm
            forward_scatter: Forward scattering fraction (0-1)
            albedo: Ground albedo (0-1)

        Returns:
            Dictionary containing:
                - direct_beam: Direct beam irradiance (W/m²)
                - direct_hz: Direct horizontal irradiance (W/m²)
                - diffuse_hz: Diffuse horizontal irradiance (W/m²)
                - global_hz: Global horizontal irradiance (W/m²)

        Note:
            Returns all zeros if zenith angle >= 89 degrees (near horizon).
        """
        # If sun is near or below horizon, no solar radiation (Requirement 17.2)
        if zenith >= 89.0:
            return {"direct_beam": 0.0, "direct_hz": 0.0, "diffuse_hz": 0.0, "global_hz": 0.0}

        # Calculate extraterrestrial radiation corrected for Earth-Sun distance
        extraterrestrial_radiation = SOLAR_CONSTANT / (earth_sun_distance**2)

        # Convert zenith to radians
        zenith_rad = zenith * DEG_TO_RAD
        cos_zenith = math.cos(zenith_rad)

        # Calculate air mass (relative path length through atmosphere)
        air_mass = SolarRadiationBird._calc_air_mass(zenith)

        # Calculate pressure-corrected air mass
        air_mass_pressure = air_mass * pressure_mb / 1013.25

        # Calculate transmittances for each atmospheric component

        # 1. Rayleigh scattering transmittance
        tr = SolarRadiationBird._calc_rayleigh_transmittance(air_mass_pressure)

        # 2. Ozone transmittance
        to = SolarRadiationBird._calc_ozone_transmittance(ozone_cm, air_mass)

        # 3. Uniformly mixed gases transmittance
        tg = SolarRadiationBird._calc_gas_transmittance(air_mass_pressure)

        # 4. Water vapor transmittance
        tw = SolarRadiationBird._calc_water_vapor_transmittance(water_cm, air_mass)

        # 5. Aerosol transmittance
        ta = SolarRadiationBird._calc_aerosol_transmittance(aod_500nm, aod_380nm, air_mass)

        # Calculate direct beam irradiance
        # This is the radiation that reaches the surface without scattering
        direct_beam = (
            0.9662  # Correction factor for solar constant
            * extraterrestrial_radiation
            * tr
            * to
            * tg
            * tw
            * ta
        )

        # Calculate direct horizontal irradiance
        # This is the direct beam projected onto a horizontal surface
        direct_hz = direct_beam * cos_zenith

        # Calculate diffuse irradiance components

        # Rayleigh-scattered diffuse
        diffuse_rayleigh = (
            0.79
            * extraterrestrial_radiation
            * cos_zenith
            * to
            * tg
            * tw
            * ta
            * (1.0 - tr)
            / (1.0 - air_mass_pressure + air_mass_pressure**1.02)
        )

        # Aerosol-scattered diffuse
        # Forward scattering fraction determines how much aerosol scattering
        # contributes to diffuse radiation
        taa = 1.0 - (1.0 - ta) * (1.0 - air_mass_pressure + air_mass_pressure**1.02)
        diffuse_aerosol = (
            0.79
            * extraterrestrial_radiation
            * cos_zenith
            * to
            * tg
            * tw
            * forward_scatter
            * (1.0 - taa)
            / (1.0 - air_mass_pressure + air_mass_pressure**1.02)
        )

        # Multiple reflection between ground and atmosphere
        # This accounts for radiation reflected from the ground and scattered back down
        diffuse_multiple = (
            (direct_hz + diffuse_rayleigh + diffuse_aerosol)
            * albedo
            * (1.0 - tr)
            / (1.0 - albedo * (1.0 - tr))
        )

        # Total diffuse horizontal irradiance
        diffuse_hz = diffuse_rayleigh + diffuse_aerosol + diffuse_multiple

        # Global horizontal irradiance (total radiation on horizontal surface)
        global_hz = direct_hz + diffuse_hz

        return {
            "direct_beam": max(0.0, direct_beam),
            "direct_hz": max(0.0, direct_hz),
            "diffuse_hz": max(0.0, diffuse_hz),
            "global_hz": max(0.0, global_hz),
        }

    @staticmethod
    def _calc_air_mass(zenith: float) -> float:
        """
        Calculate relative air mass.

        Args:
            zenith: Solar zenith angle in degrees from vertical

        Returns:
            Relative air mass (dimensionless, >= 1.0)
        """
        if zenith >= 89.0:
            return 38.0  # Large value for near-horizon sun

        zenith_rad = zenith * DEG_TO_RAD
        cos_zenith = math.cos(zenith_rad)

        # Simple air mass formula: AM = 1 / cos(zenith)
        # This is accurate enough for the Bird model
        air_mass = 1.0 / cos_zenith

        return air_mass

    @staticmethod
    def _calc_rayleigh_transmittance(air_mass_pressure: float) -> float:
        """
        Calculate Rayleigh scattering transmittance.

        Rayleigh scattering is caused by air molecules and is wavelength-dependent.

        Args:
            air_mass_pressure: Pressure-corrected air mass

        Returns:
            Rayleigh transmittance (0-1)
        """
        # Bird-Hulstrom formula for Rayleigh transmittance
        tr = math.exp(
            -0.0903
            * (air_mass_pressure**0.84)
            * (1.0 + air_mass_pressure - air_mass_pressure**1.01)
        )

        return tr

    @staticmethod
    def _calc_ozone_transmittance(ozone_cm: float, air_mass: float) -> float:
        """
        Calculate ozone transmittance.

        Ozone absorbs UV radiation, particularly in the 0.3-0.35 μm range.

        Args:
            ozone_cm: Ozone layer thickness in cm-atm
            air_mass: Relative air mass

        Returns:
            Ozone transmittance (0-1)
        """
        # Bird-Hulstrom formula for ozone transmittance
        # Uses ozone absorption coefficient
        ozone_path = ozone_cm * air_mass
        to: float = (
            1.0
            - 0.1611 * ozone_path * (1.0 + 139.48 * ozone_path) ** -0.3035
            - 0.002715 * ozone_path / (1.0 + 0.044 * ozone_path + 0.0003 * ozone_path**2)
        )

        return to

    @staticmethod
    def _calc_gas_transmittance(air_mass_pressure: float) -> float:
        """
        Calculate uniformly mixed gases transmittance.

        This accounts for absorption by CO2, O2, and other uniformly mixed gases.

        Args:
            air_mass_pressure: Pressure-corrected air mass

        Returns:
            Gas transmittance (0-1)
        """
        # Bird-Hulstrom formula for uniformly mixed gases
        tg = math.exp(-0.0127 * (air_mass_pressure**0.26))

        return tg

    @staticmethod
    def _calc_water_vapor_transmittance(water_cm: float, air_mass: float) -> float:
        """
        Calculate water vapor transmittance.

        Water vapor absorbs radiation in several bands, particularly in the infrared.

        Args:
            water_cm: Precipitable water in cm
            air_mass: Relative air mass

        Returns:
            Water vapor transmittance (0-1)
        """
        # Bird-Hulstrom formula for water vapor transmittance
        water_path = water_cm * air_mass
        tw: float = 1.0 - 2.4959 * water_path / (
            (1.0 + 79.034 * water_path) ** 0.6828 + 6.385 * water_path
        )

        return tw

    @staticmethod
    def _calc_aerosol_transmittance(aod_500nm: float, aod_380nm: float, air_mass: float) -> float:
        """
        Calculate aerosol transmittance.

        Aerosols (dust, pollution, etc.) scatter and absorb radiation.

        Args:
            aod_500nm: Aerosol optical depth at 500nm
            aod_380nm: Aerosol optical depth at 380nm
            air_mass: Relative air mass

        Returns:
            Aerosol transmittance (0-1)
        """
        # Calculate wavelength exponent (Angstrom exponent)
        # This characterizes the wavelength dependence of aerosol optical depth
        if aod_500nm > 0 and aod_380nm > 0:
            alpha = math.log(aod_380nm / aod_500nm) / math.log(500.0 / 380.0)
        else:
            alpha = 1.3  # Default value

        # Calculate aerosol optical depth at broadband wavelength
        # Using 0.38 μm as reference
        aod_broadband = aod_380nm

        # Bird-Hulstrom formula for aerosol transmittance
        ta: float = math.exp(
            -(aod_broadband**0.873)
            * (1.0 + aod_broadband - aod_broadband**0.7088)
            * air_mass**0.9108
        )

        return ta
