"""
Unit tests for wind function models.
"""

import pytest
import math
from rtemp.wind.functions import (
    WindFunctionBradyGravesGeyer,
    WindFunctionMarcianoHarbeck,
    WindFunctionRyanHarleman,
    WindFunctionEastMesa,
    WindFunctionHelfrich,
    calculate_virtual_temperature_difference,
)
from rtemp.constants import M_S_TO_MPH


class TestWindFunctionBradyGravesGeyer:
    """Test suite for Brady-Graves-Geyer wind function."""
    
    def test_basic_calculation(self):
        """Test basic wind function calculation."""
        wf = WindFunctionBradyGravesGeyer()
        
        # Test with wind speed of 5 m/s at 7m
        wind_speed = 5.0
        result = wf.calculate(wind_speed, 20.0, 15.0, 10.0, 12.0)
        
        # Expected: 19 + 0.95 * 5² = 19 + 23.75 = 42.75
        expected = 19.0 + 0.95 * (wind_speed ** 2)
        assert abs(result - expected) < 1e-10
        assert abs(result - 42.75) < 1e-10
    
    def test_zero_wind(self):
        """Test wind function with zero wind speed."""
        wf = WindFunctionBradyGravesGeyer()
        result = wf.calculate(0.0, 20.0, 15.0, 10.0, 12.0)
        
        # Expected: 19 + 0.95 * 0² = 19
        assert abs(result - 19.0) < 1e-10
    
    def test_high_wind(self):
        """Test wind function with high wind speed."""
        wf = WindFunctionBradyGravesGeyer()
        wind_speed = 10.0
        result = wf.calculate(wind_speed, 20.0, 15.0, 10.0, 12.0)
        
        # Expected: 19 + 0.95 * 100 = 114
        expected = 19.0 + 0.95 * 100.0
        assert abs(result - expected) < 1e-10
    
    def test_temperature_independence(self):
        """Test that result is independent of temperature inputs."""
        wf = WindFunctionBradyGravesGeyer()
        wind_speed = 3.0
        
        result1 = wf.calculate(wind_speed, 20.0, 15.0, 10.0, 12.0)
        result2 = wf.calculate(wind_speed, 30.0, 25.0, 15.0, 20.0)
        
        # Results should be identical regardless of temperatures
        assert abs(result1 - result2) < 1e-10


class TestWindFunctionMarcianoHarbeck:
    """Test suite for Marciano-Harbeck wind function."""
    
    def test_basic_calculation(self):
        """Test basic wind function calculation."""
        wf = WindFunctionMarcianoHarbeck()
        
        # Test with wind speed of 5 m/s at 7m
        wind_speed = 5.0
        result = wf.calculate(wind_speed, 20.0, 15.0, 10.0, 12.0)
        
        # Convert to mph: 5.0 * 2.23694 ≈ 11.1847 mph
        wind_mph = wind_speed * M_S_TO_MPH
        # Expected: 70.0 + 0.7 * (11.1847)² ≈ 70.0 + 87.56 ≈ 157.56
        expected = 70.0 + 0.7 * (wind_mph ** 2)
        assert abs(result - expected) < 1e-6
    
    def test_zero_wind(self):
        """Test wind function with zero wind speed."""
        wf = WindFunctionMarcianoHarbeck()
        result = wf.calculate(0.0, 20.0, 15.0, 10.0, 12.0)
        
        # Expected: 70.0 + 0.7 * 0² = 70.0
        assert abs(result - 70.0) < 1e-10
    
    def test_unit_conversion(self):
        """Test that m/s to mph conversion is correct."""
        wf = WindFunctionMarcianoHarbeck()
        
        # 1 m/s ≈ 2.23694 mph
        wind_speed = 1.0
        result = wf.calculate(wind_speed, 20.0, 15.0, 10.0, 12.0)
        
        wind_mph = M_S_TO_MPH  # ≈ 2.23694
        expected = 70.0 + 0.7 * (wind_mph ** 2)
        assert abs(result - expected) < 1e-6
    
    def test_temperature_independence(self):
        """Test that result is independent of temperature inputs."""
        wf = WindFunctionMarcianoHarbeck()
        wind_speed = 3.0
        
        result1 = wf.calculate(wind_speed, 20.0, 15.0, 10.0, 12.0)
        result2 = wf.calculate(wind_speed, 30.0, 25.0, 15.0, 20.0)
        
        # Results should be identical regardless of temperatures
        assert abs(result1 - result2) < 1e-10


class TestWindFunctionRyanHarleman:
    """Test suite for Ryan-Harleman wind function."""
    
    def test_basic_calculation(self):
        """Test basic wind function calculation."""
        wf = WindFunctionRyanHarleman()
        
        # Test with typical conditions
        wind_speed = 3.0  # m/s at 2m
        air_temp = 20.0
        water_temp = 25.0
        vapor_pressure_air = 10.0
        vapor_pressure_water = 15.0
        
        result = wf.calculate(
            wind_speed, air_temp, water_temp, 
            vapor_pressure_air, vapor_pressure_water
        )
        
        # Should be positive
        assert result > 0
        
        # Should be greater than base value of 4.5
        assert result > 4.5
    
    def test_zero_wind(self):
        """Test wind function with zero wind speed."""
        wf = WindFunctionRyanHarleman()
        result = wf.calculate(0.0, 20.0, 25.0, 10.0, 15.0)
        
        # With zero wind, should get base value of 4.5
        assert abs(result - 4.5) < 1e-10
    
    def test_virtual_temperature_effect(self):
        """Test that virtual temperature affects result."""
        wf = WindFunctionRyanHarleman()
        wind_speed = 5.0
        
        # Case 1: Small temperature difference
        result1 = wf.calculate(wind_speed, 20.0, 21.0, 10.0, 11.0)
        
        # Case 2: Large temperature difference
        result2 = wf.calculate(wind_speed, 20.0, 30.0, 10.0, 20.0)
        
        # Larger temperature difference should give larger wind function
        assert result2 > result1
    
    def test_formula_structure(self):
        """Test that formula structure is correct."""
        wf = WindFunctionRyanHarleman()
        wind_speed = 4.0
        air_temp = 15.0
        water_temp = 20.0
        vapor_pressure_air = 8.0
        vapor_pressure_water = 12.0
        
        result = wf.calculate(
            wind_speed, air_temp, water_temp,
            vapor_pressure_air, vapor_pressure_water
        )
        
        # Calculate expected value manually
        delta_t_v = calculate_virtual_temperature_difference(
            air_temp, water_temp, vapor_pressure_air, vapor_pressure_water
        )
        expected = 4.5 + 0.05 * (wind_speed ** 2) * (1.0 + 0.4 * delta_t_v)
        
        assert abs(result - expected) < 1e-10


class TestWindFunctionEastMesa:
    """Test suite for East Mesa wind function."""
    
    def test_basic_calculation(self):
        """Test basic wind function calculation."""
        wf = WindFunctionEastMesa()
        
        wind_speed = 3.0
        air_temp = 20.0
        water_temp = 25.0
        vapor_pressure_air = 10.0
        vapor_pressure_water = 15.0
        
        result = wf.calculate(
            wind_speed, air_temp, water_temp,
            vapor_pressure_air, vapor_pressure_water
        )
        
        # Should be positive
        assert result > 0
        
        # Should be greater than base value of 3.0
        assert result > 3.0
    
    def test_zero_wind(self):
        """Test wind function with zero wind speed."""
        wf = WindFunctionEastMesa()
        result = wf.calculate(0.0, 20.0, 25.0, 10.0, 15.0)
        
        # With zero wind, should get base value of 3.0
        assert abs(result - 3.0) < 1e-10
    
    def test_linear_wind_dependence(self):
        """Test that wind function has linear wind speed dependence."""
        wf = WindFunctionEastMesa()
        
        # Double the wind speed
        result1 = wf.calculate(2.0, 20.0, 25.0, 10.0, 15.0)
        result2 = wf.calculate(4.0, 20.0, 25.0, 10.0, 15.0)
        
        # The wind-dependent part should roughly double
        # (not exactly due to virtual temperature term)
        assert result2 > result1
    
    def test_formula_structure(self):
        """Test that formula structure is correct."""
        wf = WindFunctionEastMesa()
        wind_speed = 5.0
        air_temp = 18.0
        water_temp = 22.0
        vapor_pressure_air = 9.0
        vapor_pressure_water = 13.0
        
        result = wf.calculate(
            wind_speed, air_temp, water_temp,
            vapor_pressure_air, vapor_pressure_water
        )
        
        # Calculate expected value manually
        delta_t_v = calculate_virtual_temperature_difference(
            air_temp, water_temp, vapor_pressure_air, vapor_pressure_water
        )
        expected = 3.0 + 0.15 * wind_speed * (1.0 + 0.3 * delta_t_v)
        
        assert abs(result - expected) < 1e-10


class TestWindFunctionHelfrich:
    """Test suite for Helfrich wind function."""
    
    def test_basic_calculation(self):
        """Test basic wind function calculation."""
        wf = WindFunctionHelfrich()
        
        wind_speed = 3.0
        air_temp = 20.0
        water_temp = 25.0
        vapor_pressure_air = 10.0
        vapor_pressure_water = 15.0
        
        result = wf.calculate(
            wind_speed, air_temp, water_temp,
            vapor_pressure_air, vapor_pressure_water
        )
        
        # Should be positive
        assert result > 0
        
        # Should be greater than base value of 5.2
        assert result > 5.2
    
    def test_zero_wind(self):
        """Test wind function with zero wind speed."""
        wf = WindFunctionHelfrich()
        result = wf.calculate(0.0, 20.0, 25.0, 10.0, 15.0)
        
        # With zero wind, should get base value of 5.2
        assert abs(result - 5.2) < 1e-10
    
    def test_comparison_with_ryan_harleman(self):
        """Test that Helfrich is similar to Ryan-Harleman but recalibrated."""
        wf_helfrich = WindFunctionHelfrich()
        wf_ryan = WindFunctionRyanHarleman()
        
        wind_speed = 4.0
        air_temp = 20.0
        water_temp = 25.0
        vapor_pressure_air = 10.0
        vapor_pressure_water = 15.0
        
        result_helfrich = wf_helfrich.calculate(
            wind_speed, air_temp, water_temp,
            vapor_pressure_air, vapor_pressure_water
        )
        result_ryan = wf_ryan.calculate(
            wind_speed, air_temp, water_temp,
            vapor_pressure_air, vapor_pressure_water
        )
        
        # Both should be positive and in similar range
        assert result_helfrich > 0
        assert result_ryan > 0
        
        # Helfrich has higher base (5.2 vs 4.5) and slightly higher coefficient
        # So it should generally be higher
        assert result_helfrich > result_ryan
    
    def test_formula_structure(self):
        """Test that formula structure is correct."""
        wf = WindFunctionHelfrich()
        wind_speed = 6.0
        air_temp = 22.0
        water_temp = 28.0
        vapor_pressure_air = 11.0
        vapor_pressure_water = 17.0
        
        result = wf.calculate(
            wind_speed, air_temp, water_temp,
            vapor_pressure_air, vapor_pressure_water
        )
        
        # Calculate expected value manually
        delta_t_v = calculate_virtual_temperature_difference(
            air_temp, water_temp, vapor_pressure_air, vapor_pressure_water
        )
        expected = 5.2 + 0.06 * (wind_speed ** 2) * (1.0 + 0.35 * delta_t_v)
        
        assert abs(result - expected) < 1e-10


class TestVirtualTemperatureDifference:
    """Test suite for virtual temperature difference calculation."""
    
    def test_basic_calculation(self):
        """Test basic virtual temperature difference calculation."""
        air_temp = 20.0
        water_temp = 25.0
        vapor_pressure_air = 10.0
        vapor_pressure_water = 15.0
        
        delta_t_v = calculate_virtual_temperature_difference(
            air_temp, water_temp, vapor_pressure_air, vapor_pressure_water
        )
        
        # Should be positive when water is warmer than air
        assert delta_t_v > 0
    
    def test_equal_temperatures(self):
        """Test when air and water temperatures are equal."""
        temp = 20.0
        vapor_pressure_air = 10.0
        vapor_pressure_water = 12.0
        
        delta_t_v = calculate_virtual_temperature_difference(
            temp, temp, vapor_pressure_air, vapor_pressure_water
        )
        
        # Should be small but not exactly zero due to vapor pressure difference
        assert abs(delta_t_v) < 1.0
    
    def test_water_warmer_than_air(self):
        """Test when water is warmer than air."""
        air_temp = 15.0
        water_temp = 25.0
        vapor_pressure_air = 8.0
        vapor_pressure_water = 16.0
        
        delta_t_v = calculate_virtual_temperature_difference(
            air_temp, water_temp, vapor_pressure_air, vapor_pressure_water
        )
        
        # Virtual temperature difference should be positive
        assert delta_t_v > 0
        
        # Should be larger than simple temperature difference due to vapor effect
        simple_diff = water_temp - air_temp
        assert delta_t_v > simple_diff
    
    def test_air_warmer_than_water(self):
        """Test when air is warmer than water."""
        air_temp = 25.0
        water_temp = 15.0
        vapor_pressure_air = 16.0
        vapor_pressure_water = 8.0
        
        delta_t_v = calculate_virtual_temperature_difference(
            air_temp, water_temp, vapor_pressure_air, vapor_pressure_water
        )
        
        # Virtual temperature difference should be negative
        assert delta_t_v < 0
    
    def test_vapor_pressure_effect(self):
        """Test that vapor pressure affects virtual temperature."""
        air_temp = 20.0
        water_temp = 20.0
        
        # Case 1: Equal vapor pressures
        delta_t_v1 = calculate_virtual_temperature_difference(
            air_temp, water_temp, 10.0, 10.0
        )
        
        # Case 2: Different vapor pressures
        delta_t_v2 = calculate_virtual_temperature_difference(
            air_temp, water_temp, 10.0, 15.0
        )
        
        # With higher vapor pressure at water surface, virtual temp difference should be positive
        assert delta_t_v2 > delta_t_v1
        assert abs(delta_t_v1) < 0.1  # Should be very small
        assert delta_t_v2 > 0
    
    def test_formula_structure(self):
        """Test that formula structure is correct."""
        air_temp = 18.0
        water_temp = 24.0
        vapor_pressure_air = 9.0
        vapor_pressure_water = 14.0
        
        delta_t_v = calculate_virtual_temperature_difference(
            air_temp, water_temp, vapor_pressure_air, vapor_pressure_water
        )
        
        # Calculate expected value manually
        standard_pressure_mmhg = 760.0
        air_temp_k = air_temp + 273.15
        water_temp_k = water_temp + 273.15
        
        t_virtual_air = air_temp_k * (1.0 + 0.378 * vapor_pressure_air / standard_pressure_mmhg)
        t_virtual_water = water_temp_k * (1.0 + 0.378 * vapor_pressure_water / standard_pressure_mmhg)
        expected = t_virtual_water - t_virtual_air
        
        assert abs(delta_t_v - expected) < 1e-10
    
    def test_typical_conditions(self):
        """Test with typical meteorological conditions."""
        # Typical summer day
        air_temp = 25.0
        water_temp = 28.0
        vapor_pressure_air = 15.0  # ~60% RH at 25°C
        vapor_pressure_water = 22.0  # Saturation at 28°C
        
        delta_t_v = calculate_virtual_temperature_difference(
            air_temp, water_temp, vapor_pressure_air, vapor_pressure_water
        )
        
        # Should be positive and reasonable
        assert delta_t_v > 0
        assert delta_t_v < 10.0  # Should not be unreasonably large


class TestWindFunctionComparison:
    """Test suite comparing different wind function methods."""
    
    def test_all_methods_positive(self):
        """Test that all methods produce positive results."""
        wind_speed = 5.0
        air_temp = 20.0
        water_temp = 25.0
        vapor_pressure_air = 10.0
        vapor_pressure_water = 15.0
        
        methods = [
            WindFunctionBradyGravesGeyer(),
            WindFunctionMarcianoHarbeck(),
            WindFunctionRyanHarleman(),
            WindFunctionEastMesa(),
            WindFunctionHelfrich(),
        ]
        
        for method in methods:
            result = method.calculate(
                wind_speed, air_temp, water_temp,
                vapor_pressure_air, vapor_pressure_water
            )
            assert result > 0, f"{method.__class__.__name__} produced non-positive result"
    
    def test_all_methods_increase_with_wind(self):
        """Test that all methods increase with wind speed."""
        air_temp = 20.0
        water_temp = 25.0
        vapor_pressure_air = 10.0
        vapor_pressure_water = 15.0
        
        methods = [
            WindFunctionBradyGravesGeyer(),
            WindFunctionMarcianoHarbeck(),
            WindFunctionRyanHarleman(),
            WindFunctionEastMesa(),
            WindFunctionHelfrich(),
        ]
        
        for method in methods:
            result_low = method.calculate(2.0, air_temp, water_temp, vapor_pressure_air, vapor_pressure_water)
            result_high = method.calculate(8.0, air_temp, water_temp, vapor_pressure_air, vapor_pressure_water)
            
            assert result_high > result_low, f"{method.__class__.__name__} did not increase with wind speed"
    
    def test_relative_magnitudes(self):
        """Test relative magnitudes of different methods."""
        wind_speed = 5.0
        air_temp = 20.0
        water_temp = 25.0
        vapor_pressure_air = 10.0
        vapor_pressure_water = 15.0
        
        brady = WindFunctionBradyGravesGeyer().calculate(
            wind_speed, air_temp, water_temp, vapor_pressure_air, vapor_pressure_water
        )
        marciano = WindFunctionMarcianoHarbeck().calculate(
            wind_speed, air_temp, water_temp, vapor_pressure_air, vapor_pressure_water
        )
        
        # Marciano-Harbeck typically gives much larger values due to mph conversion
        assert marciano > brady
