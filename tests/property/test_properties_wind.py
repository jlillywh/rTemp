"""
Property-based tests for wind function models.

These tests use Hypothesis to verify that wind function properties hold
across a wide range of input values.
"""

import math
import pytest
from hypothesis import given, settings, assume
from hypothesis import strategies as st

from rtemp.wind.functions import (
    WindFunctionBradyGravesGeyer,
    WindFunctionMarcianoHarbeck,
    WindFunctionRyanHarleman,
    WindFunctionEastMesa,
    WindFunctionHelfrich,
    calculate_virtual_temperature_difference,
)
from rtemp.utils.atmospheric import AtmosphericHelpers


# Strategy for generating valid wind speeds (non-negative, reasonable range)
wind_speed_strategy = st.floats(
    min_value=0.0, max_value=50.0, allow_nan=False, allow_infinity=False
)

# Strategy for generating valid temperatures (reasonable meteorological range)
temperature_strategy = st.floats(
    min_value=-10.0, max_value=45.0, allow_nan=False, allow_infinity=False
)


def calculate_saturation_vapor_pressure(temp_c: float) -> float:
    """Calculate saturation vapor pressure for a given temperature."""
    return AtmosphericHelpers.saturation_vapor_pressure(temp_c)


@st.composite
def realistic_meteorological_conditions(draw):
    """
    Generate physically realistic meteorological conditions.

    This ensures that vapor pressures do not exceed saturation vapor pressure
    for the given temperatures, which is physically impossible.
    """
    # Generate temperatures
    air_temp = draw(
        st.floats(min_value=-10.0, max_value=45.0, allow_nan=False, allow_infinity=False)
    )
    water_temp = draw(
        st.floats(min_value=-10.0, max_value=45.0, allow_nan=False, allow_infinity=False)
    )

    # Calculate saturation vapor pressures
    sat_vp_air = calculate_saturation_vapor_pressure(air_temp)
    sat_vp_water = calculate_saturation_vapor_pressure(water_temp)

    # Generate vapor pressures that don't exceed saturation
    # Use 0.1 to 0.95 of saturation to ensure realistic relative humidity
    vapor_pressure_air = draw(
        st.floats(
            min_value=max(0.1, sat_vp_air * 0.1),
            max_value=sat_vp_air * 0.95,
            allow_nan=False,
            allow_infinity=False,
        )
    )

    # Water surface is typically at or near saturation
    vapor_pressure_water = draw(
        st.floats(
            min_value=max(0.1, sat_vp_water * 0.8),
            max_value=sat_vp_water,
            allow_nan=False,
            allow_infinity=False,
        )
    )

    return air_temp, water_temp, vapor_pressure_air, vapor_pressure_water


class TestWindFunctionPositivityProperty:
    """Property-based tests for wind function positivity."""

    # Feature: rtemp-python-complete, Property 11: Wind Function Positivity
    # Validates: Requirements 5.1-5.5
    @given(
        wind_speed=wind_speed_strategy,
        conditions=realistic_meteorological_conditions(),
    )
    @settings(max_examples=100)
    def test_brady_graves_geyer_positivity(
        self,
        wind_speed: float,
        conditions: tuple,
    ):
        """
        Property 11: Wind Function Positivity - Brady-Graves-Geyer

        For any non-negative wind speed and physically realistic meteorological
        conditions, the Brady-Graves-Geyer wind function should produce a positive result.

        Validates: Requirements 5.1
        """
        air_temp, water_temp, vapor_pressure_air, vapor_pressure_water = conditions

        wf = WindFunctionBradyGravesGeyer()
        result = wf.calculate(
            wind_speed, air_temp, water_temp, vapor_pressure_air, vapor_pressure_water
        )

        assert result > 0, f"Wind function should be positive, got {result}"

    # Feature: rtemp-python-complete, Property 11: Wind Function Positivity
    # Validates: Requirements 5.1-5.5
    @given(
        wind_speed=wind_speed_strategy,
        conditions=realistic_meteorological_conditions(),
    )
    @settings(max_examples=100)
    def test_marciano_harbeck_positivity(
        self,
        wind_speed: float,
        conditions: tuple,
    ):
        """
        Property 11: Wind Function Positivity - Marciano-Harbeck

        For any non-negative wind speed and physically realistic meteorological
        conditions, the Marciano-Harbeck wind function should produce a positive result.

        Validates: Requirements 5.2
        """
        air_temp, water_temp, vapor_pressure_air, vapor_pressure_water = conditions

        wf = WindFunctionMarcianoHarbeck()
        result = wf.calculate(
            wind_speed, air_temp, water_temp, vapor_pressure_air, vapor_pressure_water
        )

        assert result > 0, f"Wind function should be positive, got {result}"

    # Feature: rtemp-python-complete, Property 11: Wind Function Positivity
    # Validates: Requirements 5.1-5.5
    @given(
        wind_speed=wind_speed_strategy,
        conditions=realistic_meteorological_conditions(),
    )
    @settings(max_examples=100)
    def test_ryan_harleman_positivity(
        self,
        wind_speed: float,
        conditions: tuple,
    ):
        """
        Property 11: Wind Function Positivity - Ryan-Harleman

        For any non-negative wind speed and physically realistic meteorological
        conditions, the Ryan-Harleman wind function should produce a positive result.

        Validates: Requirements 5.3
        """
        air_temp, water_temp, vapor_pressure_air, vapor_pressure_water = conditions

        wf = WindFunctionRyanHarleman()
        result = wf.calculate(
            wind_speed, air_temp, water_temp, vapor_pressure_air, vapor_pressure_water
        )

        assert result > 0, f"Wind function should be positive, got {result}"

    # Feature: rtemp-python-complete, Property 11: Wind Function Positivity
    # Validates: Requirements 5.1-5.5
    @given(
        wind_speed=wind_speed_strategy,
        conditions=realistic_meteorological_conditions(),
    )
    @settings(max_examples=100)
    def test_east_mesa_positivity(
        self,
        wind_speed: float,
        conditions: tuple,
    ):
        """
        Property 11: Wind Function Positivity - East Mesa

        For any non-negative wind speed and physically realistic meteorological
        conditions, the East Mesa wind function should produce a positive result.

        Validates: Requirements 5.4
        """
        air_temp, water_temp, vapor_pressure_air, vapor_pressure_water = conditions

        wf = WindFunctionEastMesa()
        result = wf.calculate(
            wind_speed, air_temp, water_temp, vapor_pressure_air, vapor_pressure_water
        )

        assert result > 0, f"Wind function should be positive, got {result}"

    # Feature: rtemp-python-complete, Property 11: Wind Function Positivity
    # Validates: Requirements 5.1-5.5
    @given(
        wind_speed=wind_speed_strategy,
        conditions=realistic_meteorological_conditions(),
    )
    @settings(max_examples=100)
    def test_helfrich_positivity(
        self,
        wind_speed: float,
        conditions: tuple,
    ):
        """
        Property 11: Wind Function Positivity - Helfrich

        For any non-negative wind speed and physically realistic meteorological
        conditions, the Helfrich wind function should produce a positive result.

        Validates: Requirements 5.5
        """
        air_temp, water_temp, vapor_pressure_air, vapor_pressure_water = conditions

        wf = WindFunctionHelfrich()
        result = wf.calculate(
            wind_speed, air_temp, water_temp, vapor_pressure_air, vapor_pressure_water
        )

        assert result > 0, f"Wind function should be positive, got {result}"


class TestWindFunctionMonotonicityProperty:
    """Property-based tests for wind function monotonicity with wind speed."""

    # Feature: rtemp-python-complete, Property 12: Wind Function Increases with Wind Speed
    # Validates: Requirements 5.1-5.5
    @given(
        wind_speed_low=st.floats(
            min_value=0.0, max_value=25.0, allow_nan=False, allow_infinity=False
        ),
        wind_speed_high=st.floats(
            min_value=25.0, max_value=50.0, allow_nan=False, allow_infinity=False
        ),
        conditions=realistic_meteorological_conditions(),
    )
    @settings(max_examples=100)
    def test_brady_graves_geyer_monotonicity(
        self,
        wind_speed_low: float,
        wind_speed_high: float,
        conditions: tuple,
    ):
        """
        Property 12: Wind Function Increases with Wind Speed - Brady-Graves-Geyer

        For any two wind speeds where wind_speed_high > wind_speed_low and physically
        realistic meteorological conditions, the Brady-Graves-Geyer wind function
        should produce a higher result for the higher wind speed.

        Validates: Requirements 5.1
        """
        air_temp, water_temp, vapor_pressure_air, vapor_pressure_water = conditions

        # Ensure wind_speed_high > wind_speed_low
        assume(wind_speed_high > wind_speed_low)

        wf = WindFunctionBradyGravesGeyer()

        result_low = wf.calculate(
            wind_speed_low, air_temp, water_temp, vapor_pressure_air, vapor_pressure_water
        )
        result_high = wf.calculate(
            wind_speed_high, air_temp, water_temp, vapor_pressure_air, vapor_pressure_water
        )

        assert result_high > result_low, (
            f"Wind function should increase with wind speed: "
            f"f({wind_speed_low}) = {result_low}, f({wind_speed_high}) = {result_high}"
        )

    # Feature: rtemp-python-complete, Property 12: Wind Function Increases with Wind Speed
    # Validates: Requirements 5.1-5.5
    @given(
        wind_speed_low=st.floats(
            min_value=0.0, max_value=25.0, allow_nan=False, allow_infinity=False
        ),
        wind_speed_high=st.floats(
            min_value=25.0, max_value=50.0, allow_nan=False, allow_infinity=False
        ),
        conditions=realistic_meteorological_conditions(),
    )
    @settings(max_examples=100)
    def test_marciano_harbeck_monotonicity(
        self,
        wind_speed_low: float,
        wind_speed_high: float,
        conditions: tuple,
    ):
        """
        Property 12: Wind Function Increases with Wind Speed - Marciano-Harbeck

        For any two wind speeds where wind_speed_high > wind_speed_low and physically
        realistic meteorological conditions, the Marciano-Harbeck wind function
        should produce a higher result for the higher wind speed.

        Validates: Requirements 5.2
        """
        air_temp, water_temp, vapor_pressure_air, vapor_pressure_water = conditions

        # Ensure wind_speed_high > wind_speed_low
        assume(wind_speed_high > wind_speed_low)

        wf = WindFunctionMarcianoHarbeck()

        result_low = wf.calculate(
            wind_speed_low, air_temp, water_temp, vapor_pressure_air, vapor_pressure_water
        )
        result_high = wf.calculate(
            wind_speed_high, air_temp, water_temp, vapor_pressure_air, vapor_pressure_water
        )

        # Use >= to handle floating point precision issues when wind speeds are very close
        assert result_high >= result_low, (
            f"Wind function should increase with wind speed: "
            f"f({wind_speed_low}) = {result_low}, f({wind_speed_high}) = {result_high}"
        )

    # Feature: rtemp-python-complete, Property 12: Wind Function Increases with Wind Speed
    # Validates: Requirements 5.1-5.5
    @given(
        wind_speed_low=st.floats(
            min_value=0.0, max_value=25.0, allow_nan=False, allow_infinity=False
        ),
        wind_speed_high=st.floats(
            min_value=25.0, max_value=50.0, allow_nan=False, allow_infinity=False
        ),
        conditions=realistic_meteorological_conditions(),
    )
    @settings(max_examples=100)
    def test_ryan_harleman_monotonicity(
        self,
        wind_speed_low: float,
        wind_speed_high: float,
        conditions: tuple,
    ):
        """
        Property 12: Wind Function Increases with Wind Speed - Ryan-Harleman

        For any two wind speeds where wind_speed_high > wind_speed_low and physically
        realistic meteorological conditions, the Ryan-Harleman wind function
        should produce a higher result for the higher wind speed.

        Validates: Requirements 5.3
        """
        air_temp, water_temp, vapor_pressure_air, vapor_pressure_water = conditions

        # Ensure wind_speed_high > wind_speed_low
        assume(wind_speed_high > wind_speed_low)

        wf = WindFunctionRyanHarleman()

        result_low = wf.calculate(
            wind_speed_low, air_temp, water_temp, vapor_pressure_air, vapor_pressure_water
        )
        result_high = wf.calculate(
            wind_speed_high, air_temp, water_temp, vapor_pressure_air, vapor_pressure_water
        )

        assert result_high > result_low, (
            f"Wind function should increase with wind speed: "
            f"f({wind_speed_low}) = {result_low}, f({wind_speed_high}) = {result_high}"
        )

    # Feature: rtemp-python-complete, Property 12: Wind Function Increases with Wind Speed
    # Validates: Requirements 5.1-5.5
    @given(
        wind_speed_low=st.floats(
            min_value=0.0, max_value=25.0, allow_nan=False, allow_infinity=False
        ),
        wind_speed_high=st.floats(
            min_value=25.0, max_value=50.0, allow_nan=False, allow_infinity=False
        ),
        conditions=realistic_meteorological_conditions(),
    )
    @settings(max_examples=100)
    def test_east_mesa_monotonicity(
        self,
        wind_speed_low: float,
        wind_speed_high: float,
        conditions: tuple,
    ):
        """
        Property 12: Wind Function Increases with Wind Speed - East Mesa

        For any two wind speeds where wind_speed_high > wind_speed_low and physically
        realistic meteorological conditions, the East Mesa wind function
        should produce a higher result for the higher wind speed.

        Validates: Requirements 5.4
        """
        air_temp, water_temp, vapor_pressure_air, vapor_pressure_water = conditions

        # Ensure wind_speed_high > wind_speed_low
        assume(wind_speed_high > wind_speed_low)

        wf = WindFunctionEastMesa()

        result_low = wf.calculate(
            wind_speed_low, air_temp, water_temp, vapor_pressure_air, vapor_pressure_water
        )
        result_high = wf.calculate(
            wind_speed_high, air_temp, water_temp, vapor_pressure_air, vapor_pressure_water
        )

        assert result_high > result_low, (
            f"Wind function should increase with wind speed: "
            f"f({wind_speed_low}) = {result_low}, f({wind_speed_high}) = {result_high}"
        )

    # Feature: rtemp-python-complete, Property 12: Wind Function Increases with Wind Speed
    # Validates: Requirements 5.1-5.5
    @given(
        wind_speed_low=st.floats(
            min_value=0.0, max_value=25.0, allow_nan=False, allow_infinity=False
        ),
        wind_speed_high=st.floats(
            min_value=25.0, max_value=50.0, allow_nan=False, allow_infinity=False
        ),
        conditions=realistic_meteorological_conditions(),
    )
    @settings(max_examples=100)
    def test_helfrich_monotonicity(
        self,
        wind_speed_low: float,
        wind_speed_high: float,
        conditions: tuple,
    ):
        """
        Property 12: Wind Function Increases with Wind Speed - Helfrich

        For any two wind speeds where wind_speed_high > wind_speed_low and physically
        realistic meteorological conditions, the Helfrich wind function
        should produce a higher result for the higher wind speed.

        Validates: Requirements 5.5
        """
        air_temp, water_temp, vapor_pressure_air, vapor_pressure_water = conditions

        # Ensure wind_speed_high > wind_speed_low
        assume(wind_speed_high > wind_speed_low)

        wf = WindFunctionHelfrich()

        result_low = wf.calculate(
            wind_speed_low, air_temp, water_temp, vapor_pressure_air, vapor_pressure_water
        )
        result_high = wf.calculate(
            wind_speed_high, air_temp, water_temp, vapor_pressure_air, vapor_pressure_water
        )

        assert result_high > result_low, (
            f"Wind function should increase with wind speed: "
            f"f({wind_speed_low}) = {result_low}, f({wind_speed_high}) = {result_high}"
        )


class TestVirtualTemperatureProperties:
    """Property-based tests for virtual temperature calculations."""

    @given(conditions=realistic_meteorological_conditions())
    @settings(max_examples=100)
    def test_virtual_temperature_sign_consistency(
        self,
        conditions: tuple,
    ):
        """
        Property: Virtual temperature difference sign consistency.

        When water is warmer than air and has higher vapor pressure,
        the virtual temperature difference should be positive.
        When air is warmer than water and has higher vapor pressure,
        the virtual temperature difference should be negative.
        """
        air_temp, water_temp, vapor_pressure_air, vapor_pressure_water = conditions

        delta_t_v = calculate_virtual_temperature_difference(
            air_temp, water_temp, vapor_pressure_air, vapor_pressure_water
        )

        # If water is significantly warmer and has higher vapor pressure
        if water_temp > air_temp + 1.0 and vapor_pressure_water > vapor_pressure_air:
            assert delta_t_v > 0, (
                f"Virtual temp difference should be positive when water is warmer: "
                f"air={air_temp}, water={water_temp}, delta_t_v={delta_t_v}"
            )

        # If air is significantly warmer and has higher vapor pressure
        if air_temp > water_temp + 1.0 and vapor_pressure_air > vapor_pressure_water:
            assert delta_t_v < 0, (
                f"Virtual temp difference should be negative when air is warmer: "
                f"air={air_temp}, water={water_temp}, delta_t_v={delta_t_v}"
            )

    @given(
        temp=temperature_strategy,
        conditions=realistic_meteorological_conditions(),
    )
    @settings(max_examples=100)
    def test_virtual_temperature_vapor_pressure_effect(
        self,
        temp: float,
        conditions: tuple,
    ):
        """
        Property: Virtual temperature increases with vapor pressure.

        At the same temperature, higher vapor pressure at the water surface
        should result in higher virtual temperature difference.
        """
        air_temp, water_temp, vapor_pressure_air, vapor_pressure_water = conditions

        # Calculate saturation vapor pressure at temp
        sat_vp = calculate_saturation_vapor_pressure(temp)

        # Generate two different vapor pressures for water, both realistic
        vapor_pressure_low = min(vapor_pressure_water, sat_vp * 0.7)
        vapor_pressure_high = min(sat_vp * 0.95, vapor_pressure_water * 1.2)

        # Ensure they're different enough to matter
        assume(vapor_pressure_high > vapor_pressure_low + 0.5)

        # Keep air conditions constant, vary water vapor pressure
        delta_t_v_low = calculate_virtual_temperature_difference(
            temp, temp, vapor_pressure_air, vapor_pressure_low
        )
        delta_t_v_high = calculate_virtual_temperature_difference(
            temp, temp, vapor_pressure_air, vapor_pressure_high
        )

        # Higher water vapor pressure should give higher virtual temp difference
        assert delta_t_v_high > delta_t_v_low, (
            f"Higher vapor pressure should increase virtual temp difference: "
            f"low={delta_t_v_low}, high={delta_t_v_high}"
        )
