"""
Unit tests for wind speed height adjustment calculations.
"""

import pytest
import math
from rtemp.wind.adjustment import WindAdjustment


class TestWindAdjustment:
    """Test suite for WindAdjustment class."""
    
    def test_adjust_for_height_basic(self):
        """Test basic height adjustment calculation."""
        # Test adjusting from 10m to 2m (downward)
        wind_10m = 5.0
        adjusted = WindAdjustment.adjust_for_height(wind_10m, 10.0, 2.0)
        
        # Expected: 5.0 * (2.0/10.0)^0.15 = 5.0 * 0.79063...
        expected = 5.0 * (0.2 ** 0.15)
        assert abs(adjusted - expected) < 1e-6
        assert adjusted < wind_10m  # Wind should be lower at lower height
    
    def test_adjust_for_height_upward(self):
        """Test adjusting wind speed upward in height."""
        # Test adjusting from 2m to 7m (upward)
        wind_2m = 3.0
        adjusted = WindAdjustment.adjust_for_height(wind_2m, 2.0, 7.0)
        
        # Expected: 3.0 * (7.0/2.0)^0.15
        expected = 3.0 * (3.5 ** 0.15)
        assert abs(adjusted - expected) < 1e-6
        assert adjusted > wind_2m  # Wind should be higher at higher height
    
    def test_adjust_for_height_same_height(self):
        """Test that adjusting to same height returns original wind speed."""
        wind_speed = 4.5
        height = 5.0
        adjusted = WindAdjustment.adjust_for_height(wind_speed, height, height)
        
        assert abs(adjusted - wind_speed) < 1e-10
    
    def test_adjust_for_height_tva_exponent(self):
        """Test that TVA exponent of 0.15 is used correctly."""
        wind_speed = 10.0
        measured_height = 10.0
        target_height = 2.0
        
        adjusted = WindAdjustment.adjust_for_height(
            wind_speed, measured_height, target_height
        )
        
        # Manually calculate with exponent 0.15
        expected = wind_speed * ((target_height / measured_height) ** 0.15)
        assert abs(adjusted - expected) < 1e-10
    
    def test_adjust_for_height_zero_measured_height(self):
        """Test that zero measured height raises ValueError."""
        with pytest.raises(ValueError, match="Measured height must be greater than zero"):
            WindAdjustment.adjust_for_height(5.0, 0.0, 2.0)
    
    def test_adjust_for_height_negative_measured_height(self):
        """Test that negative measured height raises ValueError."""
        with pytest.raises(ValueError, match="Measured height must be greater than zero"):
            WindAdjustment.adjust_for_height(5.0, -1.0, 2.0)
    
    def test_adjust_for_height_zero_target_height(self):
        """Test that zero target height raises ValueError."""
        with pytest.raises(ValueError, match="Target height must be greater than zero"):
            WindAdjustment.adjust_for_height(5.0, 10.0, 0.0)
    
    def test_adjust_for_height_negative_target_height(self):
        """Test that negative target height raises ValueError."""
        with pytest.raises(ValueError, match="Target height must be greater than zero"):
            WindAdjustment.adjust_for_height(5.0, 10.0, -2.0)
    
    def test_apply_shelter_factor_no_shelter(self):
        """Test shelter factor of 1.0 (no sheltering)."""
        wind_speed = 5.0
        adjusted = WindAdjustment.apply_shelter_factor(wind_speed, 1.0)
        
        assert adjusted == wind_speed
    
    def test_apply_shelter_factor_partial_shelter(self):
        """Test partial sheltering effect."""
        wind_speed = 5.0
        shelter_factor = 0.8
        adjusted = WindAdjustment.apply_shelter_factor(wind_speed, shelter_factor)
        
        expected = wind_speed * shelter_factor
        assert adjusted == expected
        assert adjusted == 4.0
    
    def test_apply_shelter_factor_heavy_shelter(self):
        """Test heavy sheltering effect."""
        wind_speed = 5.0
        shelter_factor = 0.5
        adjusted = WindAdjustment.apply_shelter_factor(wind_speed, shelter_factor)
        
        assert adjusted == 2.5
    
    def test_apply_shelter_factor_complete_shelter(self):
        """Test complete sheltering (factor = 0)."""
        wind_speed = 5.0
        adjusted = WindAdjustment.apply_shelter_factor(wind_speed, 0.0)
        
        assert adjusted == 0.0
    
    def test_apply_shelter_factor_negative(self):
        """Test that negative shelter factor raises ValueError."""
        with pytest.raises(ValueError, match="Effective wind factor must be non-negative"):
            WindAdjustment.apply_shelter_factor(5.0, -0.1)
    
    def test_adjust_with_shelter_combined(self):
        """Test combined height and shelter adjustment."""
        wind_speed = 5.0
        measured_height = 10.0
        target_height = 2.0
        shelter_factor = 0.8
        
        adjusted = WindAdjustment.adjust_with_shelter(
            wind_speed, measured_height, target_height, shelter_factor
        )
        
        # First adjust for height
        height_adjusted = wind_speed * ((target_height / measured_height) ** 0.15)
        # Then apply shelter
        expected = height_adjusted * shelter_factor
        
        assert abs(adjusted - expected) < 1e-10
    
    def test_adjust_with_shelter_order_matters(self):
        """Test that height adjustment is applied before shelter factor."""
        wind_speed = 10.0
        measured_height = 10.0
        target_height = 7.0
        shelter_factor = 0.9
        
        # Using combined method
        combined = WindAdjustment.adjust_with_shelter(
            wind_speed, measured_height, target_height, shelter_factor
        )
        
        # Manual calculation: height first, then shelter
        step1 = WindAdjustment.adjust_for_height(wind_speed, measured_height, target_height)
        step2 = WindAdjustment.apply_shelter_factor(step1, shelter_factor)
        
        assert abs(combined - step2) < 1e-10
    
    def test_typical_use_case_10m_to_7m(self):
        """Test typical use case: adjusting from 10m measurement to 7m height."""
        # Typical scenario: wind measured at 10m, need it at 7m for wind function
        wind_10m = 3.5  # m/s
        adjusted_7m = WindAdjustment.adjust_for_height(wind_10m, 10.0, 7.0)
        
        # Should be slightly lower at 7m
        assert adjusted_7m < wind_10m
        assert adjusted_7m > 3.0  # But not drastically different
        
        # Check approximate value
        expected = 3.5 * ((7.0 / 10.0) ** 0.15)
        assert abs(adjusted_7m - expected) < 1e-6
    
    def test_typical_use_case_10m_to_2m(self):
        """Test typical use case: adjusting from 10m measurement to 2m height."""
        # Typical scenario: wind measured at 10m, need it at 2m for wind function
        wind_10m = 4.0  # m/s
        adjusted_2m = WindAdjustment.adjust_for_height(wind_10m, 10.0, 2.0)
        
        # Should be noticeably lower at 2m
        assert adjusted_2m < wind_10m
        
        # Check approximate value
        expected = 4.0 * ((2.0 / 10.0) ** 0.15)
        assert abs(adjusted_2m - expected) < 1e-6
    
    def test_zero_wind_speed(self):
        """Test that zero wind speed remains zero after adjustment."""
        adjusted_height = WindAdjustment.adjust_for_height(0.0, 10.0, 2.0)
        assert adjusted_height == 0.0
        
        adjusted_shelter = WindAdjustment.apply_shelter_factor(0.0, 0.8)
        assert adjusted_shelter == 0.0
        
        adjusted_combined = WindAdjustment.adjust_with_shelter(0.0, 10.0, 2.0, 0.8)
        assert adjusted_combined == 0.0
    
    def test_large_height_ratio(self):
        """Test adjustment with large height ratio."""
        # Adjusting from 1m to 100m
        wind_1m = 2.0
        adjusted = WindAdjustment.adjust_for_height(wind_1m, 1.0, 100.0)
        
        expected = 2.0 * (100.0 ** 0.15)
        assert abs(adjusted - expected) < 1e-6
        assert adjusted > wind_1m
    
    def test_small_height_ratio(self):
        """Test adjustment with small height ratio."""
        # Adjusting from 100m to 1m
        wind_100m = 10.0
        adjusted = WindAdjustment.adjust_for_height(wind_100m, 100.0, 1.0)
        
        expected = 10.0 * (0.01 ** 0.15)
        assert abs(adjusted - expected) < 1e-6
        assert adjusted < wind_100m
