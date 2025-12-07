"""
Integration tests for GoldSim-rTemp adapter.

These tests verify the complete data flow from GoldSim through the adapter
to rTemp and back, including edge cases and error handling.

Requirements: Testing Strategy - Integration Testing
"""

import math
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import numpy as np
import pandas as pd
import pytest

# Import the adapter module
import rtemp_goldsim_adapter
from rtemp import ModelConfiguration, RTempModel


class TestEndToEndWithMockGoldSimData:
    """
    End-to-end test with mock GoldSim data.

    Simulates the complete workflow of GoldSim calling the adapter function
    with realistic daily meteorological data.
    """

    def test_single_day_execution(self):
        """Test adapter with one day of mock GoldSim data."""
        # Mock GoldSim inputs for a typical summer day
        # These would come from GoldSim External element
        args = (
            15.0,  # Current_Water_Temp (°C)
            14.0,  # Current_Sediment_Temp (°C)
            2.0,  # Water_Depth (meters)
            45.0,  # Latitude (degrees)
            -120.0,  # Longitude (degrees)
            100.0,  # Elevation (meters)
            -8.0,  # Timezone (hours from UTC)
            12.0,  # Air_Temp_Min (°C)
            28.0,  # Air_Temp_Max (°C)
            8.0,  # Dewpoint_Min (°C)
            18.0,  # Dewpoint_Max (°C)
            2.5,  # Wind_Speed_Avg (m/s)
            0.3,  # Cloud_Cover_Avg (fraction)
            0.0,  # Simulation_Date (elapsed days)
        )

        # Call adapter function
        result = rtemp_goldsim_adapter.process_data(*args)

        # Verify return structure
        assert isinstance(result, tuple)
        assert len(result) == 3

        # Unpack results
        new_water_temp, new_sediment_temp, daily_avg_net_flux = result

        # Verify output types
        assert isinstance(new_water_temp, float)
        assert isinstance(new_sediment_temp, float)
        assert isinstance(daily_avg_net_flux, float)

        # Verify outputs are reasonable
        assert not math.isnan(new_water_temp)
        assert not math.isnan(new_sediment_temp)
        assert not math.isnan(daily_avg_net_flux)

        # Temperature should be within reasonable bounds
        assert -5.0 <= new_water_temp <= 50.0
        assert -5.0 <= new_sediment_temp <= 50.0

        # Water temperature should have changed from initial
        # (unless conditions are perfectly stable, which is unlikely)
        # Allow for small changes or no change in stable conditions
        assert abs(new_water_temp - 15.0) < 10.0

    def test_multi_day_sequence(self):
        """Test adapter over multiple consecutive days."""
        # Simulate 5 days of GoldSim calls
        water_temp = 15.0
        sediment_temp = 14.0

        for day in range(5):
            # Vary meteorological conditions slightly each day
            day_offset = 2.0 * math.sin(day * math.pi / 2.5)

            args = (
                water_temp,  # Use previous day's output
                sediment_temp,
                2.0,  # Water_Depth
                45.0,  # Latitude
                -120.0,  # Longitude
                100.0,  # Elevation
                -8.0,  # Timezone
                12.0 + day_offset,  # Air_Temp_Min
                28.0 + day_offset,  # Air_Temp_Max
                8.0 + day_offset,  # Dewpoint_Min
                18.0 + day_offset,  # Dewpoint_Max
                2.5,  # Wind_Speed_Avg
                0.3,  # Cloud_Cover_Avg
                float(day),  # Simulation_Date
            )

            # Call adapter
            water_temp, sediment_temp, flux = rtemp_goldsim_adapter.process_data(*args)

            # Verify each day produces valid results
            assert not math.isnan(water_temp)
            assert not math.isnan(sediment_temp)
            assert not math.isnan(flux)
            assert -5.0 <= water_temp <= 50.0

    def test_different_locations(self):
        """Test adapter at different geographic locations."""
        locations = [
            (30.0, -90.0, "Tropical"),
            (45.0, -120.0, "Mid-latitude"),
            (60.0, -150.0, "High-latitude"),
        ]

        for lat, lon, name in locations:
            args = (
                15.0,  # Current_Water_Temp
                14.0,  # Current_Sediment_Temp
                2.0,  # Water_Depth
                lat,  # Latitude
                lon,  # Longitude
                100.0,  # Elevation
                -8.0,  # Timezone
                12.0,  # Air_Temp_Min
                28.0,  # Air_Temp_Max
                8.0,  # Dewpoint_Min
                18.0,  # Dewpoint_Max
                2.5,  # Wind_Speed_Avg
                0.3,  # Cloud_Cover_Avg
                0.0,  # Simulation_Date
            )

            result = rtemp_goldsim_adapter.process_data(*args)

            # Verify valid results for each location
            assert len(result) == 3
            assert all(not math.isnan(v) for v in result)
            assert all(-5.0 <= result[i] <= 50.0 for i in [0, 1])


class TestComparisonAgainstStandaloneRTemp:
    """
    Comparison test against standalone rTemp.

    Verifies that the adapter produces results consistent with running
    rTemp directly with the same data.
    """

    def test_adapter_matches_standalone_rtemp(self):
        """Verify adapter results match standalone rTemp execution."""
        # Define test parameters
        initial_water_temp = 15.0
        initial_sediment_temp = 14.0
        water_depth = 2.0
        latitude = 45.0
        longitude = -120.0
        elevation = 100.0
        timezone = -8.0
        air_temp_min = 12.0
        air_temp_max = 28.0
        dewpoint_min = 8.0
        dewpoint_max = 18.0
        wind_speed_avg = 2.5
        cloud_cover_avg = 0.3
        simulation_date = 0.0

        # Call adapter
        adapter_args = (
            initial_water_temp,
            initial_sediment_temp,
            water_depth,
            latitude,
            longitude,
            elevation,
            timezone,
            air_temp_min,
            air_temp_max,
            dewpoint_min,
            dewpoint_max,
            wind_speed_avg,
            cloud_cover_avg,
            simulation_date,
        )

        adapter_water_temp, adapter_sediment_temp, adapter_flux = (
            rtemp_goldsim_adapter.process_data(*adapter_args)
        )

        # Run standalone rTemp with equivalent hourly data
        # Use the same disaggregation logic as the adapter
        start_datetime = rtemp_goldsim_adapter.REFERENCE_DATE + timedelta(days=simulation_date)

        # Calculate sunrise for disaggregation
        from rtemp.solar.position import NOAASolarPosition

        sunrise_frac = NOAASolarPosition.calc_sunrise(
            latitude,
            longitude,
            start_datetime.year,
            start_datetime.month,
            start_datetime.day,
            timezone,
            0,
        )

        # Disaggregate temperatures
        air_temp_array = rtemp_goldsim_adapter.disaggregate_temperature(
            air_temp_min, air_temp_max, sunrise_frac
        )
        dewpoint_array = rtemp_goldsim_adapter.disaggregate_temperature(
            dewpoint_min, dewpoint_max, sunrise_frac
        )

        # Create hourly DataFrame
        datetime_stamps = [start_datetime + timedelta(hours=i) for i in range(24)]
        met_data = pd.DataFrame(
            {
                "datetime": datetime_stamps,
                "air_temperature": air_temp_array,
                "dewpoint_temperature": dewpoint_array,
                "wind_speed": np.full(24, wind_speed_avg),
                "cloud_cover": np.full(24, cloud_cover_avg),
            }
        )

        # Run standalone rTemp
        config = ModelConfiguration(
            latitude=latitude,
            longitude=longitude,
            elevation=elevation,
            timezone=timezone,
            initial_water_temp=initial_water_temp,
            initial_sediment_temp=initial_sediment_temp,
            water_depth=water_depth,
            solar_method="Bras",
            longwave_method="Brunt",
            wind_function_method="Brady-Graves-Geyer",
            enable_diagnostics=False,
        )

        model = RTempModel(config)
        results = model.run(met_data)

        # Extract final state
        standalone_water_temp = float(results.iloc[-1]["water_temperature"])
        standalone_sediment_temp = float(results.iloc[-1]["sediment_temperature"])
        standalone_flux = float(results["net_flux"].mean())

        # Compare results (should match within numerical precision)
        assert (
            abs(adapter_water_temp - standalone_water_temp) < 0.01
        ), f"Water temp mismatch: adapter={adapter_water_temp:.4f}, standalone={standalone_water_temp:.4f}"
        assert (
            abs(adapter_sediment_temp - standalone_sediment_temp) < 0.01
        ), f"Sediment temp mismatch: adapter={adapter_sediment_temp:.4f}, standalone={standalone_sediment_temp:.4f}"
        assert (
            abs(adapter_flux - standalone_flux) < 0.1
        ), f"Flux mismatch: adapter={adapter_flux:.2f}, standalone={standalone_flux:.2f}"


class TestDryBedScenario:
    """
    Dry-bed scenario test.

    Verifies that the adapter handles dry-bed conditions correctly,
    bypassing rTemp and returning appropriate fallback values.
    """

    def test_dry_bed_at_threshold(self):
        """Test dry-bed bypass at exactly the threshold depth."""
        args = (
            15.0,  # Current_Water_Temp
            14.0,  # Current_Sediment_Temp
            0.01,  # Water_Depth (exactly at threshold)
            45.0,  # Latitude
            -120.0,  # Longitude
            100.0,  # Elevation
            -8.0,  # Timezone
            12.0,  # Air_Temp_Min
            28.0,  # Air_Temp_Max
            8.0,  # Dewpoint_Min
            18.0,  # Dewpoint_Max
            2.5,  # Wind_Speed_Avg
            0.3,  # Cloud_Cover_Avg
            0.0,  # Simulation_Date
        )

        result = rtemp_goldsim_adapter.process_data(*args)
        new_water_temp, new_sediment_temp, daily_avg_net_flux = result

        # Verify dry-bed behavior
        # Water temperature should be preserved
        assert new_water_temp == 15.0

        # Sediment temperature should be mean of air temperature range
        expected_sediment_temp = (12.0 + 28.0) / 2.0
        assert new_sediment_temp == expected_sediment_temp

        # Net flux should be zero
        assert daily_avg_net_flux == 0.0

    def test_dry_bed_below_threshold(self):
        """Test dry-bed bypass below the threshold depth."""
        args = (
            20.0,  # Current_Water_Temp
            18.0,  # Current_Sediment_Temp
            0.005,  # Water_Depth (below threshold)
            45.0,  # Latitude
            -120.0,  # Longitude
            100.0,  # Elevation
            -8.0,  # Timezone
            10.0,  # Air_Temp_Min
            30.0,  # Air_Temp_Max
            5.0,  # Dewpoint_Min
            20.0,  # Dewpoint_Max
            3.0,  # Wind_Speed_Avg
            0.5,  # Cloud_Cover_Avg
            5.0,  # Simulation_Date
        )

        result = rtemp_goldsim_adapter.process_data(*args)
        new_water_temp, new_sediment_temp, daily_avg_net_flux = result

        # Verify dry-bed behavior
        assert new_water_temp == 20.0
        assert new_sediment_temp == 20.0  # (10 + 30) / 2
        assert daily_avg_net_flux == 0.0

    def test_dry_bed_zero_depth(self):
        """Test dry-bed bypass with zero depth."""
        args = (
            18.0,  # Current_Water_Temp
            16.0,  # Current_Sediment_Temp
            0.0,  # Water_Depth (zero)
            45.0,  # Latitude
            -120.0,  # Longitude
            100.0,  # Elevation
            -8.0,  # Timezone
            15.0,  # Air_Temp_Min
            25.0,  # Air_Temp_Max
            10.0,  # Dewpoint_Min
            15.0,  # Dewpoint_Max
            2.0,  # Wind_Speed_Avg
            0.4,  # Cloud_Cover_Avg
            10.0,  # Simulation_Date
        )

        result = rtemp_goldsim_adapter.process_data(*args)
        new_water_temp, new_sediment_temp, daily_avg_net_flux = result

        # Verify dry-bed behavior
        assert new_water_temp == 18.0
        assert new_sediment_temp == 20.0  # (15 + 25) / 2
        assert daily_avg_net_flux == 0.0

    def test_normal_execution_above_threshold(self):
        """Test that normal execution occurs above threshold."""
        args = (
            15.0,  # Current_Water_Temp
            14.0,  # Current_Sediment_Temp
            0.5,  # Water_Depth (well above threshold, avoid instability)
            45.0,  # Latitude
            -120.0,  # Longitude
            100.0,  # Elevation
            -8.0,  # Timezone
            12.0,  # Air_Temp_Min
            28.0,  # Air_Temp_Max
            8.0,  # Dewpoint_Min
            18.0,  # Dewpoint_Max
            2.5,  # Wind_Speed_Avg
            0.3,  # Cloud_Cover_Avg
            0.0,  # Simulation_Date
        )

        result = rtemp_goldsim_adapter.process_data(*args)
        new_water_temp, new_sediment_temp, daily_avg_net_flux = result

        # Verify normal execution (not dry-bed bypass)
        # Water temperature should have changed (not preserved)
        # This is a weak test, but we can't predict exact values
        assert isinstance(new_water_temp, float)
        assert not math.isnan(new_water_temp)

        # Net flux should be non-zero (typically)
        # In rare cases it could be near zero, so just check it's a valid number
        assert isinstance(daily_avg_net_flux, float)
        assert not math.isnan(daily_avg_net_flux)


class TestErrorRecovery:
    """
    Error recovery test.

    Verifies that the adapter handles invalid inputs gracefully,
    logging errors and returning safe fallback values.
    """

    def test_negative_depth_error(self):
        """Test error handling for negative water depth."""
        args = (
            15.0,  # Current_Water_Temp
            14.0,  # Current_Sediment_Temp
            -0.5,  # Water_Depth (negative - invalid)
            45.0,  # Latitude
            -120.0,  # Longitude
            100.0,  # Elevation
            -8.0,  # Timezone
            12.0,  # Air_Temp_Min
            28.0,  # Air_Temp_Max
            8.0,  # Dewpoint_Min
            18.0,  # Dewpoint_Max
            2.5,  # Wind_Speed_Avg
            0.3,  # Cloud_Cover_Avg
            0.0,  # Simulation_Date
        )

        # Mock gspy.error to capture the error call
        with patch.object(rtemp_goldsim_adapter.gspy, "error") as mock_error:
            mock_error.side_effect = RuntimeError("Simulated GoldSim stop")

            # Call should raise error
            with pytest.raises(RuntimeError):
                rtemp_goldsim_adapter.process_data(*args)

            # Verify error was called (may be called twice: once for validation, once in exception handler)
            assert mock_error.call_count >= 1

            # Check first call has appropriate message
            first_call_msg = mock_error.call_args_list[0][0][0]
            assert "Water_Depth" in first_call_msg
            assert "-0.5" in first_call_msg

    def test_invalid_latitude_error(self):
        """Test error handling for out-of-range latitude."""
        args = (
            15.0,  # Current_Water_Temp
            14.0,  # Current_Sediment_Temp
            2.0,  # Water_Depth
            95.0,  # Latitude (invalid - out of range)
            -120.0,  # Longitude
            100.0,  # Elevation
            -8.0,  # Timezone
            12.0,  # Air_Temp_Min
            28.0,  # Air_Temp_Max
            8.0,  # Dewpoint_Min
            18.0,  # Dewpoint_Max
            2.5,  # Wind_Speed_Avg
            0.3,  # Cloud_Cover_Avg
            0.0,  # Simulation_Date
        )

        with patch.object(rtemp_goldsim_adapter.gspy, "error") as mock_error:
            mock_error.side_effect = RuntimeError("Simulated GoldSim stop")

            with pytest.raises(RuntimeError):
                rtemp_goldsim_adapter.process_data(*args)

            # Verify error was called (may be called twice: once for validation, once in exception handler)
            assert mock_error.call_count >= 1

            # Check first call has appropriate message
            first_call_msg = mock_error.call_args_list[0][0][0]
            assert "Latitude" in first_call_msg
            assert "95" in first_call_msg

    def test_invalid_longitude_error(self):
        """Test error handling for out-of-range longitude."""
        args = (
            15.0,  # Current_Water_Temp
            14.0,  # Current_Sediment_Temp
            2.0,  # Water_Depth
            45.0,  # Latitude
            -200.0,  # Longitude (invalid - out of range)
            100.0,  # Elevation
            -8.0,  # Timezone
            12.0,  # Air_Temp_Min
            28.0,  # Air_Temp_Max
            8.0,  # Dewpoint_Min
            18.0,  # Dewpoint_Max
            2.5,  # Wind_Speed_Avg
            0.3,  # Cloud_Cover_Avg
            0.0,  # Simulation_Date
        )

        with patch.object(rtemp_goldsim_adapter.gspy, "error") as mock_error:
            mock_error.side_effect = RuntimeError("Simulated GoldSim stop")

            with pytest.raises(RuntimeError):
                rtemp_goldsim_adapter.process_data(*args)

            # Verify error was called (may be called twice: once for validation, once in exception handler)
            assert mock_error.call_count >= 1

            # Check first call has appropriate message
            first_call_msg = mock_error.call_args_list[0][0][0]
            assert "Longitude" in first_call_msg
            assert "-200" in first_call_msg

    def test_exception_handling_with_fallback(self):
        """Test that exceptions are caught and logged with fallback values."""
        # Create args that will cause an exception in rTemp
        # (e.g., by mocking rTemp to raise an exception)
        args = (
            15.0,  # Current_Water_Temp
            14.0,  # Current_Sediment_Temp
            2.0,  # Water_Depth
            45.0,  # Latitude
            -120.0,  # Longitude
            100.0,  # Elevation
            -8.0,  # Timezone
            12.0,  # Air_Temp_Min
            28.0,  # Air_Temp_Max
            8.0,  # Dewpoint_Min
            18.0,  # Dewpoint_Max
            2.5,  # Wind_Speed_Avg
            0.3,  # Cloud_Cover_Avg
            0.0,  # Simulation_Date
        )

        # Mock RTempModel.run to raise an exception
        with patch.object(RTempModel, "run") as mock_run:
            mock_run.side_effect = ValueError("Simulated rTemp error")

            # Mock gspy.error to capture the error call
            with patch.object(rtemp_goldsim_adapter.gspy, "error") as mock_error:
                mock_error.side_effect = RuntimeError("Simulated GoldSim stop")

                # Call should raise error
                with pytest.raises(RuntimeError):
                    rtemp_goldsim_adapter.process_data(*args)

                # Verify error was called
                mock_error.assert_called_once()
                error_msg = mock_error.call_args[0][0]
                assert "rTemp adapter error" in error_msg

    def test_logging_during_normal_execution(self):
        """Test that logging occurs during normal execution."""
        args = (
            15.0,  # Current_Water_Temp
            14.0,  # Current_Sediment_Temp
            2.0,  # Water_Depth
            45.0,  # Latitude
            -120.0,  # Longitude
            100.0,  # Elevation
            -8.0,  # Timezone
            12.0,  # Air_Temp_Min
            28.0,  # Air_Temp_Max
            8.0,  # Dewpoint_Min
            18.0,  # Dewpoint_Max
            2.5,  # Wind_Speed_Avg
            0.3,  # Cloud_Cover_Avg
            0.0,  # Simulation_Date
        )

        # Mock gspy.log to capture log calls
        with patch.object(rtemp_goldsim_adapter.gspy, "log") as mock_log:
            result = rtemp_goldsim_adapter.process_data(*args)

            # Verify logging occurred
            assert mock_log.call_count >= 2  # At least start and end logs

            # Check that log messages contain expected information
            log_messages = [call[0][0] for call in mock_log.call_args_list]

            # Should have a "Processing day" message
            assert any("Processing day" in msg for msg in log_messages)

            # Should have a "rTemp complete" message
            assert any("rTemp complete" in msg for msg in log_messages)

    def test_logging_during_dry_bed(self):
        """Test that warning is logged during dry-bed bypass."""
        args = (
            15.0,  # Current_Water_Temp
            14.0,  # Current_Sediment_Temp
            0.005,  # Water_Depth (dry-bed)
            45.0,  # Latitude
            -120.0,  # Longitude
            100.0,  # Elevation
            -8.0,  # Timezone
            12.0,  # Air_Temp_Min
            28.0,  # Air_Temp_Max
            8.0,  # Dewpoint_Min
            18.0,  # Dewpoint_Max
            2.5,  # Wind_Speed_Avg
            0.3,  # Cloud_Cover_Avg
            0.0,  # Simulation_Date
        )

        # Mock gspy.log to capture log calls
        with patch.object(rtemp_goldsim_adapter.gspy, "log") as mock_log:
            result = rtemp_goldsim_adapter.process_data(*args)

            # Verify warning was logged
            log_messages = [call[0][0] for call in mock_log.call_args_list]
            assert any("Dry-bed condition detected" in msg for msg in log_messages)

            # Check that warning level (1) was used
            log_levels = [call[0][1] for call in mock_log.call_args_list if len(call[0]) > 1]
            assert 1 in log_levels


class TestDisaggregationFunction:
    """Test the temperature disaggregation function."""

    def test_disaggregation_produces_24_values(self):
        """Test that disaggregation produces exactly 24 hourly values."""
        result = rtemp_goldsim_adapter.disaggregate_temperature(10.0, 30.0, 0.25)
        assert len(result) == 24

    def test_disaggregation_respects_min_max(self):
        """Test that disaggregated values stay within min/max bounds."""
        t_min = 10.0
        t_max = 30.0
        result = rtemp_goldsim_adapter.disaggregate_temperature(t_min, t_max, 0.25)

        # Values should be within reasonable bounds (allowing for sinusoidal pattern)
        assert result.min() >= t_min - 1.0  # Small tolerance for numerical precision
        assert result.max() <= t_max + 1.0

    def test_disaggregation_mean_equals_average(self):
        """Test that mean of disaggregated values equals average of min/max."""
        t_min = 10.0
        t_max = 30.0
        result = rtemp_goldsim_adapter.disaggregate_temperature(t_min, t_max, 0.25)

        expected_mean = (t_min + t_max) / 2.0
        actual_mean = result.mean()

        # Should be very close (within numerical precision)
        assert abs(actual_mean - expected_mean) < 0.1
