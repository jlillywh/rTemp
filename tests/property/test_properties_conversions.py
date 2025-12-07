"""
Property-based tests for unit conversion utilities.

These tests use Hypothesis to verify that conversion properties hold
across a wide range of input values.
"""

import math

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from rtemp.utils.conversions import UnitConversions


class TestUnitConversionProperties:
    """Property-based tests for unit conversions."""

    # Feature: rtemp-python-complete, Property 14: Unit Conversion Round Trip
    # Validates: Requirements 7.1-7.8
    @given(st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False))
    @settings(max_examples=100)
    def test_heat_flux_round_trip_property(self, value: float):
        """
        Property 14: Unit Conversion Round Trip - Heat Flux

        For any numeric value, converting from W/m² to cal/(cm²·day) and back
        should produce the original value within numerical precision.

        Validates: Requirements 7.1-7.2
        """
        converted = UnitConversions.watts_m2_to_cal_cm2_day(value)
        back = UnitConversions.cal_cm2_day_to_watts_m2(converted)
        assert back == pytest.approx(value, rel=1e-10, abs=1e-10)

    # Feature: rtemp-python-complete, Property 14: Unit Conversion Round Trip
    # Validates: Requirements 7.1-7.8
    @given(st.floats(min_value=-360.0, max_value=360.0, allow_nan=False, allow_infinity=False))
    @settings(max_examples=100)
    def test_angle_round_trip_property(self, degrees: float):
        """
        Property 14: Unit Conversion Round Trip - Angles

        For any angle in degrees, converting to radians and back should
        produce the original value within numerical precision.

        Validates: Requirements 7.7-7.8
        """
        radians = UnitConversions.deg_to_rad(degrees)
        back = UnitConversions.rad_to_deg(radians)
        assert back == pytest.approx(degrees, rel=1e-10, abs=1e-10)

    # Feature: rtemp-python-complete, Property 14: Unit Conversion Round Trip
    # Validates: Requirements 7.1-7.8
    @given(st.floats(min_value=-100.0, max_value=100.0, allow_nan=False, allow_infinity=False))
    @settings(max_examples=100)
    def test_temperature_round_trip_property(self, celsius: float):
        """
        Property 14: Unit Conversion Round Trip - Temperature

        For any temperature in Celsius, converting to Kelvin and back should
        produce the original value within numerical precision.

        Validates: Requirements 7.6
        """
        kelvin = UnitConversions.celsius_to_kelvin(celsius)
        back = UnitConversions.kelvin_to_celsius(kelvin)
        assert back == pytest.approx(celsius, rel=1e-10, abs=1e-10)

    # Feature: rtemp-python-complete, Property 14: Unit Conversion Round Trip
    # Validates: Requirements 7.1-7.8
    @given(st.floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False))
    @settings(max_examples=100)
    def test_length_round_trip_property(self, meters: float):
        """
        Property 14: Unit Conversion Round Trip - Length

        For any length in meters, converting to centimeters and back should
        produce the original value within numerical precision.

        Validates: Requirements 7.3
        """
        centimeters = UnitConversions.meters_to_centimeters(meters)
        back = UnitConversions.centimeters_to_meters(centimeters)
        assert back == pytest.approx(meters, rel=1e-10, abs=1e-10)

    # Feature: rtemp-python-complete, Property 14: Unit Conversion Round Trip
    # Validates: Requirements 7.1-7.8
    @given(st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False))
    @settings(max_examples=100)
    def test_wind_speed_round_trip_property(self, m_s: float):
        """
        Property 14: Unit Conversion Round Trip - Wind Speed

        For any wind speed in m/s, converting to mph and back should
        produce the original value within numerical precision.

        Validates: Requirements 7.5
        """
        mph = UnitConversions.m_s_to_mph(m_s)
        back = UnitConversions.mph_to_m_s(mph)
        assert back == pytest.approx(m_s, rel=1e-10, abs=1e-10)

    # Feature: rtemp-python-complete, Property 14: Unit Conversion Round Trip
    # Validates: Requirements 7.1-7.8
    @given(st.floats(min_value=0.0, max_value=10.0, allow_nan=False, allow_infinity=False))
    @settings(max_examples=100)
    def test_thermal_conductivity_round_trip_property(self, w_m_c: float):
        """
        Property 14: Unit Conversion Round Trip - Thermal Conductivity

        For any thermal conductivity in W/(m·°C), converting to cal/(s·cm·°C)
        and back should produce the original value within numerical precision.

        Validates: Requirements 7.4
        """
        cal_s_cm_c = UnitConversions.w_m_c_to_cal_s_cm_c(w_m_c)
        back = UnitConversions.cal_s_cm_c_to_w_m_c(cal_s_cm_c)
        assert back == pytest.approx(w_m_c, rel=1e-10, abs=1e-10)

    # Additional property: Conversion consistency
    @given(
        st.floats(min_value=-1000.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
        st.floats(min_value=-1000.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
    )
    @settings(max_examples=100)
    def test_heat_flux_linearity(self, value1: float, value2: float):
        """
        Property: Conversion linearity for heat flux.

        Converting the sum should equal the sum of conversions.
        This verifies that the conversion is a linear operation.
        """
        sum_converted = UnitConversions.watts_m2_to_cal_cm2_day(value1 + value2)
        converted_sum = UnitConversions.watts_m2_to_cal_cm2_day(
            value1
        ) + UnitConversions.watts_m2_to_cal_cm2_day(value2)
        assert sum_converted == pytest.approx(converted_sum, rel=1e-10, abs=1e-10)

    # Additional property: Zero preservation
    @given(
        st.sampled_from(
            [
                UnitConversions.watts_m2_to_cal_cm2_day,
                UnitConversions.cal_cm2_day_to_watts_m2,
                UnitConversions.deg_to_rad,
                UnitConversions.rad_to_deg,
                UnitConversions.celsius_to_kelvin,
                UnitConversions.meters_to_centimeters,
                UnitConversions.centimeters_to_meters,
                UnitConversions.m_s_to_mph,
                UnitConversions.mph_to_m_s,
                UnitConversions.w_m_c_to_cal_s_cm_c,
                UnitConversions.cal_s_cm_c_to_w_m_c,
            ]
        )
    )
    @settings(max_examples=100)
    def test_zero_preservation(self, conversion_func):
        """
        Property: Zero preservation.

        Converting zero should always produce zero (except for temperature
        conversions which have an offset).
        """
        # Skip temperature conversions as they have an offset
        if conversion_func in [
            UnitConversions.celsius_to_kelvin,
            UnitConversions.kelvin_to_celsius,
        ]:
            pytest.skip("Temperature conversions have an offset")

        result = conversion_func(0.0)
        assert result == pytest.approx(0.0, abs=1e-10)
