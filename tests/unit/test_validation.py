"""
Unit tests for input validation.

Tests the InputValidator class for site parameter validation,
meteorological data validation, and timestep checking.
"""

import pytest
import pandas as pd
from datetime import datetime, timedelta
from rtemp.utils.validation import InputValidator


class TestSiteParameterValidation:
    """Tests for site parameter validation."""
    
    def test_valid_parameters_pass_through(self):
        """Valid parameters should pass through unchanged."""
        params = {
            'water_depth': 1.5,
            'effective_shade': 0.3,
            'wind_height': 2.0,
            'effective_wind_factor': 0.8,
            'groundwater_temperature': 15.0,
            'groundwater_inflow': 5.0,
            'sediment_thermal_conductivity': 1.0,
            'sediment_thermal_diffusivity': 0.001,
            'sediment_thickness': 20.0,
            'hyporheic_exchange_rate': 2.0
        }
        
        validated, warnings = InputValidator.validate_site_parameters(params)
        
        assert validated == params
        assert len(warnings) == 0
    
    def test_water_depth_zero_raises_error(self):
        """Water depth of zero should raise ValueError."""
        params = {'water_depth': 0.0}
        
        with pytest.raises(ValueError, match="Water depth must be greater than zero"):
            InputValidator.validate_site_parameters(params)
    
    def test_water_depth_negative_raises_error(self):
        """Negative water depth should raise ValueError."""
        params = {'water_depth': -1.0}
        
        with pytest.raises(ValueError, match="Water depth must be greater than zero"):
            InputValidator.validate_site_parameters(params)
    
    def test_effective_shade_negative_raises_error(self):
        """Negative effective shade should raise ValueError."""
        params = {'effective_shade': -0.1}
        
        with pytest.raises(ValueError, match="Effective shade must be between 0 and 1"):
            InputValidator.validate_site_parameters(params)
    
    def test_effective_shade_greater_than_one_raises_error(self):
        """Effective shade > 1 should raise ValueError."""
        params = {'effective_shade': 1.5}
        
        with pytest.raises(ValueError, match="Effective shade must be between 0 and 1"):
            InputValidator.validate_site_parameters(params)
    
    def test_wind_height_zero_raises_error(self):
        """Wind height of zero should raise ValueError."""
        params = {'wind_height': 0.0}
        
        with pytest.raises(ValueError, match="Wind height must be greater than zero"):
            InputValidator.validate_site_parameters(params)
    
    def test_wind_height_negative_raises_error(self):
        """Negative wind height should raise ValueError."""
        params = {'wind_height': -2.0}
        
        with pytest.raises(ValueError, match="Wind height must be greater than zero"):
            InputValidator.validate_site_parameters(params)
    
    def test_effective_wind_factor_negative_raises_error(self):
        """Negative effective wind factor should raise ValueError."""
        params = {'effective_wind_factor': -0.5}
        
        with pytest.raises(ValueError, match="Effective wind factor must be greater than or equal to zero"):
            InputValidator.validate_site_parameters(params)
    
    def test_groundwater_temperature_negative_raises_error(self):
        """Negative groundwater temperature should raise ValueError."""
        params = {'groundwater_temperature': -5.0}
        
        with pytest.raises(ValueError, match="Groundwater temperature must be greater than or equal to zero"):
            InputValidator.validate_site_parameters(params)
    
    def test_negative_groundwater_inflow_corrected(self):
        """Negative groundwater inflow should be set to zero with warning."""
        params = {'groundwater_inflow': -2.0}
        
        validated, warnings = InputValidator.validate_site_parameters(params)
        
        assert validated['groundwater_inflow'] == 0.0
        assert len(warnings) == 1
        assert "Groundwater inflow was negative" in warnings[0]
    
    def test_negative_sediment_conductivity_corrected(self):
        """Negative sediment thermal conductivity should be set to zero with warning."""
        params = {'sediment_thermal_conductivity': -1.0}
        
        validated, warnings = InputValidator.validate_site_parameters(params)
        
        assert validated['sediment_thermal_conductivity'] == 0.0
        assert len(warnings) == 1
        assert "Sediment thermal conductivity was negative" in warnings[0]
    
    def test_zero_sediment_diffusivity_corrected(self):
        """Zero sediment thermal diffusivity should be set to water value with warning."""
        params = {'sediment_thermal_diffusivity': 0.0}
        
        validated, warnings = InputValidator.validate_site_parameters(params)
        
        assert validated['sediment_thermal_diffusivity'] == 0.0014
        assert len(warnings) == 1
        assert "assumed equal to water properties" in warnings[0]
    
    def test_negative_sediment_diffusivity_corrected(self):
        """Negative sediment thermal diffusivity should be set to water value with warning."""
        params = {'sediment_thermal_diffusivity': -0.001}
        
        validated, warnings = InputValidator.validate_site_parameters(params)
        
        assert validated['sediment_thermal_diffusivity'] == 0.0014
        assert len(warnings) == 1
        assert "assumed equal to water properties" in warnings[0]
    
    def test_zero_sediment_thickness_corrected(self):
        """Zero sediment thickness should be set to 10 cm with warning."""
        params = {'sediment_thickness': 0.0}
        
        validated, warnings = InputValidator.validate_site_parameters(params)
        
        assert validated['sediment_thickness'] == 10.0
        assert len(warnings) == 1
        assert "set to 10 cm" in warnings[0]
    
    def test_negative_sediment_thickness_corrected(self):
        """Negative sediment thickness should be set to 10 cm with warning."""
        params = {'sediment_thickness': -5.0}
        
        validated, warnings = InputValidator.validate_site_parameters(params)
        
        assert validated['sediment_thickness'] == 10.0
        assert len(warnings) == 1
        assert "set to 10 cm" in warnings[0]
    
    def test_negative_hyporheic_exchange_corrected(self):
        """Negative hyporheic exchange should be set to zero with warning."""
        params = {'hyporheic_exchange_rate': -1.5}
        
        validated, warnings = InputValidator.validate_site_parameters(params)
        
        assert validated['hyporheic_exchange_rate'] == 0.0
        assert len(warnings) == 1
        assert "Hyporheic exchange rate was negative" in warnings[0]
    
    def test_multiple_corrections(self):
        """Multiple invalid parameters should all be corrected with multiple warnings."""
        params = {
            'groundwater_inflow': -2.0,
            'sediment_thermal_conductivity': -1.0,
            'sediment_thickness': 0.0
        }
        
        validated, warnings = InputValidator.validate_site_parameters(params)
        
        assert validated['groundwater_inflow'] == 0.0
        assert validated['sediment_thermal_conductivity'] == 0.0
        assert validated['sediment_thickness'] == 10.0
        assert len(warnings) == 3


class TestMeteorologicalDataValidation:
    """Tests for meteorological data validation."""
    
    def test_valid_data_passes_through(self):
        """Valid meteorological data should pass through unchanged."""
        data = pd.DataFrame({
            'air_temperature': [20.0, 22.0, 24.0],
            'dewpoint_temperature': [15.0, 16.0, 17.0],
            'wind_speed': [2.0, 3.0, 2.5],
            'cloud_cover': [0.3, 0.5, 0.2]
        })
        
        validated, warnings = InputValidator.validate_meteorological_data(data)
        
        pd.testing.assert_frame_equal(validated, data)
        assert len(warnings) == 0
    
    def test_missing_air_temperature_corrected(self):
        """Missing air temperature (≤ -999) should be set to 20°C."""
        data = pd.DataFrame({
            'air_temperature': [20.0, -999.0, -1000.0],
            'dewpoint_temperature': [15.0, 16.0, 17.0]
        })
        
        validated, warnings = InputValidator.validate_meteorological_data(data)
        
        assert validated['air_temperature'].tolist() == [20.0, 20.0, 20.0]
        assert len(warnings) == 1
        assert "Air temperature missing for 2 timestep(s)" in warnings[0]
    
    def test_missing_dewpoint_corrected(self):
        """Missing dewpoint temperature (≤ -999) should be set to 10°C."""
        data = pd.DataFrame({
            'air_temperature': [20.0, 22.0, 24.0],
            'dewpoint_temperature': [15.0, -999.0, -1000.0]
        })
        
        validated, warnings = InputValidator.validate_meteorological_data(data)
        
        assert validated['dewpoint_temperature'].tolist() == [15.0, 10.0, 10.0]
        assert len(warnings) == 1
        assert "Dewpoint temperature missing for 2 timestep(s)" in warnings[0]
    
    def test_negative_wind_speed_corrected(self):
        """Negative wind speed should be set to zero."""
        data = pd.DataFrame({
            'wind_speed': [2.0, -1.0, 3.0, -0.5]
        })
        
        validated, warnings = InputValidator.validate_meteorological_data(data)
        
        assert validated['wind_speed'].tolist() == [2.0, 0.0, 3.0, 0.0]
        assert len(warnings) == 1
        assert "Wind speed was negative for 2 timestep(s)" in warnings[0]
    
    def test_negative_cloud_cover_corrected(self):
        """Negative cloud cover should be set to zero."""
        data = pd.DataFrame({
            'cloud_cover': [0.3, -0.1, 0.5, -0.2]
        })
        
        validated, warnings = InputValidator.validate_meteorological_data(data)
        
        assert validated['cloud_cover'].tolist() == [0.3, 0.0, 0.5, 0.0]
        assert len(warnings) == 1
        assert "Cloud cover was negative for 2 timestep(s)" in warnings[0]
    
    def test_excessive_cloud_cover_corrected(self):
        """Cloud cover > 1 should be set to 1."""
        data = pd.DataFrame({
            'cloud_cover': [0.3, 1.5, 0.5, 2.0]
        })
        
        validated, warnings = InputValidator.validate_meteorological_data(data)
        
        assert validated['cloud_cover'].tolist() == [0.3, 1.0, 0.5, 1.0]
        assert len(warnings) == 1
        assert "Cloud cover was greater than 1 for 2 timestep(s)" in warnings[0]
    
    def test_multiple_issues_corrected(self):
        """Multiple data quality issues should all be corrected."""
        data = pd.DataFrame({
            'air_temperature': [20.0, -999.0],
            'dewpoint_temperature': [15.0, -999.0],
            'wind_speed': [2.0, -1.0],
            'cloud_cover': [0.3, 1.5]
        })
        
        validated, warnings = InputValidator.validate_meteorological_data(data)
        
        assert validated['air_temperature'].tolist() == [20.0, 20.0]
        assert validated['dewpoint_temperature'].tolist() == [15.0, 10.0]
        assert validated['wind_speed'].tolist() == [2.0, 0.0]
        assert validated['cloud_cover'].tolist() == [0.3, 1.0]
        assert len(warnings) == 4


class TestTimestepChecking:
    """Tests for timestep validation."""
    
    def test_normal_timestep_no_warning(self):
        """Normal timestep (< 2 hours) should not generate warning."""
        current = datetime(2024, 1, 1, 12, 0)
        previous = datetime(2024, 1, 1, 11, 0)
        
        warning, timestep = InputValidator.check_timestep(current, previous)
        
        assert warning is None
        assert timestep == 1.0 / 24.0  # 1 hour in days
    
    def test_timestep_greater_than_2_hours_warning(self):
        """Timestep > 2 hours should generate warning."""
        current = datetime(2024, 1, 1, 15, 0)
        previous = datetime(2024, 1, 1, 12, 0)
        
        warning, timestep = InputValidator.check_timestep(current, previous)
        
        assert warning is not None
        assert "Timestep greater than 2 hours" in warning
        assert "3.00 hours" in warning
        assert timestep == 3.0 / 24.0
    
    def test_timestep_greater_than_4_hours_severe_warning(self):
        """Timestep > 4 hours should generate more severe warning."""
        current = datetime(2024, 1, 1, 17, 0)
        previous = datetime(2024, 1, 1, 12, 0)
        
        warning, timestep = InputValidator.check_timestep(current, previous)
        
        assert warning is not None
        assert "Large timestep detected" in warning
        assert "5.00 hours" in warning
        assert "resetting temperatures" in warning
        assert timestep == 5.0 / 24.0
    
    def test_zero_timestep_warning(self):
        """Zero timestep (duplicate data) should generate warning."""
        current = datetime(2024, 1, 1, 12, 0)
        previous = datetime(2024, 1, 1, 12, 0)
        
        warning, timestep = InputValidator.check_timestep(current, previous)
        
        assert warning is not None
        assert "Duplicate timestep" in warning
        assert timestep == 0.0
    
    def test_negative_timestep_warning(self):
        """Negative timestep (time going backwards) should generate warning."""
        current = datetime(2024, 1, 1, 11, 0)
        previous = datetime(2024, 1, 1, 12, 0)
        
        warning, timestep = InputValidator.check_timestep(current, previous)
        
        assert warning is not None
        assert "negative" in warning.lower()
        assert timestep < 0
    
    def test_small_timestep_no_warning(self):
        """Small timestep (minutes) should not generate warning."""
        current = datetime(2024, 1, 1, 12, 15)
        previous = datetime(2024, 1, 1, 12, 0)
        
        warning, timestep = InputValidator.check_timestep(current, previous)
        
        assert warning is None
        assert timestep == 15.0 / (24.0 * 60.0)  # 15 minutes in days
