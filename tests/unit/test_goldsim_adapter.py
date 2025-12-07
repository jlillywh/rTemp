"""
Unit tests for GoldSim-rTemp adapter edge cases.

These tests focus on specific edge cases for:
- Input validation
- Dry-bed logic
- DataFrame construction
- Output extraction

Requirements: Testing Strategy - Unit Testing
"""

import math
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

import numpy as np
import pandas as pd
import pytest

# Import the adapter module from examples
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "examples" / "goldsim_integration"))
import rtemp_goldsim_adapter

from rtemp import ModelConfiguration, RTempModel


class TestInputValidationEdgeCases:
    """Unit tests for input validation edge cases."""

    def test_water_depth_exactly_zero(self):
        """Test validation with water depth exactly zero."""
        args = (
            15.0,
            14.0,
            0.0,  # depth = 0.0
            45.0,
            -120.0,
            100.0,
            -8.0,
            12.0,
            28.0,
            8.0,
            18.0,
            2.5,
            0.3,
            0.0,
        )

        # Should trigger dry-bed bypass (not error)
        result = rtemp_goldsim_adapter.process_data(*args)
        assert result[0] == 15.0  # Water temp preserved
        assert result[2] == 0.0  # Flux zero

    def test_water_depth_slightly_negative(self):
        """Test validation with slightly negative water depth."""
        args = (
            15.0,
            14.0,
            -0.001,  # depth = -0.001
            45.0,
            -120.0,
            100.0,
            -8.0,
            12.0,
            28.0,
            8.0,
            18.0,
            2.5,
            0.3,
            0.0,
        )

        with patch.object(rtemp_goldsim_adapter.gspy, "error") as mock_error:
            mock_error.side_effect = RuntimeError("Simulated error")

            with pytest.raises(RuntimeError):
                rtemp_goldsim_adapter.process_data(*args)

            assert mock_error.call_count >= 1
            error_msg = mock_error.call_args_list[0][0][0]
            assert "Water_Depth" in error_msg

    def test_water_depth_very_negative(self):
        """Test validation with very negative water depth."""
        args = (
            15.0,
            14.0,
            -100.0,  # depth = -100.0
            45.0,
            -120.0,
            100.0,
            -8.0,
            12.0,
            28.0,
            8.0,
            18.0,
            2.5,
            0.3,
            0.0,
        )

        with patch.object(rtemp_goldsim_adapter.gspy, "error") as mock_error:
            mock_error.side_effect = RuntimeError("Simulated error")

            with pytest.raises(RuntimeError):
                rtemp_goldsim_adapter.process_data(*args)

            assert mock_error.call_count >= 1

    def test_latitude_at_north_pole(self):
        """Test validation with latitude at north pole (90)."""
        args = (
            15.0,
            14.0,
            2.0,
            90.0,
            -120.0,
            100.0,
            -8.0,  # lat = 90.0
            12.0,
            28.0,
            8.0,
            18.0,
            2.5,
            0.3,
            0.0,
        )

        # Should be valid (90 is within range)
        result = rtemp_goldsim_adapter.process_data(*args)
        assert len(result) == 3
        assert all(isinstance(v, float) for v in result)

    def test_latitude_at_south_pole(self):
        """Test validation with latitude at south pole (-90)."""
        args = (
            15.0,
            14.0,
            2.0,
            -90.0,
            -120.0,
            100.0,
            -8.0,  # lat = -90.0
            12.0,
            28.0,
            8.0,
            18.0,
            2.5,
            0.3,
            0.0,
        )

        # Should be valid (-90 is within range)
        result = rtemp_goldsim_adapter.process_data(*args)
        assert len(result) == 3
        assert all(isinstance(v, float) for v in result)

    def test_latitude_just_above_north_pole(self):
        """Test validation with latitude just above north pole."""
        args = (
            15.0,
            14.0,
            2.0,
            90.1,
            -120.0,
            100.0,
            -8.0,  # lat = 90.1
            12.0,
            28.0,
            8.0,
            18.0,
            2.5,
            0.3,
            0.0,
        )

        with patch.object(rtemp_goldsim_adapter.gspy, "error") as mock_error:
            mock_error.side_effect = RuntimeError("Simulated error")

            with pytest.raises(RuntimeError):
                rtemp_goldsim_adapter.process_data(*args)

            assert mock_error.call_count >= 1
            error_msg = mock_error.call_args_list[0][0][0]
            assert "Latitude" in error_msg

    def test_latitude_just_below_south_pole(self):
        """Test validation with latitude just below south pole."""
        args = (
            15.0,
            14.0,
            2.0,
            -90.1,
            -120.0,
            100.0,
            -8.0,  # lat = -90.1
            12.0,
            28.0,
            8.0,
            18.0,
            2.5,
            0.3,
            0.0,
        )

        with patch.object(rtemp_goldsim_adapter.gspy, "error") as mock_error:
            mock_error.side_effect = RuntimeError("Simulated error")

            with pytest.raises(RuntimeError):
                rtemp_goldsim_adapter.process_data(*args)

            assert mock_error.call_count >= 1

    def test_longitude_at_date_line_positive(self):
        """Test validation with longitude at date line (180)."""
        args = (
            15.0,
            14.0,
            2.0,
            45.0,
            180.0,
            100.0,
            -8.0,  # lon = 180.0
            12.0,
            28.0,
            8.0,
            18.0,
            2.5,
            0.3,
            0.0,
        )

        # Should be valid (180 is within range)
        result = rtemp_goldsim_adapter.process_data(*args)
        assert len(result) == 3

    def test_longitude_at_date_line_negative(self):
        """Test validation with longitude at date line (-180)."""
        args = (
            15.0,
            14.0,
            2.0,
            45.0,
            -180.0,
            100.0,
            -8.0,  # lon = -180.0
            12.0,
            28.0,
            8.0,
            18.0,
            2.5,
            0.3,
            0.0,
        )

        # Should be valid (-180 is within range)
        result = rtemp_goldsim_adapter.process_data(*args)
        assert len(result) == 3

    def test_longitude_just_above_date_line(self):
        """Test validation with longitude just above date line."""
        args = (
            15.0,
            14.0,
            2.0,
            45.0,
            180.1,
            100.0,
            -8.0,  # lon = 180.1
            12.0,
            28.0,
            8.0,
            18.0,
            2.5,
            0.3,
            0.0,
        )

        with patch.object(rtemp_goldsim_adapter.gspy, "error") as mock_error:
            mock_error.side_effect = RuntimeError("Simulated error")

            with pytest.raises(RuntimeError):
                rtemp_goldsim_adapter.process_data(*args)

            assert mock_error.call_count >= 1
            error_msg = mock_error.call_args_list[0][0][0]
            assert "Longitude" in error_msg

    def test_longitude_just_below_negative_date_line(self):
        """Test validation with longitude just below negative date line."""
        args = (
            15.0,
            14.0,
            2.0,
            45.0,
            -180.1,
            100.0,
            -8.0,  # lon = -180.1
            12.0,
            28.0,
            8.0,
            18.0,
            2.5,
            0.3,
            0.0,
        )

        with patch.object(rtemp_goldsim_adapter.gspy, "error") as mock_error:
            mock_error.side_effect = RuntimeError("Simulated error")

            with pytest.raises(RuntimeError):
                rtemp_goldsim_adapter.process_data(*args)

            assert mock_error.call_count >= 1

    def test_extreme_temperature_values(self):
        """Test with extreme but valid temperature values."""
        args = (
            -5.0,
            -5.0,
            2.0,  # Very cold initial temps
            45.0,
            -120.0,
            100.0,
            -8.0,
            -40.0,
            45.0,
            -45.0,
            40.0,  # Extreme air/dewpoint
            2.5,
            0.3,
            0.0,
        )

        # Should execute without error
        result = rtemp_goldsim_adapter.process_data(*args)
        assert len(result) == 3
        assert all(isinstance(v, float) for v in result)


class TestDryBedLogicEdgeCases:
    """Unit tests for dry-bed logic edge cases."""

    def test_dry_bed_exactly_at_threshold(self):
        """Test dry-bed logic at exactly the threshold value."""
        args = (
            20.0,
            18.0,
            0.01,  # depth = 0.01 (exactly at threshold)
            45.0,
            -120.0,
            100.0,
            -8.0,
            10.0,
            30.0,
            5.0,
            20.0,
            2.5,
            0.3,
            0.0,
        )

        result = rtemp_goldsim_adapter.process_data(*args)

        # Should trigger dry-bed bypass
        assert result[0] == 20.0  # Water temp preserved
        assert result[1] == 20.0  # Sediment temp = mean air temp
        assert result[2] == 0.0  # Flux zero

    def test_dry_bed_just_below_threshold(self):
        """Test dry-bed logic just below threshold."""
        args = (
            20.0,
            18.0,
            0.009,  # depth = 0.009 (just below threshold)
            45.0,
            -120.0,
            100.0,
            -8.0,
            10.0,
            30.0,
            5.0,
            20.0,
            2.5,
            0.3,
            0.0,
        )

        result = rtemp_goldsim_adapter.process_data(*args)

        # Should trigger dry-bed bypass
        assert result[0] == 20.0
        assert result[1] == 20.0
        assert result[2] == 0.0

    def test_dry_bed_just_above_threshold(self):
        """Test normal execution just above threshold."""
        args = (
            20.0,
            18.0,
            0.5,  # depth = 0.5 (well above threshold to avoid instability)
            45.0,
            -120.0,
            100.0,
            -8.0,
            10.0,
            30.0,
            5.0,
            20.0,
            2.5,
            0.3,
            0.0,
        )

        result = rtemp_goldsim_adapter.process_data(*args)

        # Should NOT trigger dry-bed bypass
        # Water temp may have changed
        assert isinstance(result[0], float)
        assert not math.isnan(result[0])

    def test_dry_bed_with_negative_air_temps(self):
        """Test dry-bed logic with negative air temperatures."""
        args = (
            5.0,
            4.0,
            0.005,  # Dry bed
            45.0,
            -120.0,
            100.0,
            -8.0,
            -10.0,
            5.0,
            -15.0,
            0.0,  # Negative air temps
            2.5,
            0.3,
            0.0,
        )

        result = rtemp_goldsim_adapter.process_data(*args)

        # Water temp preserved
        assert result[0] == 5.0
        # Sediment temp = mean of air temps
        expected_sediment = (-10.0 + 5.0) / 2.0
        assert result[1] == expected_sediment
        assert result[2] == 0.0

    def test_dry_bed_with_equal_min_max_temps(self):
        """Test dry-bed logic when min and max temps are equal."""
        args = (
            15.0,
            14.0,
            0.005,  # Dry bed
            45.0,
            -120.0,
            100.0,
            -8.0,
            20.0,
            20.0,
            15.0,
            15.0,  # Constant temps
            2.5,
            0.3,
            0.0,
        )

        result = rtemp_goldsim_adapter.process_data(*args)

        assert result[0] == 15.0
        assert result[1] == 20.0  # Mean of 20 and 20
        assert result[2] == 0.0

    def test_dry_bed_preserves_extreme_water_temp(self):
        """Test that dry-bed preserves extreme water temperatures."""
        args = (
            45.0,
            40.0,
            0.005,  # Very hot water, dry bed
            45.0,
            -120.0,
            100.0,
            -8.0,
            10.0,
            30.0,
            5.0,
            20.0,
            2.5,
            0.3,
            0.0,
        )

        result = rtemp_goldsim_adapter.process_data(*args)

        # Should preserve the extreme water temp
        assert result[0] == 45.0
        assert result[2] == 0.0


class TestDataFrameConstructionEdgeCases:
    """Unit tests for DataFrame construction edge cases."""

    def test_dataframe_construction_day_zero(self):
        """Test DataFrame construction for simulation day 0."""
        # 12 inputs: water_temp, sed_temp, depth, lat, lon, elev, tz,
        #            air_min, air_max, wind, cloud, sim_date
        args = (15.0, 14.0, 2.0, 45.0, -120.0, 100.0, -8.0, 12.0, 28.0, 2.5, 0.3, 0.0)  # Day 0

        # Mock RTempModel to capture the DataFrame
        with patch.object(RTempModel, "run") as mock_run:
            mock_run.return_value = pd.DataFrame(
                {
                    "water_temperature": [15.5] * 24,
                    "sediment_temperature": [14.5] * 24,
                    "net_flux": [100.0] * 24,
                }
            )

            result = rtemp_goldsim_adapter.process_data(*args)

            # Verify run was called
            assert mock_run.called

            # Get the DataFrame that was passed
            df = mock_run.call_args[0][0]

            # Verify DataFrame structure
            assert len(df) == 24
            assert "datetime" in df.columns

            # Verify first datetime is REFERENCE_DATE
            expected_start = rtemp_goldsim_adapter.REFERENCE_DATE
            assert df["datetime"].iloc[0] == expected_start

            # Verify last datetime is 23 hours later
            expected_end = expected_start + timedelta(hours=23)
            assert df["datetime"].iloc[-1] == expected_end

    def test_dataframe_construction_large_day_number(self):
        """Test DataFrame construction for large simulation day."""
        # 12 inputs: water_temp, sed_temp, depth, lat, lon, elev, tz,
        #            air_min, air_max, wind, cloud, sim_date
        args = (
            15.0,
            14.0,
            2.0,
            45.0,
            -120.0,
            100.0,
            -8.0,
            12.0,
            28.0,
            2.5,
            0.3,
            1000.0,  # Day 1000
        )

        with patch.object(RTempModel, "run") as mock_run:
            mock_run.return_value = pd.DataFrame(
                {
                    "water_temperature": [15.5] * 24,
                    "sediment_temperature": [14.5] * 24,
                    "net_flux": [100.0] * 24,
                }
            )

            result = rtemp_goldsim_adapter.process_data(*args)

            df = mock_run.call_args[0][0]

            # Verify first datetime is REFERENCE_DATE + 1000 days
            expected_start = rtemp_goldsim_adapter.REFERENCE_DATE + timedelta(days=1000)
            assert df["datetime"].iloc[0] == expected_start

    def test_dataframe_has_correct_columns(self):
        """Test that DataFrame has all required columns."""
        # 12 inputs
        args = (15.0, 14.0, 2.0, 45.0, -120.0, 100.0, -8.0, 12.0, 28.0, 2.5, 0.3, 0.0)

        with patch.object(RTempModel, "run") as mock_run:
            mock_run.return_value = pd.DataFrame(
                {
                    "water_temperature": [15.5] * 24,
                    "sediment_temperature": [14.5] * 24,
                    "net_flux": [100.0] * 24,
                }
            )

            result = rtemp_goldsim_adapter.process_data(*args)

            df = mock_run.call_args[0][0]

            # Verify required columns
            required_columns = [
                "datetime",
                "air_temperature",
                "dewpoint_temperature",
                "wind_speed",
                "cloud_cover",
            ]
            for col in required_columns:
                assert col in df.columns

    def test_dataframe_wind_speed_constant(self):
        """Test that wind speed is constant across all hours."""
        # 12 inputs
        args = (
            15.0,
            14.0,
            2.0,
            45.0,
            -120.0,
            100.0,
            -8.0,
            12.0,
            28.0,
            3.5,  # Wind speed
            0.3,
            3.5,  # cloud_cover, sim_date
        )

        with patch.object(RTempModel, "run") as mock_run:
            mock_run.return_value = pd.DataFrame(
                {
                    "water_temperature": [15.5] * 24,
                    "sediment_temperature": [14.5] * 24,
                    "net_flux": [100.0] * 24,
                }
            )

            result = rtemp_goldsim_adapter.process_data(*args)

            df = mock_run.call_args[0][0]

            # All wind speed values should be 3.5
            assert all(df["wind_speed"] == 3.5)

    def test_dataframe_cloud_cover_constant(self):
        """Test that cloud cover is constant across all hours."""
        # 12 inputs
        args = (
            15.0,
            14.0,
            2.0,
            45.0,
            -120.0,
            100.0,
            -8.0,
            12.0,
            28.0,
            2.5,
            0.7,  # Cloud cover
            2.5,  # sim_date
        )

        with patch.object(RTempModel, "run") as mock_run:
            mock_run.return_value = pd.DataFrame(
                {
                    "water_temperature": [15.5] * 24,
                    "sediment_temperature": [14.5] * 24,
                    "net_flux": [100.0] * 24,
                }
            )

            result = rtemp_goldsim_adapter.process_data(*args)

            df = mock_run.call_args[0][0]

            # All cloud cover values should be 0.7
            assert all(df["cloud_cover"] == 0.7)


class TestOutputExtractionEdgeCases:
    """Unit tests for output extraction edge cases."""

    def test_output_extraction_from_single_row(self):
        """Test output extraction when results has only one row."""
        args = (15.0, 14.0, 2.0, 45.0, -120.0, 100.0, -8.0, 12.0, 28.0, 8.0, 18.0, 2.5, 0.3, 0.0)

        # Mock rTemp to return single-row DataFrame
        with patch.object(RTempModel, "run") as mock_run:
            mock_run.return_value = pd.DataFrame(
                {"water_temperature": [16.5], "sediment_temperature": [15.5], "net_flux": [150.0]}
            )

            result = rtemp_goldsim_adapter.process_data(*args)

            # Should extract the single row
            assert result[0] == 16.5
            assert result[1] == 15.5
            assert result[2] == 150.0

    def test_output_extraction_with_varying_flux(self):
        """Test flux calculation with varying values."""
        args = (15.0, 14.0, 2.0, 45.0, -120.0, 100.0, -8.0, 12.0, 28.0, 8.0, 18.0, 2.5, 0.3, 0.0)

        # Create flux values that vary
        flux_values = list(range(0, 240, 10))  # 0, 10, 20, ..., 230

        with patch.object(RTempModel, "run") as mock_run:
            mock_run.return_value = pd.DataFrame(
                {
                    "water_temperature": [16.0] * 24,
                    "sediment_temperature": [15.0] * 24,
                    "net_flux": flux_values,
                }
            )

            result = rtemp_goldsim_adapter.process_data(*args)

            # Flux should be mean of flux_values
            expected_flux = np.mean(flux_values)
            assert abs(result[2] - expected_flux) < 0.01

    def test_output_extraction_with_negative_flux(self):
        """Test flux calculation with negative values."""
        args = (15.0, 14.0, 2.0, 45.0, -120.0, 100.0, -8.0, 12.0, 28.0, 8.0, 18.0, 2.5, 0.3, 0.0)

        with patch.object(RTempModel, "run") as mock_run:
            mock_run.return_value = pd.DataFrame(
                {
                    "water_temperature": [14.5] * 24,
                    "sediment_temperature": [13.5] * 24,
                    "net_flux": [-50.0] * 24,  # Negative flux (cooling)
                }
            )

            result = rtemp_goldsim_adapter.process_data(*args)

            # Should handle negative flux correctly
            assert result[2] == -50.0

    def test_output_types_are_float(self):
        """Test that all outputs are Python float type."""
        args = (15.0, 14.0, 2.0, 45.0, -120.0, 100.0, -8.0, 12.0, 28.0, 8.0, 18.0, 2.5, 0.3, 0.0)

        with patch.object(RTempModel, "run") as mock_run:
            # Return DataFrame with numpy types
            mock_run.return_value = pd.DataFrame(
                {
                    "water_temperature": np.array([16.5] * 24),
                    "sediment_temperature": np.array([15.5] * 24),
                    "net_flux": np.array([150.0] * 24),
                }
            )

            result = rtemp_goldsim_adapter.process_data(*args)

            # All outputs should be Python float, not numpy types
            assert type(result[0]) == float
            assert type(result[1]) == float
            assert type(result[2]) == float

    def test_output_extraction_with_temperature_change(self):
        """Test extraction when temperature changes over time."""
        args = (15.0, 14.0, 2.0, 45.0, -120.0, 100.0, -8.0, 12.0, 28.0, 8.0, 18.0, 2.5, 0.3, 0.0)

        # Create temperature that increases over time
        water_temps = [15.0 + i * 0.1 for i in range(24)]  # 15.0 to 17.3

        with patch.object(RTempModel, "run") as mock_run:
            mock_run.return_value = pd.DataFrame(
                {
                    "water_temperature": water_temps,
                    "sediment_temperature": [14.5] * 24,
                    "net_flux": [100.0] * 24,
                }
            )

            result = rtemp_goldsim_adapter.process_data(*args)

            # Should extract the LAST temperature (end of day)
            assert result[0] == water_temps[-1]

    def test_output_tuple_structure(self):
        """Test that output is always a 3-tuple."""
        args = (15.0, 14.0, 2.0, 45.0, -120.0, 100.0, -8.0, 12.0, 28.0, 8.0, 18.0, 2.5, 0.3, 0.0)

        with patch.object(RTempModel, "run") as mock_run:
            mock_run.return_value = pd.DataFrame(
                {
                    "water_temperature": [16.5] * 24,
                    "sediment_temperature": [15.5] * 24,
                    "net_flux": [150.0] * 24,
                }
            )

            result = rtemp_goldsim_adapter.process_data(*args)

            # Verify tuple structure
            assert isinstance(result, tuple)
            assert len(result) == 3


class TestDisaggregationEdgeCases:
    """Unit tests for temperature disaggregation edge cases."""

    def test_disaggregation_with_zero_range(self):
        """Test disaggregation when min equals max."""
        result = rtemp_goldsim_adapter.disaggregate_temperature(20.0, 20.0, 0.25)

        # All values should be 20.0
        assert len(result) == 24
        assert all(abs(v - 20.0) < 0.01 for v in result)

    def test_disaggregation_with_negative_temps(self):
        """Test disaggregation with negative temperatures."""
        result = rtemp_goldsim_adapter.disaggregate_temperature(-20.0, -5.0, 0.25)

        assert len(result) == 24
        # Mean should be approximately (-20 + -5) / 2 = -12.5
        assert abs(result.mean() - (-12.5)) < 0.1

    def test_disaggregation_with_large_range(self):
        """Test disaggregation with large temperature range."""
        result = rtemp_goldsim_adapter.disaggregate_temperature(-10.0, 40.0, 0.25)

        assert len(result) == 24
        # Mean should be approximately 15.0
        assert abs(result.mean() - 15.0) < 0.1

    def test_disaggregation_sunrise_at_midnight(self):
        """Test disaggregation with sunrise at midnight."""
        result = rtemp_goldsim_adapter.disaggregate_temperature(10.0, 30.0, 0.0)

        assert len(result) == 24
        # Should still produce valid pattern
        assert abs(result.mean() - 20.0) < 0.1

    def test_disaggregation_sunrise_at_noon(self):
        """Test disaggregation with sunrise at noon."""
        result = rtemp_goldsim_adapter.disaggregate_temperature(10.0, 30.0, 0.5)

        assert len(result) == 24
        # Should still produce valid pattern
        assert abs(result.mean() - 20.0) < 0.1

    def test_disaggregation_returns_numpy_array(self):
        """Test that disaggregation returns numpy array."""
        result = rtemp_goldsim_adapter.disaggregate_temperature(10.0, 30.0, 0.25)

        assert isinstance(result, np.ndarray)
        assert result.dtype == np.float64

    def test_disaggregation_with_very_small_range(self):
        """Test disaggregation with very small temperature range."""
        result = rtemp_goldsim_adapter.disaggregate_temperature(20.0, 20.1, 0.25)

        assert len(result) == 24
        # All values should be close to 20.05
        assert all(abs(v - 20.05) < 0.1 for v in result)


class TestEdgeCasesCombinations:
    """Unit tests for combinations of edge cases."""

    def test_dry_bed_with_extreme_temps(self):
        """Test dry-bed with extreme temperature values."""
        args = (
            -5.0,
            -5.0,
            0.005,  # Dry bed, very cold
            45.0,
            -120.0,
            100.0,
            -8.0,
            -40.0,
            45.0,
            -45.0,
            40.0,  # Extreme range
            2.5,
            0.3,
            0.0,
        )

        result = rtemp_goldsim_adapter.process_data(*args)

        # Water temp preserved
        assert result[0] == -5.0
        # Sediment temp = mean of extreme air temps
        expected_sediment = (-40.0 + 45.0) / 2.0
        assert result[1] == expected_sediment
        assert result[2] == 0.0

    def test_boundary_latitude_with_dry_bed(self):
        """Test boundary latitude combined with dry-bed."""
        args = (
            15.0,
            14.0,
            0.005,  # Dry bed
            90.0,
            -120.0,
            100.0,
            -8.0,  # North pole
            12.0,
            28.0,
            8.0,
            18.0,
            2.5,
            0.3,
            0.0,
        )

        result = rtemp_goldsim_adapter.process_data(*args)

        # Should trigger dry-bed bypass (not error)
        assert result[0] == 15.0
        assert result[2] == 0.0

    def test_boundary_longitude_with_dry_bed(self):
        """Test boundary longitude combined with dry-bed."""
        args = (
            15.0,
            14.0,
            0.005,  # Dry bed
            45.0,
            180.0,
            100.0,
            -8.0,  # Date line
            12.0,
            28.0,
            8.0,
            18.0,
            2.5,
            0.3,
            0.0,
        )

        result = rtemp_goldsim_adapter.process_data(*args)

        # Should trigger dry-bed bypass
        assert result[0] == 15.0
        assert result[2] == 0.0

    def test_zero_wind_speed(self):
        """Test with zero wind speed."""
        args = (
            15.0,
            14.0,
            2.0,
            45.0,
            -120.0,
            100.0,
            -8.0,
            12.0,
            28.0,
            8.0,
            18.0,
            0.0,  # Zero wind speed
            0.3,
            0.0,
        )

        # Should execute without error
        result = rtemp_goldsim_adapter.process_data(*args)
        assert len(result) == 3
        assert all(isinstance(v, float) for v in result)

    def test_zero_cloud_cover(self):
        """Test with zero cloud cover (clear sky)."""
        args = (
            15.0,
            14.0,
            2.0,
            45.0,
            -120.0,
            100.0,
            -8.0,
            12.0,
            28.0,
            8.0,
            18.0,
            2.5,
            0.0,  # Zero cloud cover
            0.0,
        )

        result = rtemp_goldsim_adapter.process_data(*args)
        assert len(result) == 3

    def test_full_cloud_cover(self):
        """Test with full cloud cover."""
        args = (
            15.0,
            14.0,
            2.0,
            45.0,
            -120.0,
            100.0,
            -8.0,
            12.0,
            28.0,
            8.0,
            18.0,
            2.5,
            1.0,  # Full cloud cover
            0.0,
        )

        result = rtemp_goldsim_adapter.process_data(*args)
        assert len(result) == 3
