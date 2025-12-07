"""
Iqbal solar radiation model implementation.

This module implements the Iqbal atmospheric transmittance model for calculating
clear-sky solar radiation. This model computes atmospheric transmittances for
Rayleigh scattering, ozone, uniformly mixed gases, water vapor, and aerosols,
then calculates direct and diffuse irradiance components including multiple
scattering between ground and atmosphere.

Reference:
    Iqbal, M. (1983). An Introduction to Solar Radiation. Academic Press.
"""

import math
from typing import Dict

from rtemp.constants import SOLAR_CONSTANT, DEG_TO_RAD


class SolarRadiationIqbal:
    """
    Iqbal solar radiation model.

    Implements the Iqbal atmospheric transmittance model for calculating
    clear-sky solar radiation. This model computes detailed atmospheric
    transmittances for various atmospheric constituents and calculates
    direct beam, diffuse (Rayleigh, aerosol, and multiple scattering),
    and global horizontal irradiance.

    Reference:
        Iqbal, M. (1983). An Introduction to Solar Radiation. Academic Press.
    """

    # Constants from Iqbal (1983)
    SINGLE_SCATTERING_ALBEDO = 0.9  # Single scattering albedo for aerosols
    FORWARD_SCATTER_RATIO = 0.84  # Ratio of forward to total energy scattered
    ALTITUDE_CORRECTION_COEFF = 2.2e-5  # m^-1, Bintanja (1996)
    MAX_ALTITUDE_CORRECTION = 3000.0  # meters

    @staticmethod
    def calculate(
        zenith: float,
        earth_sun_distance: float,
        pressure_mb: float,
        ozone_cm: float,
        temperature_k: float,
        relative_humidity: float,
        visibility_km: float,
        albedo: float,
        site_elevation_m: float = 0.0,
    ) -> Dict[str, float]:
        """
        Calculate solar radiation components using Iqbal method.

        Args:
            zenith: Solar zenith angle in degrees from vertical
            earth_sun_distance: Earth-Sun distance in astronomical units (AU)
            pressure_mb: Atmospheric pressure in millibars
            ozone_cm: Ozone layer thickness in cm-atm
            temperature_k: Air temperature in Kelvin
            relative_humidity: Relative humidity as fraction (0-1)
            visibility_km: Visibility in kilometers
            albedo: Ground albedo (0-1)
            site_elevation_m: Site elevation above sea level in meters (default 0.0)

        Returns:
            Dictionary containing:
                - direct_beam: Direct beam irradiance (W/m²)
                - direct_hz: Direct horizontal irradiance (W/m²)
                - diffuse_hz: Diffuse horizontal irradiance (W/m²)
                - global_hz: Global horizontal irradiance (W/m²)
                - diffuse_rayleigh: Rayleigh-scattered diffuse (W/m²)
                - diffuse_aerosol: Aerosol-scattered diffuse (W/m²)
                - diffuse_multiple: Multiple-scattered diffuse (W/m²)

        Note:
            Returns all zeros if zenith angle >= 89 degrees (near horizon).
        """
        # If sun is near or below horizon, no solar radiation (Requirement 17.2)
        if zenith >= 89.0:
            return {
                "direct_beam": 0.0,
                "direct_hz": 0.0,
                "diffuse_hz": 0.0,
                "global_hz": 0.0,
                "diffuse_rayleigh": 0.0,
                "diffuse_aerosol": 0.0,
                "diffuse_multiple": 0.0,
            }

        # Convert zenith to radians
        zenith_rad = zenith * DEG_TO_RAD
        cos_zenith = math.cos(zenith_rad)

        # Calculate relative optical air mass (Kasten-Young formula)
        elevation = 90.0 - zenith
        mr = SolarRadiationIqbal._calc_relative_air_mass(elevation)

        # Calculate pressure-corrected air mass
        ma = mr * pressure_mb / 1013.25

        # Calculate precipitable water using Prata (1996) formula
        # First get saturated water vapor pressure using Lowe polynomials
        wvap_s = SolarRadiationIqbal._calc_water_vapor_saturation(temperature_k)

        # Precipitable water in cm
        wprec = 46.5 * relative_humidity * wvap_s / temperature_k

        # Calculate Earth-Sun distance correction (Spencer 1971)
        # This is the eccentricity correction factor
        rho2 = earth_sun_distance**-2

        # Calculate atmospheric transmittances

        # 1. Rayleigh scattering transmittance
        tau_r = SolarRadiationIqbal._calc_rayleigh_transmittance(ma)

        # 2. Ozone transmittance
        tau_o = SolarRadiationIqbal._calc_ozone_transmittance(ozone_cm, mr)

        # 3. Uniformly mixed gases transmittance
        tau_g = SolarRadiationIqbal._calc_gas_transmittance(ma)

        # 4. Water vapor transmittance
        tau_w = SolarRadiationIqbal._calc_water_vapor_transmittance(wprec, mr)

        # 5. Aerosol transmittance (using visibility parameterization)
        tau_a = SolarRadiationIqbal._calc_aerosol_transmittance(visibility_km, ma)

        # Apply altitude correction (Bintanja 1996)
        b_z = SolarRadiationIqbal._calc_altitude_correction(site_elevation_m)

        # Total transmittance
        tau_total = tau_r * tau_o * tau_g * tau_w * tau_a + b_z

        # Calculate direct beam irradiance
        direct_beam = 0.9751 * rho2 * SOLAR_CONSTANT * tau_total

        # Calculate direct horizontal irradiance
        direct_hz = direct_beam * cos_zenith

        # Calculate diffuse irradiance components

        # Aerosol after-scattering transmittance
        tau_aa = 1.0 - (1.0 - SolarRadiationIqbal.SINGLE_SCATTERING_ALBEDO) * (
            1.0 - ma + ma**1.06
        ) * (1.0 - tau_a)

        # Rayleigh-scattered diffuse irradiance
        diffuse_rayleigh = (
            0.79
            * rho2
            * SOLAR_CONSTANT
            * cos_zenith
            * tau_o
            * tau_g
            * tau_w
            * tau_aa
            * 0.5
            * (1.0 - tau_r)
            / (1.0 - ma + ma**1.02)
        )

        # Aerosol-scattered diffuse irradiance
        tau_as = tau_a / tau_aa
        diffuse_aerosol = (
            0.79
            * rho2
            * SOLAR_CONSTANT
            * cos_zenith
            * tau_o
            * tau_g
            * tau_w
            * tau_aa
            * SolarRadiationIqbal.FORWARD_SCATTER_RATIO
            * (1.0 - tau_as)
            / (1.0 - ma + ma**1.02)
        )

        # Multiple scattering between ground and atmosphere
        alpha_atmos = 0.0685 + (1.0 - SolarRadiationIqbal.FORWARD_SCATTER_RATIO) * (1.0 - tau_as)

        diffuse_multiple = (
            (direct_hz + diffuse_rayleigh + diffuse_aerosol)
            * albedo
            * alpha_atmos
            / (1.0 - albedo * alpha_atmos)
        )

        # Total diffuse horizontal irradiance
        diffuse_hz = diffuse_rayleigh + diffuse_aerosol + diffuse_multiple

        # Global horizontal irradiance
        global_hz = direct_hz + diffuse_hz

        return {
            "direct_beam": max(0.0, direct_beam),
            "direct_hz": max(0.0, direct_hz),
            "diffuse_hz": max(0.0, diffuse_hz),
            "global_hz": max(0.0, global_hz),
            "diffuse_rayleigh": max(0.0, diffuse_rayleigh),
            "diffuse_aerosol": max(0.0, diffuse_aerosol),
            "diffuse_multiple": max(0.0, diffuse_multiple),
        }

    @staticmethod
    def _calc_relative_air_mass(elevation: float) -> float:
        """
        Calculate relative optical air mass using Kasten-Young formula.

        Args:
            elevation: Solar elevation angle in degrees above horizon

        Returns:
            Relative optical air mass (dimensionless, >= 1.0)
        """
        if elevation <= 0.0:
            return 38.0  # Large value for below-horizon sun

        # Kasten-Young formula
        # mr = 1 / (cos(zenith) + 0.15 * (93.885 - zenith)^-1.253)
        zenith = 90.0 - elevation
        mr: float = 1.0 / (math.cos(zenith * DEG_TO_RAD) + 0.15 * ((93.885 - zenith) ** -1.253))

        return mr

    @staticmethod
    def _calc_water_vapor_saturation(temperature_k: float) -> float:
        """
        Calculate saturated water vapor pressure using Lowe (1977) polynomials.

        Args:
            temperature_k: Temperature in Kelvin

        Returns:
            Saturated water vapor pressure in hPa
        """
        # Convert to Celsius
        temp_c = temperature_k - 273.15

        # Lowe polynomial coefficients for liquid water (T > 0°C)
        # For ice (T < 0°C), different coefficients would be used
        if temp_c >= 0.0:
            # Coefficients for liquid water
            a0 = 6.107799961
            a1 = 4.436518521e-1
            a2 = 1.428945805e-2
            a3 = 2.650648471e-4
            a4 = 3.031240396e-6
            a5 = 2.034080948e-8
            a6 = 6.136820929e-11
        else:
            # Coefficients for ice
            a0 = 6.109177956
            a1 = 5.034698970e-1
            a2 = 1.886013408e-2
            a3 = 4.176223716e-4
            a4 = 5.824720280e-6
            a5 = 4.838803174e-8
            a6 = 1.838826904e-10

        # Calculate using polynomial
        wvap_s: float = a0 + temp_c * (
            a1 + temp_c * (a2 + temp_c * (a3 + temp_c * (a4 + temp_c * (a5 + temp_c * a6))))
        )

        return wvap_s

    @staticmethod
    def _calc_rayleigh_transmittance(ma: float) -> float:
        """
        Calculate Rayleigh scattering transmittance.

        Args:
            ma: Pressure-corrected air mass

        Returns:
            Rayleigh transmittance (0-1)
        """
        # Iqbal formula for Rayleigh transmittance
        tau_r = math.exp(-0.0903 * (ma**0.84) * (1.0 + ma - ma**1.01))

        return tau_r

    @staticmethod
    def _calc_ozone_transmittance(ozone_cm: float, mr: float) -> float:
        """
        Calculate ozone transmittance.

        Args:
            ozone_cm: Ozone layer thickness in cm-atm
            mr: Relative air mass

        Returns:
            Ozone transmittance (0-1)
        """
        # Iqbal formula for ozone transmittance
        ozone_path = ozone_cm * mr

        tau_o: float = 1.0 - (
            0.1611 * ozone_path * (1.0 + 139.48 * ozone_path) ** -0.3035
            - 0.002715 * ozone_path / (1.0 + 0.044 * ozone_path + 0.0003 * ozone_path**2)
        )

        return tau_o

    @staticmethod
    def _calc_gas_transmittance(ma: float) -> float:
        """
        Calculate uniformly mixed gases transmittance.

        Args:
            ma: Pressure-corrected air mass

        Returns:
            Gas transmittance (0-1)
        """
        # Iqbal formula for uniformly mixed gases
        tau_g = math.exp(-0.0127 * (ma**0.26))

        return tau_g

    @staticmethod
    def _calc_water_vapor_transmittance(wprec: float, mr: float) -> float:
        """
        Calculate water vapor transmittance.

        Args:
            wprec: Precipitable water in cm
            mr: Relative air mass

        Returns:
            Water vapor transmittance (0-1)
        """
        # Iqbal formula for water vapor transmittance
        water_path = wprec * mr

        tau_w: float = 1.0 - (
            2.4959 * water_path / ((1.0 + 79.034 * water_path) ** 0.6828 + 6.385 * water_path)
        )

        return tau_w

    @staticmethod
    def _calc_aerosol_transmittance(visibility_km: float, ma: float) -> float:
        """
        Calculate aerosol transmittance using visibility parameterization.

        This uses the Mächler (1983) parameterization model A based on
        visibility, as referenced in Iqbal (1983).

        Args:
            visibility_km: Visibility in kilometers
            ma: Pressure-corrected air mass

        Returns:
            Aerosol transmittance (0-1)
        """
        # Mächler (1983) formula using visibility
        # tau_a = (0.97 - 1.265 * visibility^-0.66)^(ma^0.9)

        # Calculate the base term
        base = 0.97 - 1.265 * (visibility_km**-0.66)

        # Ensure base is positive to avoid complex numbers
        # For very low visibility (< ~1.5 km), the formula can produce negative values
        # In such cases, set transmittance to a very small positive value
        if base <= 0.0:
            tau_a = 0.01  # Very low transmittance for extremely poor visibility
        else:
            tau_a = base ** (ma**0.9)

        # Ensure transmittance is in valid range [0, 1]
        tau_a = max(0.0, min(1.0, tau_a))

        result: float = tau_a
        return result

    @staticmethod
    def _calc_altitude_correction(site_elevation_m: float) -> float:
        """
        Calculate altitude correction factor (Bintanja 1996).

        This correction accounts for the increase in direct radiation
        with altitude due to reduced atmospheric path length.

        Args:
            site_elevation_m: Site elevation above sea level in meters

        Returns:
            Altitude correction factor (dimensionless)
        """
        # Bintanja (1996) altitude correction
        # B_z increases linearly up to 3000m, then constant up to 5-6000m
        b_z_coeff = SolarRadiationIqbal.ALTITUDE_CORRECTION_COEFF

        if site_elevation_m <= SolarRadiationIqbal.MAX_ALTITUDE_CORRECTION:
            b_z = b_z_coeff * site_elevation_m
        else:
            b_z = b_z_coeff * SolarRadiationIqbal.MAX_ALTITUDE_CORRECTION

        return b_z
