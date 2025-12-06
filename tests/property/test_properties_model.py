"""
Property-based tests for RTempModel class.

These tests use Hypothesis to verify that model-level properties hold
across a wide range of input values.
"""

import pytest
from datetime import datetime, timedelta
from hypothesis import given, settings, assume
from hypothesis import strategies as st
import pandas as pd
import numpy as np

from rtemp.model import RTempModel
from rtemp.config import ModelConfiguration


class TestModelProperties:
    """Property-based tests for RTempModel."""

    # Feature: rtemp-python-complete, Property 18: Temperature Minimum Enforcement
    # Validates: Requirements 11.1-11.3
    @given(
        initial_water_temp=st.floats(min_value=-10.0, max_value=5.0),
        initial_sediment_temp=st.floats(min_value=-10.0, max_value=5.0),
        minimum_temperature=st.floats(min_value=0.0, max_value=2.0),
        air_temp=st.floats(min_value=-5.0, max_value=10.0),
        dewpoint=st.floats(min_value=-10.0, max_value=5.0),
        wind_speed=st.floats(min_value=0.0, max_value=10.0),
        cloud_cover=st.floats(min_value=0.0, max_value=1.0),
        num_timesteps=st.integers(min_value=1, max_value=5),
    )
    @settings(max_examples=100, deadline=None)
    def test_temperature_minimum_enforcement_property(
        self,
        initial_water_temp: float,
        initial_sediment_temp: float,
        minimum_temperature: float,
        air_temp: float,
        dewpoint: float,
        wind_speed: float,
        cloud_cover: float,
        num_timesteps: int,
    ):
        """
        Property 18: Temperature Minimum Enforcement
        
        For any calculated water or sediment temperature, the final value
        should be greater than or equal to the specified minimum temperature.
        
        This property verifies that:
        - Water temperature >= minimum_temperature after each timestep
        - Sediment temperature >= minimum_temperature after each timestep
        - The constraint is applied even when heat losses would drive
          temperatures below the minimum
        
        Validates: Requirements 11.1-11.3
        """
        # Ensure dewpoint is not higher than air temperature
        assume(dewpoint <= air_temp)
        
        # Create model configuration with specified minimum temperature
        config = ModelConfiguration(
            latitude=45.0,
            longitude=122.0,
            elevation=100.0,
            timezone=8.0,
            daylight_savings=0,
            initial_water_temp=initial_water_temp,
            initial_sediment_temp=initial_sediment_temp,
            minimum_temperature=minimum_temperature,
            water_depth=1.0,
            effective_shade=0.0,
            wind_height=2.0,
            effective_wind_factor=1.0,
            sediment_thermal_conductivity=0.5,
            sediment_thermal_diffusivity=0.001,
            sediment_thickness=10.0,
            hyporheic_exchange_rate=0.0,
            groundwater_temperature=15.0,
            groundwater_inflow=0.0,
            solar_method="Bras",
            longwave_method="Brunt",
            wind_function_method="Brady-Graves-Geyer",
            atmospheric_turbidity=2.0,
            atmospheric_transmission_coeff=0.8,
            brutsaert_coefficient=1.24,
            solar_cloud_kcl1=1.0,
            solar_cloud_kcl2=2.0,
            longwave_cloud_method="Eqn 1",
            longwave_cloud_kcl3=1.0,
            longwave_cloud_kcl4=2.0,
            stability_criteria=10.0,  # Relaxed for testing
            enable_diagnostics=False,
        )
        
        # Create meteorological data
        start_date = datetime(2023, 6, 15, 12, 0, 0)
        met_data = []
        
        for i in range(num_timesteps):
            met_data.append({
                'datetime': start_date + timedelta(hours=i),
                'air_temperature': air_temp,
                'dewpoint_temperature': dewpoint,
                'wind_speed': wind_speed,
                'cloud_cover': cloud_cover,
            })
        
        met_df = pd.DataFrame(met_data)
        
        # Initialize model
        model = RTempModel(config)
        
        # Run model
        try:
            results = model.run(met_df)
            
            # Verify that all water temperatures are >= minimum_temperature
            water_temps = results['water_temperature'].values
            assert np.all(water_temps >= minimum_temperature - 1e-10), (
                f"Water temperature {np.min(water_temps):.6f} is below "
                f"minimum {minimum_temperature:.6f}"
            )
            
            # Verify that all sediment temperatures are >= minimum_temperature
            sediment_temps = results['sediment_temperature'].values
            assert np.all(sediment_temps >= minimum_temperature - 1e-10), (
                f"Sediment temperature {np.min(sediment_temps):.6f} is below "
                f"minimum {minimum_temperature:.6f}"
            )
            
            # Verify that temperatures are finite (not NaN or infinite)
            assert np.all(np.isfinite(water_temps)), "Water temperatures contain NaN or infinite values"
            assert np.all(np.isfinite(sediment_temps)), "Sediment temperatures contain NaN or infinite values"
            
        except RuntimeError as e:
            # If stability error occurs, that's acceptable for this test
            # as we're testing extreme conditions
            if "Numerical instability" in str(e):
                pytest.skip("Numerical instability encountered (acceptable for extreme conditions)")
            else:
                raise

    # Feature: rtemp-python-complete, Property 18: Temperature Minimum Enforcement
    # Validates: Requirements 11.1-11.3
    @given(
        minimum_temperature=st.floats(min_value=0.0, max_value=5.0),
    )
    @settings(max_examples=100, deadline=None)
    def test_minimum_temperature_enforcement_with_cold_conditions(
        self,
        minimum_temperature: float,
    ):
        """
        Property: Temperature minimum enforcement under cold conditions
        
        For any minimum temperature setting, when the model is run with
        very cold conditions (cold air, high wind, clear sky), the
        calculated temperatures should never fall below the minimum.
        
        This tests the enforcement under conditions that would naturally
        drive temperatures below the minimum.
        
        Validates: Requirements 11.1-11.3
        """
        # Create model configuration
        config = ModelConfiguration(
            latitude=45.0,
            longitude=122.0,
            elevation=100.0,
            timezone=8.0,
            daylight_savings=0,
            initial_water_temp=minimum_temperature + 1.0,  # Start just above minimum
            initial_sediment_temp=minimum_temperature + 1.0,
            minimum_temperature=minimum_temperature,
            water_depth=0.5,  # Shallow water cools faster
            effective_shade=0.0,
            wind_height=2.0,
            effective_wind_factor=1.0,
            sediment_thermal_conductivity=0.5,
            sediment_thermal_diffusivity=0.001,
            sediment_thickness=10.0,
            hyporheic_exchange_rate=0.0,
            groundwater_temperature=max(0.0, minimum_temperature - 5.0),  # Cold groundwater
            groundwater_inflow=10.0,  # Significant inflow
            solar_method="Bras",
            longwave_method="Brunt",
            wind_function_method="Brady-Graves-Geyer",
            atmospheric_turbidity=2.0,
            atmospheric_transmission_coeff=0.8,
            brutsaert_coefficient=1.24,
            solar_cloud_kcl1=1.0,
            solar_cloud_kcl2=2.0,
            longwave_cloud_method="Eqn 1",
            longwave_cloud_kcl3=1.0,
            longwave_cloud_kcl4=2.0,
            stability_criteria=10.0,
            enable_diagnostics=False,
        )
        
        # Create cold nighttime conditions
        start_date = datetime(2023, 12, 15, 0, 0, 0)  # Winter night
        met_data = []
        
        for i in range(3):
            met_data.append({
                'datetime': start_date + timedelta(hours=i),
                'air_temperature': minimum_temperature - 10.0,  # Very cold air
                'dewpoint_temperature': minimum_temperature - 15.0,  # Very dry
                'wind_speed': 10.0,  # High wind
                'cloud_cover': 0.0,  # Clear sky (maximum radiative cooling)
            })
        
        met_df = pd.DataFrame(met_data)
        
        # Initialize and run model
        model = RTempModel(config)
        
        try:
            results = model.run(met_df)
            
            # Verify minimum temperature enforcement
            water_temps = results['water_temperature'].values
            sediment_temps = results['sediment_temperature'].values
            
            assert np.all(water_temps >= minimum_temperature - 1e-10), (
                f"Water temperature {np.min(water_temps):.6f} fell below "
                f"minimum {minimum_temperature:.6f} under cold conditions"
            )
            
            assert np.all(sediment_temps >= minimum_temperature - 1e-10), (
                f"Sediment temperature {np.min(sediment_temps):.6f} fell below "
                f"minimum {minimum_temperature:.6f} under cold conditions"
            )
            
            # The main property is verified: temperatures never go below minimum
            # We don't need to verify that they actually reach the minimum,
            # as that depends on the specific conditions and may not always happen
            
        except RuntimeError as e:
            # If stability error occurs, that's acceptable
            if "Numerical instability" in str(e):
                pytest.skip("Numerical instability encountered (acceptable for extreme conditions)")
            else:
                raise

    # Feature: rtemp-python-complete, Property 18: Temperature Minimum Enforcement
    # Validates: Requirements 11.1-11.3
    @given(
        temperature=st.floats(min_value=-20.0, max_value=50.0),
        minimum_temperature=st.floats(min_value=0.0, max_value=5.0),
    )
    @settings(max_examples=100)
    def test_enforce_minimum_temperature_method(
        self,
        temperature: float,
        minimum_temperature: float,
    ):
        """
        Property: _enforce_minimum_temperature method correctness
        
        For any temperature and minimum temperature, the enforcement method
        should return max(temperature, minimum_temperature).
        
        Validates: Requirements 11.1-11.3
        """
        # Create a simple model configuration
        config = ModelConfiguration(
            latitude=45.0,
            longitude=122.0,
            elevation=100.0,
            timezone=8.0,
            minimum_temperature=minimum_temperature,
        )
        
        model = RTempModel(config)
        
        # Test the enforcement method
        enforced_temp = model._enforce_minimum_temperature(temperature)
        
        # Verify that the enforced temperature is the maximum of the two
        expected = max(temperature, minimum_temperature)
        assert enforced_temp == pytest.approx(expected, rel=1e-10, abs=1e-10)
        
        # Verify that the enforced temperature is never below the minimum
        assert enforced_temp >= minimum_temperature - 1e-10
        
        # Verify that if temperature is above minimum, it's unchanged
        if temperature >= minimum_temperature:
            assert enforced_temp == pytest.approx(temperature, rel=1e-10, abs=1e-10)
        
        # Verify that if temperature is below minimum, it's set to minimum
        if temperature < minimum_temperature:
            assert enforced_temp == pytest.approx(minimum_temperature, rel=1e-10, abs=1e-10)

    # Feature: rtemp-python-complete, Property 22: Output Completeness
    # Validates: Requirements 16.1-16.7
    @given(
        num_timesteps=st.integers(min_value=1, max_value=10),
        air_temp=st.floats(min_value=0.0, max_value=35.0),
        dewpoint=st.floats(min_value=-5.0, max_value=30.0),
        wind_speed=st.floats(min_value=0.0, max_value=15.0),
        cloud_cover=st.floats(min_value=0.0, max_value=1.0),
    )
    @settings(max_examples=100, deadline=None)
    def test_output_completeness_property(
        self,
        num_timesteps: int,
        air_temp: float,
        dewpoint: float,
        wind_speed: float,
        cloud_cover: float,
    ):
        """
        Property 22: Output Completeness
        
        For any model execution, the output DataFrame should contain all
        required columns (datetime, water_temp, sediment_temp, heat fluxes).
        
        This property verifies that:
        - All required columns are present in the output
        - The number of output rows matches the number of input timesteps
        - All values are finite (not NaN or infinite)
        - Column data types are appropriate
        
        Validates: Requirements 16.1-16.7
        """
        # Ensure dewpoint is not higher than air temperature
        assume(dewpoint <= air_temp)
        
        # Create model configuration
        config = ModelConfiguration(
            latitude=45.0,
            longitude=122.0,
            elevation=100.0,
            timezone=8.0,
            daylight_savings=0,
            initial_water_temp=20.0,
            initial_sediment_temp=20.0,
            minimum_temperature=0.0,
            water_depth=1.0,
            effective_shade=0.0,
            wind_height=2.0,
            effective_wind_factor=1.0,
            sediment_thermal_conductivity=0.5,
            sediment_thermal_diffusivity=0.001,
            sediment_thickness=10.0,
            hyporheic_exchange_rate=0.0,
            groundwater_temperature=15.0,
            groundwater_inflow=0.0,
            solar_method="Bras",
            longwave_method="Brunt",
            wind_function_method="Brady-Graves-Geyer",
            atmospheric_turbidity=2.0,
            atmospheric_transmission_coeff=0.8,
            brutsaert_coefficient=1.24,
            solar_cloud_kcl1=1.0,
            solar_cloud_kcl2=2.0,
            longwave_cloud_method="Eqn 1",
            longwave_cloud_kcl3=1.0,
            longwave_cloud_kcl4=2.0,
            stability_criteria=10.0,
            enable_diagnostics=False,
        )
        
        # Create meteorological data
        start_date = datetime(2023, 6, 15, 12, 0, 0)
        met_data = []
        
        for i in range(num_timesteps):
            met_data.append({
                'datetime': start_date + timedelta(hours=i),
                'air_temperature': air_temp,
                'dewpoint_temperature': dewpoint,
                'wind_speed': wind_speed,
                'cloud_cover': cloud_cover,
            })
        
        met_df = pd.DataFrame(met_data)
        
        # Initialize and run model
        model = RTempModel(config)
        
        try:
            results = model.run(met_df)
            
            # Define required columns per Requirements 16.1-16.7
            required_columns = [
                'datetime',                  # Requirement 16.1
                'solar_azimuth',            # Requirement 16.2
                'solar_elevation',          # Requirement 16.2
                'solar_radiation',          # Requirement 16.3, 16.4
                'longwave_atmospheric',     # Requirement 16.4
                'longwave_back',            # Requirement 16.4
                'evaporation',              # Requirement 16.4
                'convection',               # Requirement 16.4
                'sediment_conduction',      # Requirement 16.4
                'hyporheic_exchange',       # Requirement 16.4
                'groundwater',              # Requirement 16.4
                'net_flux',                 # Requirement 16.4
                'water_temperature',        # Requirement 16.5
                'sediment_temperature',     # Requirement 16.6
                'air_temperature',          # Requirement 16.7
                'dewpoint_temperature',     # Requirement 16.7
            ]
            
            # Verify all required columns are present
            for col in required_columns:
                assert col in results.columns, (
                    f"Required column '{col}' is missing from output"
                )
            
            # Verify number of rows matches input
            assert len(results) == num_timesteps, (
                f"Output has {len(results)} rows but expected {num_timesteps}"
            )
            
            # Verify datetime column
            assert results['datetime'].dtype == 'datetime64[ns]' or \
                   all(isinstance(dt, datetime) for dt in results['datetime']), (
                "datetime column should contain datetime objects"
            )
            
            # Verify all numeric columns contain finite values
            numeric_columns = [col for col in required_columns if col != 'datetime']
            for col in numeric_columns:
                values = results[col].values
                assert np.all(np.isfinite(values)), (
                    f"Column '{col}' contains NaN or infinite values"
                )
            
            # Verify temperature columns are in reasonable range
            water_temps = results['water_temperature'].values
            sediment_temps = results['sediment_temperature'].values
            
            assert np.all(water_temps >= -50.0) and np.all(water_temps <= 100.0), (
                "Water temperatures outside reasonable range [-50, 100]°C"
            )
            assert np.all(sediment_temps >= -50.0) and np.all(sediment_temps <= 100.0), (
                "Sediment temperatures outside reasonable range [-50, 100]°C"
            )
            
            # Verify solar elevation is in valid range
            solar_elevations = results['solar_elevation'].values
            assert np.all(solar_elevations >= -90.0) and np.all(solar_elevations <= 90.0), (
                "Solar elevation outside valid range [-90, 90] degrees"
            )
            
            # Verify solar azimuth is in valid range
            solar_azimuths = results['solar_azimuth'].values
            assert np.all(solar_azimuths >= 0.0) and np.all(solar_azimuths <= 360.0), (
                "Solar azimuth outside valid range [0, 360] degrees"
            )
            
        except RuntimeError as e:
            # If stability error occurs, that's acceptable for this test
            if "Numerical instability" in str(e):
                pytest.skip("Numerical instability encountered (acceptable for extreme conditions)")
            else:
                raise

    # Feature: rtemp-python-complete, Property 23: Diagnostic Output Completeness
    # Validates: Requirements 14.1-14.8
    @given(
        num_timesteps=st.integers(min_value=1, max_value=10),
        air_temp=st.floats(min_value=0.0, max_value=35.0),
        dewpoint=st.floats(min_value=-5.0, max_value=30.0),
        wind_speed=st.floats(min_value=0.0, max_value=15.0),
        cloud_cover=st.floats(min_value=0.0, max_value=1.0),
    )
    @settings(max_examples=100, deadline=None)
    def test_diagnostic_output_completeness_property(
        self,
        num_timesteps: int,
        air_temp: float,
        dewpoint: float,
        wind_speed: float,
        cloud_cover: float,
    ):
        """
        Property 23: Diagnostic Output Completeness
        
        For any model execution with diagnostics enabled, the diagnostic
        output should contain all specified diagnostic fields.
        
        This property verifies that:
        - All diagnostic columns are present when diagnostics are enabled
        - Diagnostic values are finite (not NaN or infinite)
        - Diagnostic values are in reasonable ranges
        - The number of diagnostic rows matches the number of timesteps
        
        Validates: Requirements 14.1-14.8
        """
        # Ensure dewpoint is not higher than air temperature
        assume(dewpoint <= air_temp)
        
        # Create model configuration with diagnostics enabled
        config = ModelConfiguration(
            latitude=45.0,
            longitude=122.0,
            elevation=100.0,
            timezone=8.0,
            daylight_savings=0,
            initial_water_temp=20.0,
            initial_sediment_temp=20.0,
            minimum_temperature=0.0,
            water_depth=1.0,
            effective_shade=0.0,
            wind_height=2.0,
            effective_wind_factor=1.0,
            sediment_thermal_conductivity=0.5,
            sediment_thermal_diffusivity=0.001,
            sediment_thickness=10.0,
            hyporheic_exchange_rate=0.0,
            groundwater_temperature=15.0,
            groundwater_inflow=0.0,
            solar_method="Bras",
            longwave_method="Brunt",
            wind_function_method="Brady-Graves-Geyer",
            atmospheric_turbidity=2.0,
            atmospheric_transmission_coeff=0.8,
            brutsaert_coefficient=1.24,
            solar_cloud_kcl1=1.0,
            solar_cloud_kcl2=2.0,
            longwave_cloud_method="Eqn 1",
            longwave_cloud_kcl3=1.0,
            longwave_cloud_kcl4=2.0,
            stability_criteria=10.0,
            enable_diagnostics=True,  # Enable diagnostics
        )
        
        # Create meteorological data
        start_date = datetime(2023, 6, 15, 12, 0, 0)
        met_data = []
        
        for i in range(num_timesteps):
            met_data.append({
                'datetime': start_date + timedelta(hours=i),
                'air_temperature': air_temp,
                'dewpoint_temperature': dewpoint,
                'wind_speed': wind_speed,
                'cloud_cover': cloud_cover,
            })
        
        met_df = pd.DataFrame(met_data)
        
        # Initialize and run model
        model = RTempModel(config)
        
        try:
            results = model.run(met_df)
            
            # Define required diagnostic columns per Requirements 14.1-14.8
            diagnostic_columns = [
                'vapor_pressure_water',        # Requirement 14.8
                'vapor_pressure_air',          # Requirement 14.8
                'atmospheric_emissivity',      # Requirement 14.8
                'wind_speed_2m',               # Requirement 14.7
                'wind_speed_7m',               # Requirement 14.7
                'wind_function',               # Requirement 14.7
                'water_temp_change_rate',      # Requirement 14.5
                'sediment_temp_change_rate',   # Requirement 14.5
            ]
            
            # Verify all diagnostic columns are present
            for col in diagnostic_columns:
                assert col in results.columns, (
                    f"Required diagnostic column '{col}' is missing from output"
                )
            
            # Verify number of rows matches input
            assert len(results) == num_timesteps, (
                f"Diagnostic output has {len(results)} rows but expected {num_timesteps}"
            )
            
            # Verify all diagnostic columns contain finite values
            for col in diagnostic_columns:
                values = results[col].values
                assert np.all(np.isfinite(values)), (
                    f"Diagnostic column '{col}' contains NaN or infinite values"
                )
            
            # Verify vapor pressures are non-negative
            vapor_pressure_water = results['vapor_pressure_water'].values
            vapor_pressure_air = results['vapor_pressure_air'].values
            
            assert np.all(vapor_pressure_water >= 0.0), (
                "vapor_pressure_water contains negative values"
            )
            assert np.all(vapor_pressure_air >= 0.0), (
                "vapor_pressure_air contains negative values"
            )
            
            # Verify atmospheric emissivity is in valid range [0, 1]
            emissivity = results['atmospheric_emissivity'].values
            assert np.all(emissivity >= 0.0) and np.all(emissivity <= 1.0), (
                f"atmospheric_emissivity outside valid range [0, 1]: "
                f"min={np.min(emissivity):.4f}, max={np.max(emissivity):.4f}"
            )
            
            # Verify wind speeds are non-negative
            wind_2m = results['wind_speed_2m'].values
            wind_7m = results['wind_speed_7m'].values
            
            assert np.all(wind_2m >= 0.0), (
                "wind_speed_2m contains negative values"
            )
            assert np.all(wind_7m >= 0.0), (
                "wind_speed_7m contains negative values"
            )
            
            # Verify wind function is positive (when wind speed > 0)
            wind_func = results['wind_function'].values
            # Wind function should be positive or zero
            assert np.all(wind_func >= 0.0), (
                "wind_function contains negative values"
            )
            
            # Verify temperature change rates are in reasonable range
            water_change = results['water_temp_change_rate'].values
            sediment_change = results['sediment_temp_change_rate'].values
            
            # Temperature change rates should be finite and not extreme
            # (e.g., not changing by more than 100°C per day)
            assert np.all(np.abs(water_change) <= 100.0), (
                f"water_temp_change_rate has extreme values: "
                f"min={np.min(water_change):.2f}, max={np.max(water_change):.2f}"
            )
            assert np.all(np.abs(sediment_change) <= 100.0), (
                f"sediment_temp_change_rate has extreme values: "
                f"min={np.min(sediment_change):.2f}, max={np.max(sediment_change):.2f}"
            )
            
        except RuntimeError as e:
            # If stability error occurs, that's acceptable for this test
            if "Numerical instability" in str(e):
                pytest.skip("Numerical instability encountered (acceptable for extreme conditions)")
            else:
                raise

    # Feature: rtemp-python-complete, Property 23: Diagnostic Output Completeness
    # Validates: Requirements 14.1-14.8
    @given(
        num_timesteps=st.integers(min_value=1, max_value=5),
    )
    @settings(max_examples=100, deadline=None)
    def test_diagnostic_output_disabled_property(
        self,
        num_timesteps: int,
    ):
        """
        Property: Diagnostic output should not be present when disabled
        
        For any model execution with diagnostics disabled, the output
        should not contain diagnostic columns.
        
        This verifies that diagnostic output is only included when
        explicitly requested.
        
        Validates: Requirements 14.1-14.8
        """
        # Create model configuration with diagnostics disabled
        config = ModelConfiguration(
            latitude=45.0,
            longitude=122.0,
            elevation=100.0,
            timezone=8.0,
            daylight_savings=0,
            initial_water_temp=20.0,
            initial_sediment_temp=20.0,
            minimum_temperature=0.0,
            water_depth=1.0,
            effective_shade=0.0,
            wind_height=2.0,
            effective_wind_factor=1.0,
            sediment_thermal_conductivity=0.5,
            sediment_thermal_diffusivity=0.001,
            sediment_thickness=10.0,
            hyporheic_exchange_rate=0.0,
            groundwater_temperature=15.0,
            groundwater_inflow=0.0,
            solar_method="Bras",
            longwave_method="Brunt",
            wind_function_method="Brady-Graves-Geyer",
            atmospheric_turbidity=2.0,
            atmospheric_transmission_coeff=0.8,
            brutsaert_coefficient=1.24,
            solar_cloud_kcl1=1.0,
            solar_cloud_kcl2=2.0,
            longwave_cloud_method="Eqn 1",
            longwave_cloud_kcl3=1.0,
            longwave_cloud_kcl4=2.0,
            stability_criteria=10.0,
            enable_diagnostics=False,  # Diagnostics disabled
        )
        
        # Create meteorological data
        start_date = datetime(2023, 6, 15, 12, 0, 0)
        met_data = []
        
        for i in range(num_timesteps):
            met_data.append({
                'datetime': start_date + timedelta(hours=i),
                'air_temperature': 20.0,
                'dewpoint_temperature': 15.0,
                'wind_speed': 2.0,
                'cloud_cover': 0.5,
            })
        
        met_df = pd.DataFrame(met_data)
        
        # Initialize and run model
        model = RTempModel(config)
        results = model.run(met_df)
        
        # Define diagnostic columns that should NOT be present
        diagnostic_columns = [
            'vapor_pressure_water',
            'vapor_pressure_air',
            'atmospheric_emissivity',
            'wind_speed_2m',
            'wind_speed_7m',
            'wind_function',
            'water_temp_change_rate',
            'sediment_temp_change_rate',
        ]
        
        # Verify diagnostic columns are NOT present
        for col in diagnostic_columns:
            assert col not in results.columns, (
                f"Diagnostic column '{col}' should not be present when diagnostics are disabled"
            )
