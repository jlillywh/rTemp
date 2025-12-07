"""
Unit tests for solar radiation models.

These tests verify the solar radiation calculation methods produce
reasonable results for known conditions.
"""

import pytest
from rtemp.solar.radiation_bras import SolarRadiationBras
from rtemp.solar.radiation_bird import SolarRadiationBird
from rtemp.solar.radiation_ryan import SolarRadiationRyanStolz
from rtemp.solar.radiation_iqbal import SolarRadiationIqbal


class TestRyanStolzSolarRadiation:
    """Test Ryan-Stolzenbach solar radiation model."""

    def test_ryan_stolz_noon_summer(self):
        """Test Ryan-Stolz model at solar noon in summer."""
        # High sun angle (60 degrees), typical summer conditions
        elevation = 60.0
        earth_sun_distance = 1.0  # Mean distance
        atc = 0.8  # Default atmospheric transmission coefficient
        site_elevation = 0.0  # Sea level

        radiation = SolarRadiationRyanStolz.calculate(
            elevation=elevation,
            earth_sun_distance=earth_sun_distance,
            atmospheric_transmission_coeff=atc,
            site_elevation_m=site_elevation,
        )

        # Should be positive and reasonable (less than solar constant)
        assert 0 < radiation < 1367, f"Expected radiation between 0 and 1367 W/m², got {radiation}"

        # For 60° elevation, should be substantial radiation
        assert radiation > 500, f"Expected substantial radiation at 60° elevation, got {radiation}"

    def test_ryan_stolz_low_sun(self):
        """Test Ryan-Stolz model with low sun angle."""
        # Low sun angle (15 degrees), typical early morning/late afternoon
        elevation = 15.0
        earth_sun_distance = 1.0
        atc = 0.8
        site_elevation = 0.0

        radiation = SolarRadiationRyanStolz.calculate(
            elevation=elevation,
            earth_sun_distance=earth_sun_distance,
            atmospheric_transmission_coeff=atc,
            site_elevation_m=site_elevation,
        )

        # Should be positive but lower than high sun
        assert 0 < radiation < 500, f"Expected lower radiation at 15° elevation, got {radiation}"

    def test_ryan_stolz_below_horizon(self):
        """Test Ryan-Stolz model with sun below horizon."""
        # Negative elevation (nighttime)
        elevation = -10.0
        earth_sun_distance = 1.0
        atc = 0.8
        site_elevation = 0.0

        radiation = SolarRadiationRyanStolz.calculate(
            elevation=elevation,
            earth_sun_distance=earth_sun_distance,
            atmospheric_transmission_coeff=atc,
            site_elevation_m=site_elevation,
        )

        # Should be exactly zero at night
        assert radiation == 0.0, f"Expected zero radiation below horizon, got {radiation}"

    def test_ryan_stolz_at_horizon(self):
        """Test Ryan-Stolz model with sun at horizon."""
        # Zero elevation (sunrise/sunset)
        elevation = 0.0
        earth_sun_distance = 1.0
        atc = 0.8
        site_elevation = 0.0

        radiation = SolarRadiationRyanStolz.calculate(
            elevation=elevation,
            earth_sun_distance=earth_sun_distance,
            atmospheric_transmission_coeff=atc,
            site_elevation_m=site_elevation,
        )

        # Should be exactly zero at horizon
        assert radiation == 0.0, f"Expected zero radiation at horizon, got {radiation}"

    def test_ryan_stolz_high_elevation_site(self):
        """Test Ryan-Stolz model at high elevation site."""
        # High elevation site (2000m) should have higher radiation
        # due to less atmospheric attenuation
        elevation = 45.0
        earth_sun_distance = 1.0
        atc = 0.8

        radiation_sea_level = SolarRadiationRyanStolz.calculate(
            elevation=elevation,
            earth_sun_distance=earth_sun_distance,
            atmospheric_transmission_coeff=atc,
            site_elevation_m=0.0,
        )

        radiation_high_elev = SolarRadiationRyanStolz.calculate(
            elevation=elevation,
            earth_sun_distance=earth_sun_distance,
            atmospheric_transmission_coeff=atc,
            site_elevation_m=2000.0,
        )

        # High elevation should have more radiation (less atmosphere to pass through)
        assert radiation_high_elev > radiation_sea_level, (
            f"Expected higher radiation at elevation (got {radiation_high_elev}) "
            f"than sea level (got {radiation_sea_level})"
        )

    def test_ryan_stolz_clear_vs_hazy(self):
        """Test Ryan-Stolz model with different atmospheric conditions."""
        # Compare clear sky (high atc) vs hazy sky (low atc)
        elevation = 45.0
        earth_sun_distance = 1.0
        site_elevation = 0.0

        radiation_clear = SolarRadiationRyanStolz.calculate(
            elevation=elevation,
            earth_sun_distance=earth_sun_distance,
            atmospheric_transmission_coeff=0.9,  # Very clear
            site_elevation_m=site_elevation,
        )

        radiation_hazy = SolarRadiationRyanStolz.calculate(
            elevation=elevation,
            earth_sun_distance=earth_sun_distance,
            atmospheric_transmission_coeff=0.7,  # Hazy
            site_elevation_m=site_elevation,
        )

        # Clear sky should have more radiation
        assert radiation_clear > radiation_hazy, (
            f"Expected higher radiation in clear conditions (got {radiation_clear}) "
            f"than hazy conditions (got {radiation_hazy})"
        )

    def test_ryan_stolz_earth_sun_distance_effect(self):
        """Test Ryan-Stolz model with varying Earth-Sun distance."""
        # Compare perihelion (closest) vs aphelion (farthest)
        elevation = 45.0
        atc = 0.8
        site_elevation = 0.0

        radiation_perihelion = SolarRadiationRyanStolz.calculate(
            elevation=elevation,
            earth_sun_distance=0.983,  # Closest (January)
            atmospheric_transmission_coeff=atc,
            site_elevation_m=site_elevation,
        )

        radiation_aphelion = SolarRadiationRyanStolz.calculate(
            elevation=elevation,
            earth_sun_distance=1.017,  # Farthest (July)
            atmospheric_transmission_coeff=atc,
            site_elevation_m=site_elevation,
        )

        # Perihelion should have more radiation (closer to sun)
        assert radiation_perihelion > radiation_aphelion, (
            f"Expected higher radiation at perihelion (got {radiation_perihelion}) "
            f"than aphelion (got {radiation_aphelion})"
        )

        # Difference should be about 7% (inverse square law)
        ratio = radiation_perihelion / radiation_aphelion
        expected_ratio = (1.017 / 0.983) ** 2
        assert (
            abs(ratio - expected_ratio) < 0.01
        ), f"Expected ratio ~{expected_ratio:.3f}, got {ratio:.3f}"


class TestIqbalSolarRadiation:
    """Test Iqbal solar radiation model."""

    def test_iqbal_noon_summer(self):
        """Test Iqbal model at solar noon in summer."""
        # High sun angle (60 degrees), typical summer conditions
        zenith = 30.0  # 90 - 60 = 30 degrees from vertical
        earth_sun_distance = 1.0  # Mean distance
        pressure_mb = 1013.25  # Sea level pressure
        ozone_cm = 0.35  # Typical ozone
        temperature_k = 293.15  # 20°C
        relative_humidity = 0.5  # 50% RH
        visibility_km = 23.0  # Good visibility
        albedo = 0.2  # Typical ground albedo
        site_elevation_m = 0.0  # Sea level

        result = SolarRadiationIqbal.calculate(
            zenith=zenith,
            earth_sun_distance=earth_sun_distance,
            pressure_mb=pressure_mb,
            ozone_cm=ozone_cm,
            temperature_k=temperature_k,
            relative_humidity=relative_humidity,
            visibility_km=visibility_km,
            albedo=albedo,
            site_elevation_m=site_elevation_m,
        )

        # Check all components are present
        assert "direct_beam" in result
        assert "direct_hz" in result
        assert "diffuse_hz" in result
        assert "global_hz" in result
        assert "diffuse_rayleigh" in result
        assert "diffuse_aerosol" in result
        assert "diffuse_multiple" in result

        # All components should be non-negative
        for key, value in result.items():
            assert value >= 0, f"{key} should be non-negative, got {value}"

        # Global should equal direct + diffuse
        assert (
            abs(result["global_hz"] - (result["direct_hz"] + result["diffuse_hz"])) < 0.1
        ), "Global should equal direct + diffuse"

        # Should have substantial radiation at high sun angle
        assert (
            result["global_hz"] > 500
        ), f"Expected substantial radiation at 30° zenith, got {result['global_hz']}"

    def test_iqbal_low_sun(self):
        """Test Iqbal model with low sun angle."""
        # Low sun angle (75 degrees zenith), typical early morning/late afternoon
        zenith = 75.0
        earth_sun_distance = 1.0
        pressure_mb = 1013.25
        ozone_cm = 0.35
        temperature_k = 293.15
        relative_humidity = 0.5
        visibility_km = 23.0
        albedo = 0.2
        site_elevation_m = 0.0

        result = SolarRadiationIqbal.calculate(
            zenith=zenith,
            earth_sun_distance=earth_sun_distance,
            pressure_mb=pressure_mb,
            ozone_cm=ozone_cm,
            temperature_k=temperature_k,
            relative_humidity=relative_humidity,
            visibility_km=visibility_km,
            albedo=albedo,
            site_elevation_m=site_elevation_m,
        )

        # Should be positive but lower than high sun
        assert (
            0 < result["global_hz"] < 500
        ), f"Expected lower radiation at 75° zenith, got {result['global_hz']}"

    def test_iqbal_below_horizon(self):
        """Test Iqbal model with sun below horizon."""
        # Zenith > 90 degrees (nighttime)
        zenith = 100.0
        earth_sun_distance = 1.0
        pressure_mb = 1013.25
        ozone_cm = 0.35
        temperature_k = 293.15
        relative_humidity = 0.5
        visibility_km = 23.0
        albedo = 0.2
        site_elevation_m = 0.0

        result = SolarRadiationIqbal.calculate(
            zenith=zenith,
            earth_sun_distance=earth_sun_distance,
            pressure_mb=pressure_mb,
            ozone_cm=ozone_cm,
            temperature_k=temperature_k,
            relative_humidity=relative_humidity,
            visibility_km=visibility_km,
            albedo=albedo,
            site_elevation_m=site_elevation_m,
        )

        # All components should be zero at night
        for key, value in result.items():
            assert value == 0.0, f"{key} should be zero below horizon, got {value}"

    def test_iqbal_near_horizon(self):
        """Test Iqbal model with sun near horizon."""
        # Zenith = 89 degrees (at threshold)
        zenith = 89.0
        earth_sun_distance = 1.0
        pressure_mb = 1013.25
        ozone_cm = 0.35
        temperature_k = 293.15
        relative_humidity = 0.5
        visibility_km = 23.0
        albedo = 0.2
        site_elevation_m = 0.0

        result = SolarRadiationIqbal.calculate(
            zenith=zenith,
            earth_sun_distance=earth_sun_distance,
            pressure_mb=pressure_mb,
            ozone_cm=ozone_cm,
            temperature_k=temperature_k,
            relative_humidity=relative_humidity,
            visibility_km=visibility_km,
            albedo=albedo,
            site_elevation_m=site_elevation_m,
        )

        # All components should be zero at threshold
        for key, value in result.items():
            assert value == 0.0, f"{key} should be zero at 89° zenith, got {value}"

    def test_iqbal_high_elevation_site(self):
        """Test Iqbal model at high elevation site."""
        # High elevation site (2000m) should have higher radiation
        zenith = 45.0
        earth_sun_distance = 1.0
        pressure_mb_sea = 1013.25
        pressure_mb_high = 795.0  # Approximate pressure at 2000m
        ozone_cm = 0.35
        temperature_k = 293.15
        relative_humidity = 0.5
        visibility_km = 23.0
        albedo = 0.2

        result_sea_level = SolarRadiationIqbal.calculate(
            zenith=zenith,
            earth_sun_distance=earth_sun_distance,
            pressure_mb=pressure_mb_sea,
            ozone_cm=ozone_cm,
            temperature_k=temperature_k,
            relative_humidity=relative_humidity,
            visibility_km=visibility_km,
            albedo=albedo,
            site_elevation_m=0.0,
        )

        result_high_elev = SolarRadiationIqbal.calculate(
            zenith=zenith,
            earth_sun_distance=earth_sun_distance,
            pressure_mb=pressure_mb_high,
            ozone_cm=ozone_cm,
            temperature_k=temperature_k,
            relative_humidity=relative_humidity,
            visibility_km=visibility_km,
            albedo=albedo,
            site_elevation_m=2000.0,
        )

        # High elevation should have more radiation
        assert result_high_elev["global_hz"] > result_sea_level["global_hz"], (
            f"Expected higher radiation at elevation (got {result_high_elev['global_hz']}) "
            f"than sea level (got {result_sea_level['global_hz']})"
        )

    def test_iqbal_clear_vs_hazy(self):
        """Test Iqbal model with different visibility conditions."""
        # Compare clear sky (high visibility) vs hazy sky (low visibility)
        zenith = 45.0
        earth_sun_distance = 1.0
        pressure_mb = 1013.25
        ozone_cm = 0.35
        temperature_k = 293.15
        relative_humidity = 0.5
        albedo = 0.2
        site_elevation_m = 0.0

        result_clear = SolarRadiationIqbal.calculate(
            zenith=zenith,
            earth_sun_distance=earth_sun_distance,
            pressure_mb=pressure_mb,
            ozone_cm=ozone_cm,
            temperature_k=temperature_k,
            relative_humidity=relative_humidity,
            visibility_km=50.0,  # Very clear
            albedo=albedo,
            site_elevation_m=site_elevation_m,
        )

        result_hazy = SolarRadiationIqbal.calculate(
            zenith=zenith,
            earth_sun_distance=earth_sun_distance,
            pressure_mb=pressure_mb,
            ozone_cm=ozone_cm,
            temperature_k=temperature_k,
            relative_humidity=relative_humidity,
            visibility_km=5.0,  # Hazy
            albedo=albedo,
            site_elevation_m=site_elevation_m,
        )

        # Clear sky should have more radiation
        assert result_clear["global_hz"] > result_hazy["global_hz"], (
            f"Expected higher radiation in clear conditions (got {result_clear['global_hz']}) "
            f"than hazy conditions (got {result_hazy['global_hz']})"
        )

    def test_iqbal_diffuse_components_sum(self):
        """Test that diffuse components sum correctly."""
        zenith = 45.0
        earth_sun_distance = 1.0
        pressure_mb = 1013.25
        ozone_cm = 0.35
        temperature_k = 293.15
        relative_humidity = 0.5
        visibility_km = 23.0
        albedo = 0.2
        site_elevation_m = 0.0

        result = SolarRadiationIqbal.calculate(
            zenith=zenith,
            earth_sun_distance=earth_sun_distance,
            pressure_mb=pressure_mb,
            ozone_cm=ozone_cm,
            temperature_k=temperature_k,
            relative_humidity=relative_humidity,
            visibility_km=visibility_km,
            albedo=albedo,
            site_elevation_m=site_elevation_m,
        )

        # Diffuse should equal sum of components
        diffuse_sum = (
            result["diffuse_rayleigh"] + result["diffuse_aerosol"] + result["diffuse_multiple"]
        )

        assert abs(result["diffuse_hz"] - diffuse_sum) < 0.1, (
            f"Diffuse components should sum to total diffuse: "
            f"{diffuse_sum} vs {result['diffuse_hz']}"
        )

    def test_iqbal_water_vapor_effect(self):
        """Test Iqbal model with different humidity levels."""
        # Compare dry vs humid conditions
        zenith = 45.0
        earth_sun_distance = 1.0
        pressure_mb = 1013.25
        ozone_cm = 0.35
        temperature_k = 293.15
        visibility_km = 23.0
        albedo = 0.2
        site_elevation_m = 0.0

        result_dry = SolarRadiationIqbal.calculate(
            zenith=zenith,
            earth_sun_distance=earth_sun_distance,
            pressure_mb=pressure_mb,
            ozone_cm=ozone_cm,
            temperature_k=temperature_k,
            relative_humidity=0.1,  # Dry
            visibility_km=visibility_km,
            albedo=albedo,
            site_elevation_m=site_elevation_m,
        )

        result_humid = SolarRadiationIqbal.calculate(
            zenith=zenith,
            earth_sun_distance=earth_sun_distance,
            pressure_mb=pressure_mb,
            ozone_cm=ozone_cm,
            temperature_k=temperature_k,
            relative_humidity=0.9,  # Humid
            visibility_km=visibility_km,
            albedo=albedo,
            site_elevation_m=site_elevation_m,
        )

        # Dry conditions should have more radiation (less water vapor absorption)
        assert result_dry["global_hz"] > result_humid["global_hz"], (
            f"Expected higher radiation in dry conditions (got {result_dry['global_hz']}) "
            f"than humid conditions (got {result_humid['global_hz']})"
        )
