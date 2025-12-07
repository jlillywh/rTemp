"""
Unit tests for atmospheric helper functions.

This module contains unit tests for atmospheric calculations including
vapor pressure, humidity, and pressure calculations.
"""

import pytest
import math

from rtemp.utils.atmospheric import AtmosphericHelpers


class TestAtmosphericHelpers:
    """Unit tests for AtmosphericHelpers class."""

    def test_saturation_vapor_pressure_at_zero(self):
        """Test saturation vapor pressure at 0°C."""
        vp = AtmosphericHelpers.saturation_vapor_pressure(0.0)
        # At 0°C, saturation vapor pressure should be approximately 4.58 mmHg
        assert 4.5 < vp < 4.7, f"Expected ~4.58 mmHg, got {vp}"

    def test_saturation_vapor_pressure_at_20c(self):
        """Test saturation vapor pressure at 20°C."""
        vp = AtmosphericHelpers.saturation_vapor_pressure(20.0)
        # At 20°C, saturation vapor pressure should be approximately 17.5 mmHg
        assert 17.0 < vp < 18.0, f"Expected ~17.5 mmHg, got {vp}"

    def test_saturation_vapor_pressure_at_100c(self):
        """Test saturation vapor pressure at 100°C (boiling point)."""
        vp = AtmosphericHelpers.saturation_vapor_pressure(100.0)
        # At 100°C, saturation vapor pressure should be approximately 760 mmHg (1 atm)
        assert 750 < vp < 770, f"Expected ~760 mmHg, got {vp}"

    def test_saturation_vapor_pressure_negative_temp(self):
        """Test saturation vapor pressure at negative temperature."""
        vp = AtmosphericHelpers.saturation_vapor_pressure(-10.0)
        # Should still return a positive value
        assert vp > 0, "Vapor pressure should be positive even at negative temperatures"
        # Should be less than at 0°C
        vp_zero = AtmosphericHelpers.saturation_vapor_pressure(0.0)
        assert vp < vp_zero, "Vapor pressure at -10°C should be less than at 0°C"

    def test_dewpoint_from_rh_100_percent(self):
        """Test dewpoint calculation at 100% relative humidity."""
        air_temp = 20.0
        dewpoint = AtmosphericHelpers.dewpoint_from_rh(air_temp, 1.0)
        # At 100% RH, dewpoint should equal air temperature
        assert (
            abs(dewpoint - air_temp) < 0.1
        ), f"At 100% RH, dewpoint should equal air temp: {dewpoint} vs {air_temp}"

    def test_dewpoint_from_rh_50_percent(self):
        """Test dewpoint calculation at 50% relative humidity."""
        air_temp = 20.0
        dewpoint = AtmosphericHelpers.dewpoint_from_rh(air_temp, 0.5)
        # At 50% RH and 20°C, dewpoint should be approximately 9-10°C
        assert 8.0 < dewpoint < 11.0, f"Expected dewpoint ~9-10°C, got {dewpoint}"
        assert dewpoint < air_temp, "Dewpoint should be less than air temperature"

    def test_dewpoint_from_rh_zero_percent(self):
        """Test dewpoint calculation at 0% relative humidity."""
        air_temp = 20.0
        dewpoint = AtmosphericHelpers.dewpoint_from_rh(air_temp, 0.0)
        # Should return a very low dewpoint
        assert dewpoint < air_temp - 40, "Dewpoint at 0% RH should be very low"

    def test_relative_humidity_from_dewpoint_equal_temps(self):
        """Test RH calculation when dewpoint equals air temperature."""
        air_temp = 20.0
        dewpoint = 20.0
        rh = AtmosphericHelpers.relative_humidity_from_dewpoint(air_temp, dewpoint)
        # Should be 100% (1.0)
        assert abs(rh - 1.0) < 0.01, f"Expected RH = 1.0, got {rh}"

    def test_relative_humidity_from_dewpoint_lower_dewpoint(self):
        """Test RH calculation when dewpoint is lower than air temperature."""
        air_temp = 20.0
        dewpoint = 10.0
        rh = AtmosphericHelpers.relative_humidity_from_dewpoint(air_temp, dewpoint)
        # Should be between 0 and 1
        assert 0.0 < rh < 1.0, f"RH should be between 0 and 1, got {rh}"
        # For 20°C air and 10°C dewpoint, RH should be approximately 0.52
        assert 0.45 < rh < 0.60, f"Expected RH ~0.52, got {rh}"

    def test_pressure_from_altitude_sea_level(self):
        """Test pressure calculation at sea level."""
        pressure = AtmosphericHelpers.pressure_from_altitude(0.0)
        # Should be standard pressure (1013.25 mb)
        assert abs(pressure - 1013.25) < 0.01, f"Expected 1013.25 mb at sea level, got {pressure}"

    def test_pressure_from_altitude_1000m(self):
        """Test pressure calculation at 1000m altitude."""
        pressure = AtmosphericHelpers.pressure_from_altitude(1000.0)
        # At 1000m, pressure should be approximately 898-900 mb
        assert 895 < pressure < 905, f"Expected ~900 mb at 1000m, got {pressure}"
        # Should be less than sea level pressure
        assert pressure < 1013.25, "Pressure at altitude should be less than sea level"

    def test_pressure_from_altitude_negative(self):
        """Test pressure calculation below sea level."""
        pressure = AtmosphericHelpers.pressure_from_altitude(-100.0)
        # Should be greater than sea level pressure
        assert pressure > 1013.25, "Pressure below sea level should be greater"

    def test_water_vapor_saturation_lowe_liquid(self):
        """Test Lowe polynomial for liquid water."""
        temp_k = 293.15  # 20°C
        es = AtmosphericHelpers.water_vapor_saturation_lowe(temp_k, ice=False)
        # At 20°C, saturation vapor pressure should be approximately 23.4 hPa
        assert 22.0 < es < 25.0, f"Expected ~23.4 hPa at 20°C, got {es}"

    def test_water_vapor_saturation_lowe_ice(self):
        """Test Lowe polynomial for ice."""
        temp_k = 263.15  # -10°C
        es_ice = AtmosphericHelpers.water_vapor_saturation_lowe(temp_k, ice=True)
        es_water = AtmosphericHelpers.water_vapor_saturation_lowe(temp_k, ice=False)
        # Saturation vapor pressure over ice should be less than over water
        assert (
            es_ice < es_water
        ), "Saturation VP over ice should be less than over water at same temp"

    def test_water_vapor_saturation_lowe_freezing(self):
        """Test Lowe polynomial at freezing point."""
        temp_k = 273.15  # 0°C
        es = AtmosphericHelpers.water_vapor_saturation_lowe(temp_k, ice=False)
        # At 0°C, saturation vapor pressure should be approximately 6.11 hPa
        assert 6.0 < es < 6.3, f"Expected ~6.11 hPa at 0°C, got {es}"

    def test_koberg_brunt_coefficient_default(self):
        """Test Koberg Brunt coefficient with default parameters."""
        coeff = AtmosphericHelpers.koberg_brunt_coefficient(20.0)
        # Should be in reasonable range [0.4, 0.7]
        assert 0.4 <= coeff <= 0.7, f"Coefficient should be in [0.4, 0.7], got {coeff}"

    def test_koberg_brunt_coefficient_with_clearness(self):
        """Test Koberg Brunt coefficient with clearness factor."""
        coeff_clear = AtmosphericHelpers.koberg_brunt_coefficient(20.0, clearness=1.0)
        coeff_cloudy = AtmosphericHelpers.koberg_brunt_coefficient(20.0, clearness=0.0)
        # Clearer skies should give lower coefficient
        assert coeff_clear < coeff_cloudy, "Clear skies should have lower coefficient than cloudy"

    def test_koberg_brunt_coefficient_temperature_effect(self):
        """Test Koberg Brunt coefficient temperature dependence."""
        coeff_cold = AtmosphericHelpers.koberg_brunt_coefficient(-10.0)
        coeff_warm = AtmosphericHelpers.koberg_brunt_coefficient(30.0)
        # Warmer temperatures should give higher coefficient
        assert coeff_warm > coeff_cold, "Warmer temperatures should have higher coefficient"


class TestLongwaveRadiation:
    """Unit tests for LongwaveRadiation class."""

    def test_calculate_atmospheric_clear_sky(self):
        """Test atmospheric longwave radiation calculation for clear sky."""
        from rtemp.atmospheric import LongwaveRadiation

        # Clear sky (cloud_cover = 0)
        emissivity = 0.8
        air_temp_c = 20.0
        cloud_cover = 0.0

        longwave = LongwaveRadiation.calculate_atmospheric(emissivity, air_temp_c, cloud_cover)

        # Should be positive
        assert longwave > 0, "Longwave radiation should be positive"

        # For 20°C air with emissivity 0.8, expect around 315 W/m²
        # (accounting for 3% reflection reduction)
        assert 300 < longwave < 330, f"Expected ~315 W/m², got {longwave}"

    def test_calculate_atmospheric_overcast(self):
        """Test atmospheric longwave radiation calculation for overcast sky."""
        from rtemp.atmospheric import LongwaveRadiation

        # Overcast sky (cloud_cover = 1)
        emissivity = 0.8
        air_temp_c = 20.0
        cloud_cover = 1.0

        longwave_clear = LongwaveRadiation.calculate_atmospheric(emissivity, air_temp_c, 0.0)
        longwave_overcast = LongwaveRadiation.calculate_atmospheric(
            emissivity, air_temp_c, cloud_cover
        )

        # Overcast should have more radiation than clear sky
        assert (
            longwave_overcast > longwave_clear
        ), "Overcast sky should have more longwave radiation than clear sky"

    def test_calculate_atmospheric_equation_1(self):
        """Test atmospheric longwave radiation with Equation 1 cloud correction."""
        from rtemp.atmospheric import LongwaveRadiation

        emissivity = 0.8
        air_temp_c = 20.0
        cloud_cover = 0.5
        kcl3 = 1.0
        kcl4 = 2.0

        longwave = LongwaveRadiation.calculate_atmospheric(
            emissivity, air_temp_c, cloud_cover, cloud_method="Eqn 1", kcl3=kcl3, kcl4=kcl4
        )

        # Should be positive and reasonable
        assert longwave > 0, "Longwave radiation should be positive"
        assert 300 < longwave < 450, f"Expected reasonable value, got {longwave}"

    def test_calculate_atmospheric_equation_2(self):
        """Test atmospheric longwave radiation with Equation 2 cloud correction."""
        from rtemp.atmospheric import LongwaveRadiation

        emissivity = 0.8
        air_temp_c = 20.0
        cloud_cover = 0.5
        kcl3 = 1.0
        kcl4 = 2.0

        longwave = LongwaveRadiation.calculate_atmospheric(
            emissivity, air_temp_c, cloud_cover, cloud_method="Eqn 2", kcl3=kcl3, kcl4=kcl4
        )

        # Should be positive and reasonable
        assert longwave > 0, "Longwave radiation should be positive"
        assert 300 < longwave < 450, f"Expected reasonable value, got {longwave}"

    def test_calculate_atmospheric_temperature_effect(self):
        """Test that atmospheric radiation increases with temperature."""
        from rtemp.atmospheric import LongwaveRadiation

        emissivity = 0.8
        cloud_cover = 0.0

        longwave_cold = LongwaveRadiation.calculate_atmospheric(emissivity, 0.0, cloud_cover)
        longwave_warm = LongwaveRadiation.calculate_atmospheric(emissivity, 30.0, cloud_cover)

        # Warmer air should produce more longwave radiation
        assert longwave_warm > longwave_cold, "Warmer air should produce more longwave radiation"

    def test_calculate_atmospheric_emissivity_effect(self):
        """Test that atmospheric radiation increases with emissivity."""
        from rtemp.atmospheric import LongwaveRadiation

        air_temp_c = 20.0
        cloud_cover = 0.0

        longwave_low_emiss = LongwaveRadiation.calculate_atmospheric(0.6, air_temp_c, cloud_cover)
        longwave_high_emiss = LongwaveRadiation.calculate_atmospheric(0.9, air_temp_c, cloud_cover)

        # Higher emissivity should produce more longwave radiation
        assert (
            longwave_high_emiss > longwave_low_emiss
        ), "Higher emissivity should produce more longwave radiation"

    def test_calculate_atmospheric_reflection_reduction(self):
        """Test that surface reflection reduces atmospheric radiation by 3%."""
        from rtemp.atmospheric import LongwaveRadiation
        from rtemp.constants import STEFAN_BOLTZMANN, CELSIUS_TO_KELVIN

        emissivity = 0.8
        air_temp_c = 20.0
        cloud_cover = 0.0

        longwave = LongwaveRadiation.calculate_atmospheric(emissivity, air_temp_c, cloud_cover)

        # Calculate expected value without reflection
        air_temp_k = air_temp_c + CELSIUS_TO_KELVIN
        expected_no_reflection = emissivity * STEFAN_BOLTZMANN * (air_temp_k**4)
        expected_with_reflection = expected_no_reflection * 0.97

        # Should match within small tolerance
        assert (
            abs(longwave - expected_with_reflection) < 0.1
        ), f"Expected {expected_with_reflection}, got {longwave}"

    def test_calculate_back_radiation_20c(self):
        """Test back radiation calculation at 20°C."""
        from rtemp.atmospheric import LongwaveRadiation

        water_temp_c = 20.0
        back_radiation = LongwaveRadiation.calculate_back_radiation(water_temp_c)

        # Should be positive
        assert back_radiation > 0, "Back radiation should be positive"

        # For 20°C water, expect around 406 W/m²
        assert 400 < back_radiation < 415, f"Expected ~406 W/m², got {back_radiation}"

    def test_calculate_back_radiation_0c(self):
        """Test back radiation calculation at 0°C."""
        from rtemp.atmospheric import LongwaveRadiation

        water_temp_c = 0.0
        back_radiation = LongwaveRadiation.calculate_back_radiation(water_temp_c)

        # Should be positive
        assert back_radiation > 0, "Back radiation should be positive"

        # For 0°C water, expect around 306 W/m²
        assert 300 < back_radiation < 315, f"Expected ~306 W/m², got {back_radiation}"

    def test_calculate_back_radiation_temperature_effect(self):
        """Test that back radiation increases with water temperature."""
        from rtemp.atmospheric import LongwaveRadiation

        back_cold = LongwaveRadiation.calculate_back_radiation(0.0)
        back_warm = LongwaveRadiation.calculate_back_radiation(30.0)

        # Warmer water should emit more radiation
        assert back_warm > back_cold, "Warmer water should emit more back radiation"

    def test_calculate_back_radiation_stefan_boltzmann(self):
        """Test that back radiation follows Stefan-Boltzmann law."""
        from rtemp.atmospheric import LongwaveRadiation
        from rtemp.constants import STEFAN_BOLTZMANN, CELSIUS_TO_KELVIN, WATER_EMISSIVITY

        water_temp_c = 20.0
        back_radiation = LongwaveRadiation.calculate_back_radiation(water_temp_c)

        # Calculate expected value using Stefan-Boltzmann law
        water_temp_k = water_temp_c + CELSIUS_TO_KELVIN
        expected = WATER_EMISSIVITY * STEFAN_BOLTZMANN * (water_temp_k**4)

        # Should match within small tolerance
        assert abs(back_radiation - expected) < 0.1, f"Expected {expected}, got {back_radiation}"

    def test_calculate_back_radiation_negative_temperature(self):
        """Test back radiation calculation at negative temperature."""
        from rtemp.atmospheric import LongwaveRadiation

        water_temp_c = -5.0
        back_radiation = LongwaveRadiation.calculate_back_radiation(water_temp_c)

        # Should still be positive
        assert back_radiation > 0, "Back radiation should be positive even at negative temps"

        # Should be less than at 0°C
        back_0c = LongwaveRadiation.calculate_back_radiation(0.0)
        assert back_radiation < back_0c, "Back radiation at -5°C should be less than at 0°C"
