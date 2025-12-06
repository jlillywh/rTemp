"""
Unit tests for unit conversion utilities.

Tests all conversion methods in the UnitConversions class to ensure
correct conversion factors and numerical precision.
"""

import math
import pytest

from rtemp.utils.conversions import UnitConversions


class TestUnitConversions:
    """Test suite for UnitConversions class."""

    def test_watts_m2_to_cal_cm2_day(self):
        """Test conversion from W/m² to cal/(cm²·day)."""
        # Test zero
        assert UnitConversions.watts_m2_to_cal_cm2_day(0.0) == 0.0
        
        # Test positive value
        result = UnitConversions.watts_m2_to_cal_cm2_day(100.0)
        assert result == pytest.approx(206.56, rel=0.01)
        
        # Test negative value (heat loss)
        result = UnitConversions.watts_m2_to_cal_cm2_day(-50.0)
        assert result == pytest.approx(-103.28, rel=0.01)

    def test_cal_cm2_day_to_watts_m2(self):
        """Test conversion from cal/(cm²·day) to W/m²."""
        # Test zero
        assert UnitConversions.cal_cm2_day_to_watts_m2(0.0) == 0.0
        
        # Test positive value
        result = UnitConversions.cal_cm2_day_to_watts_m2(206.56)
        assert result == pytest.approx(100.0, rel=0.01)
        
        # Test negative value
        result = UnitConversions.cal_cm2_day_to_watts_m2(-103.28)
        assert result == pytest.approx(-50.0, rel=0.01)

    def test_heat_flux_round_trip(self):
        """Test round-trip conversion for heat flux."""
        original = 250.5
        converted = UnitConversions.watts_m2_to_cal_cm2_day(original)
        back = UnitConversions.cal_cm2_day_to_watts_m2(converted)
        assert back == pytest.approx(original, rel=1e-10)

    def test_deg_to_rad(self):
        """Test conversion from degrees to radians."""
        # Test zero
        assert UnitConversions.deg_to_rad(0.0) == 0.0
        
        # Test 180 degrees = pi radians
        result = UnitConversions.deg_to_rad(180.0)
        assert result == pytest.approx(math.pi, rel=1e-10)
        
        # Test 90 degrees = pi/2 radians
        result = UnitConversions.deg_to_rad(90.0)
        assert result == pytest.approx(math.pi / 2, rel=1e-10)
        
        # Test 360 degrees = 2*pi radians
        result = UnitConversions.deg_to_rad(360.0)
        assert result == pytest.approx(2 * math.pi, rel=1e-10)

    def test_rad_to_deg(self):
        """Test conversion from radians to degrees."""
        # Test zero
        assert UnitConversions.rad_to_deg(0.0) == 0.0
        
        # Test pi radians = 180 degrees
        result = UnitConversions.rad_to_deg(math.pi)
        assert result == pytest.approx(180.0, rel=1e-10)
        
        # Test pi/2 radians = 90 degrees
        result = UnitConversions.rad_to_deg(math.pi / 2)
        assert result == pytest.approx(90.0, rel=1e-10)
        
        # Test 2*pi radians = 360 degrees
        result = UnitConversions.rad_to_deg(2 * math.pi)
        assert result == pytest.approx(360.0, rel=1e-10)

    def test_angle_round_trip(self):
        """Test round-trip conversion for angles."""
        original = 45.7
        converted = UnitConversions.deg_to_rad(original)
        back = UnitConversions.rad_to_deg(converted)
        assert back == pytest.approx(original, rel=1e-10)

    def test_celsius_to_kelvin(self):
        """Test conversion from Celsius to Kelvin."""
        # Test absolute zero
        result = UnitConversions.celsius_to_kelvin(-273.15)
        assert result == pytest.approx(0.0, abs=1e-10)
        
        # Test freezing point of water
        result = UnitConversions.celsius_to_kelvin(0.0)
        assert result == pytest.approx(273.15, rel=1e-10)
        
        # Test boiling point of water
        result = UnitConversions.celsius_to_kelvin(100.0)
        assert result == pytest.approx(373.15, rel=1e-10)
        
        # Test typical water temperature
        result = UnitConversions.celsius_to_kelvin(20.0)
        assert result == pytest.approx(293.15, rel=1e-10)

    def test_kelvin_to_celsius(self):
        """Test conversion from Kelvin to Celsius."""
        # Test absolute zero
        result = UnitConversions.kelvin_to_celsius(0.0)
        assert result == pytest.approx(-273.15, rel=1e-10)
        
        # Test freezing point of water
        result = UnitConversions.kelvin_to_celsius(273.15)
        assert result == pytest.approx(0.0, abs=1e-10)
        
        # Test boiling point of water
        result = UnitConversions.kelvin_to_celsius(373.15)
        assert result == pytest.approx(100.0, rel=1e-10)

    def test_temperature_round_trip(self):
        """Test round-trip conversion for temperature."""
        original = 25.5
        converted = UnitConversions.celsius_to_kelvin(original)
        back = UnitConversions.kelvin_to_celsius(converted)
        assert back == pytest.approx(original, rel=1e-10)

    def test_meters_to_centimeters(self):
        """Test conversion from meters to centimeters."""
        # Test zero
        assert UnitConversions.meters_to_centimeters(0.0) == 0.0
        
        # Test 1 meter = 100 cm
        assert UnitConversions.meters_to_centimeters(1.0) == 100.0
        
        # Test fractional meter
        assert UnitConversions.meters_to_centimeters(0.5) == 50.0
        
        # Test multiple meters
        assert UnitConversions.meters_to_centimeters(2.5) == 250.0

    def test_centimeters_to_meters(self):
        """Test conversion from centimeters to meters."""
        # Test zero
        assert UnitConversions.centimeters_to_meters(0.0) == 0.0
        
        # Test 100 cm = 1 meter
        assert UnitConversions.centimeters_to_meters(100.0) == 1.0
        
        # Test fractional centimeters
        assert UnitConversions.centimeters_to_meters(50.0) == 0.5
        
        # Test multiple centimeters
        assert UnitConversions.centimeters_to_meters(250.0) == 2.5

    def test_length_round_trip(self):
        """Test round-trip conversion for length."""
        original = 1.75
        converted = UnitConversions.meters_to_centimeters(original)
        back = UnitConversions.centimeters_to_meters(converted)
        assert back == pytest.approx(original, rel=1e-10)

    def test_m_s_to_mph(self):
        """Test conversion from m/s to mph."""
        # Test zero
        assert UnitConversions.m_s_to_mph(0.0) == 0.0
        
        # Test typical wind speed
        result = UnitConversions.m_s_to_mph(10.0)
        assert result == pytest.approx(22.369, rel=0.001)
        
        # Test another value
        result = UnitConversions.m_s_to_mph(5.0)
        assert result == pytest.approx(11.185, rel=0.001)

    def test_mph_to_m_s(self):
        """Test conversion from mph to m/s."""
        # Test zero
        assert UnitConversions.mph_to_m_s(0.0) == 0.0
        
        # Test typical wind speed
        result = UnitConversions.mph_to_m_s(22.369)
        assert result == pytest.approx(10.0, rel=0.001)
        
        # Test another value
        result = UnitConversions.mph_to_m_s(11.185)
        assert result == pytest.approx(5.0, rel=0.001)

    def test_wind_speed_round_trip(self):
        """Test round-trip conversion for wind speed."""
        original = 7.5
        converted = UnitConversions.m_s_to_mph(original)
        back = UnitConversions.mph_to_m_s(converted)
        assert back == pytest.approx(original, rel=1e-10)

    def test_w_m_c_to_cal_s_cm_c(self):
        """Test conversion of thermal conductivity from W/(m·°C) to cal/(s·cm·°C)."""
        # Test zero
        assert UnitConversions.w_m_c_to_cal_s_cm_c(0.0) == 0.0
        
        # Test typical water thermal conductivity (~0.6 W/(m·°C))
        result = UnitConversions.w_m_c_to_cal_s_cm_c(0.6)
        assert result == pytest.approx(0.001433, rel=0.001)

    def test_cal_s_cm_c_to_w_m_c(self):
        """Test conversion of thermal conductivity from cal/(s·cm·°C) to W/(m·°C)."""
        # Test zero
        assert UnitConversions.cal_s_cm_c_to_w_m_c(0.0) == 0.0
        
        # Test typical value
        result = UnitConversions.cal_s_cm_c_to_w_m_c(0.001433)
        assert result == pytest.approx(0.6, rel=0.001)

    def test_thermal_conductivity_round_trip(self):
        """Test round-trip conversion for thermal conductivity."""
        original = 0.58
        converted = UnitConversions.w_m_c_to_cal_s_cm_c(original)
        back = UnitConversions.cal_s_cm_c_to_w_m_c(converted)
        assert back == pytest.approx(original, rel=1e-10)
