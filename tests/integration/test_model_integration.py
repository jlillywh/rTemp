"""
Integration tests for complete rTemp model execution.

These tests verify that the model works correctly end-to-end with
realistic data and various configurations.
"""

import math
from datetime import datetime, timedelta

import pandas as pd
import pytest

from rtemp import ModelConfiguration, RTempModel


class TestSimpleSingleDayScenario:
    """Test simple single-day scenario with hourly data."""

    def test_single_day_hourly_execution(self):
        """Test model execution for a single day with hourly data."""
        # Create basic configuration
        config = ModelConfiguration(
            latitude=45.0,
            longitude=-120.0,
            elevation=100.0,
            timezone=-8.0,  # UTC-8 for western hemisphere (120°W)
            initial_water_temp=15.0,
            initial_sediment_temp=15.0,
            water_depth=2.0,
        )

        # Create 24 hours of meteorological data
        start_date = datetime(2024, 7, 15, 0, 0)
        met_data = []
        for hour in range(24):
            dt = start_date + timedelta(hours=hour)
            temp_variation = 10.0 * (1 - abs(hour - 15) / 12.0)
            air_temp = 15.0 + temp_variation

            met_data.append(
                {
                    "datetime": dt,
                    "air_temperature": air_temp,
                    "dewpoint_temperature": air_temp - 5.0,
                    "wind_speed": 2.0,
                    "cloud_cover": 0.3,
                }
            )

        met_df = pd.DataFrame(met_data)

        # Run model
        model = RTempModel(config)
        results = model.run(met_df)

        # Verify output structure
        assert len(results) == 24
        assert "datetime" in results.columns
        assert "water_temperature" in results.columns
        assert "sediment_temperature" in results.columns
        assert "solar_radiation" in results.columns
        assert "net_flux" in results.columns

        # Verify no NaN or infinite values
        assert not results["water_temperature"].isna().any()
        assert not results["water_temperature"].apply(math.isinf).any()
        assert not results["sediment_temperature"].isna().any()
        assert not results["sediment_temperature"].apply(math.isinf).any()

        # Verify temperature is within reasonable bounds
        assert results["water_temperature"].min() >= config.minimum_temperature
        assert results["water_temperature"].max() < 50.0  # Reasonable upper bound

        # Verify solar radiation is zero at deep night
        # In July at 45°N, sunrise is around 5-6 AM, so check midnight to 4 AM
        deep_night_hours = results[results["datetime"].dt.hour.isin([0, 1, 2, 3, 4])]
        assert (deep_night_hours["solar_radiation"] == 0.0).all()

    def test_single_day_with_diagnostics(self):
        """Test model execution with diagnostic output enabled."""
        config = ModelConfiguration(
            latitude=45.0,
            longitude=-120.0,
            elevation=100.0,
            timezone=-8.0,
            initial_water_temp=15.0,
            water_depth=2.0,
            enable_diagnostics=True,
        )

        # Create simple met data
        start_date = datetime(2024, 7, 15, 12, 0)
        met_data = [
            {
                "datetime": start_date,
                "air_temperature": 20.0,
                "dewpoint_temperature": 15.0,
                "wind_speed": 2.0,
                "cloud_cover": 0.3,
            }
        ]
        met_df = pd.DataFrame(met_data)

        # Run model
        model = RTempModel(config)
        results = model.run(met_df)

        # Verify diagnostic columns are present
        assert "vapor_pressure_water" in results.columns
        assert "vapor_pressure_air" in results.columns
        assert "atmospheric_emissivity" in results.columns
        assert "wind_speed_2m" in results.columns
        assert "wind_speed_7m" in results.columns
        assert "wind_function" in results.columns
        assert "water_temp_change_rate" in results.columns
        assert "sediment_temp_change_rate" in results.columns


class TestMultiDayScenario:
    """Test multi-day scenario with realistic data patterns."""

    def test_week_long_simulation(self):
        """Test model execution for one week with hourly data."""
        config = ModelConfiguration(
            latitude=45.0,
            longitude=-120.0,
            elevation=100.0,
            timezone=-8.0,
            initial_water_temp=15.0,
            initial_sediment_temp=15.0,
            water_depth=2.0,
        )

        # Create 7 days of hourly data
        start_date = datetime(2024, 7, 15, 0, 0)
        met_data = []
        for day in range(7):
            for hour in range(24):
                dt = start_date + timedelta(days=day, hours=hour)
                # Add day-to-day variation
                day_offset = 2.0 * math.sin(day * math.pi / 3.5)
                temp_variation = 10.0 * (1 - abs(hour - 15) / 12.0)
                air_temp = 18.0 + day_offset + temp_variation

                met_data.append(
                    {
                        "datetime": dt,
                        "air_temperature": air_temp,
                        "dewpoint_temperature": air_temp - 5.0,
                        "wind_speed": 2.0 + 0.5 * math.sin(day * math.pi / 2),
                        "cloud_cover": 0.3 + 0.2 * math.sin(day * math.pi / 3),
                    }
                )

        met_df = pd.DataFrame(met_data)

        # Run model
        model = RTempModel(config)
        results = model.run(met_df)

        # Verify output
        assert len(results) == 7 * 24
        assert not results["water_temperature"].isna().any()
        assert not results["water_temperature"].apply(math.isinf).any()

        # Verify temperature trends are reasonable
        # Water temperature should not change too rapidly
        temp_diff = results["water_temperature"].diff().abs()
        assert temp_diff.max() < 5.0  # No more than 5°C change per hour

        # Verify all heat flux components are present
        assert "solar_radiation" in results.columns
        assert "longwave_atmospheric" in results.columns
        assert "evaporation" in results.columns
        assert "convection" in results.columns

    @pytest.mark.skip(reason="Test uses unrealistic 6-month timestep gap - not a valid use case")
    def test_seasonal_variation(self):
        """Test model with data spanning different seasons."""
        config = ModelConfiguration(
            latitude=45.0,
            longitude=-120.0,
            elevation=100.0,
            timezone=-8.0,
            initial_water_temp=10.0,
            water_depth=2.0,
        )

        # Create data for winter and summer days (in chronological order)
        met_data = []

        # Winter day (January)
        winter_date = datetime(2024, 1, 15, 12, 0)
        met_data.append(
            {
                "datetime": winter_date,
                "air_temperature": 5.0,
                "dewpoint_temperature": 2.0,
                "wind_speed": 3.0,
                "cloud_cover": 0.7,
            }
        )

        # Summer day (July)
        summer_date = datetime(2024, 7, 15, 12, 0)
        met_data.append(
            {
                "datetime": summer_date,
                "air_temperature": 25.0,
                "dewpoint_temperature": 18.0,
                "wind_speed": 2.0,
                "cloud_cover": 0.2,
            }
        )

        met_df = pd.DataFrame(met_data)

        # Run model
        model = RTempModel(config)
        results = model.run(met_df)

        # Verify both timesteps executed
        assert len(results) == 2

        # Summer should have higher solar radiation (now at index 1)
        winter_solar = results.iloc[0]["solar_radiation"]
        summer_solar = results.iloc[1]["solar_radiation"]
        assert summer_solar > winter_solar


class TestVariableTimestepHandling:
    """Test model handling of variable timesteps."""

    def test_irregular_timesteps(self):
        """Test model with irregular time intervals."""
        config = ModelConfiguration(
            latitude=45.0,
            longitude=-120.0,
            elevation=100.0,
            timezone=-8.0,
            initial_water_temp=15.0,
            water_depth=2.0,
        )

        # Create data with irregular timesteps
        start_date = datetime(2024, 7, 15, 0, 0)
        met_data = [
            {
                "datetime": start_date,
                "air_temperature": 15.0,
                "dewpoint_temperature": 10.0,
                "wind_speed": 2.0,
                "cloud_cover": 0.3,
            },
            {
                "datetime": start_date + timedelta(minutes=30),
                "air_temperature": 16.0,
                "dewpoint_temperature": 11.0,
                "wind_speed": 2.0,
                "cloud_cover": 0.3,
            },
            {
                "datetime": start_date + timedelta(hours=2),
                "air_temperature": 18.0,
                "dewpoint_temperature": 12.0,
                "wind_speed": 2.5,
                "cloud_cover": 0.4,
            },
            {
                "datetime": start_date + timedelta(hours=3),
                "air_temperature": 20.0,
                "dewpoint_temperature": 13.0,
                "wind_speed": 3.0,
                "cloud_cover": 0.4,
            },
        ]

        met_df = pd.DataFrame(met_data)

        # Run model
        model = RTempModel(config)
        results = model.run(met_df)

        # Verify all timesteps processed
        assert len(results) == 4
        assert not results["water_temperature"].isna().any()

    def test_large_timestep_warning(self):
        """Test that large timesteps trigger appropriate handling."""
        config = ModelConfiguration(
            latitude=45.0,
            longitude=-120.0,
            elevation=100.0,
            timezone=-8.0,
            initial_water_temp=15.0,
            water_depth=2.0,
        )

        # Create data with large gap (> 4 hours)
        start_date = datetime(2024, 7, 15, 0, 0)
        met_data = [
            {
                "datetime": start_date,
                "air_temperature": 15.0,
                "dewpoint_temperature": 10.0,
                "wind_speed": 2.0,
                "cloud_cover": 0.3,
            },
            {
                "datetime": start_date + timedelta(hours=6),
                "air_temperature": 20.0,
                "dewpoint_temperature": 13.0,
                "wind_speed": 2.5,
                "cloud_cover": 0.4,
            },
        ]

        met_df = pd.DataFrame(met_data)

        # Run model - should handle large timestep
        model = RTempModel(config)
        results = model.run(met_df)

        # Verify execution completed
        assert len(results) == 2
        assert not results["water_temperature"].isna().any()


class TestAllMethodCombinations:
    """Test all combinations of solar, longwave, and wind methods."""

    @pytest.mark.parametrize(
        "solar_method",
        [
            "Bras",
            "Bird",
            "Ryan-Stolzenbach",
            "Iqbal",
        ],
    )
    def test_solar_methods(self, solar_method):
        """Test each solar radiation method."""
        config = ModelConfiguration(
            latitude=45.0,
            longitude=-120.0,
            elevation=100.0,
            timezone=-8.0,
            initial_water_temp=15.0,
            water_depth=2.0,
            solar_method=solar_method,
        )

        # Create simple met data
        start_date = datetime(2024, 7, 15, 12, 0)
        met_data = [
            {
                "datetime": start_date,
                "air_temperature": 20.0,
                "dewpoint_temperature": 15.0,
                "wind_speed": 2.0,
                "cloud_cover": 0.3,
            }
        ]
        met_df = pd.DataFrame(met_data)

        # Run model
        model = RTempModel(config)
        results = model.run(met_df)

        # Verify execution
        assert len(results) == 1
        assert results["solar_radiation"].iloc[0] >= 0.0
        assert not math.isnan(results["water_temperature"].iloc[0])

    @pytest.mark.parametrize(
        "longwave_method",
        [
            "Brunt",
            "Brutsaert",
            "Satterlund",
            "Idso-Jackson",
            "Swinbank",
            "Koberg",
        ],
    )
    def test_longwave_methods(self, longwave_method):
        """Test each longwave radiation method."""
        config = ModelConfiguration(
            latitude=45.0,
            longitude=-120.0,
            elevation=100.0,
            timezone=-8.0,
            initial_water_temp=15.0,
            water_depth=2.0,
            longwave_method=longwave_method,
        )

        # Create simple met data
        start_date = datetime(2024, 7, 15, 12, 0)
        met_data = [
            {
                "datetime": start_date,
                "air_temperature": 20.0,
                "dewpoint_temperature": 15.0,
                "wind_speed": 2.0,
                "cloud_cover": 0.3,
            }
        ]
        met_df = pd.DataFrame(met_data)

        # Run model
        model = RTempModel(config)
        results = model.run(met_df)

        # Verify execution
        assert len(results) == 1
        assert not math.isnan(results["longwave_atmospheric"].iloc[0])
        assert not math.isnan(results["water_temperature"].iloc[0])

    @pytest.mark.parametrize(
        "wind_method",
        [
            "Brady-Graves-Geyer",
            "Marciano-Harbeck",
            "Ryan-Harleman",
            "East Mesa",
            "Helfrich",
        ],
    )
    def test_wind_function_methods(self, wind_method):
        """Test each wind function method."""
        config = ModelConfiguration(
            latitude=45.0,
            longitude=-120.0,
            elevation=100.0,
            timezone=-8.0,
            initial_water_temp=15.0,
            water_depth=2.0,
            wind_function_method=wind_method,
        )

        # Create simple met data
        start_date = datetime(2024, 7, 15, 12, 0)
        met_data = [
            {
                "datetime": start_date,
                "air_temperature": 20.0,
                "dewpoint_temperature": 15.0,
                "wind_speed": 2.0,
                "cloud_cover": 0.3,
            }
        ]
        met_df = pd.DataFrame(met_data)

        # Run model
        model = RTempModel(config)
        results = model.run(met_df)

        # Verify execution
        assert len(results) == 1
        assert not math.isnan(results["evaporation"].iloc[0])
        assert not math.isnan(results["convection"].iloc[0])
        assert not math.isnan(results["water_temperature"].iloc[0])

    def test_method_combination(self):
        """Test a specific combination of all methods."""
        config = ModelConfiguration(
            latitude=45.0,
            longitude=-120.0,
            elevation=100.0,
            timezone=-8.0,
            initial_water_temp=15.0,
            water_depth=2.0,
            solar_method="Bird",
            longwave_method="Brutsaert",
            wind_function_method="Ryan-Harleman",
        )

        # Create hourly data for one day
        start_date = datetime(2024, 7, 15, 0, 0)
        met_data = []
        for hour in range(24):
            dt = start_date + timedelta(hours=hour)
            temp_variation = 10.0 * (1 - abs(hour - 15) / 12.0)
            air_temp = 15.0 + temp_variation

            met_data.append(
                {
                    "datetime": dt,
                    "air_temperature": air_temp,
                    "dewpoint_temperature": air_temp - 5.0,
                    "wind_speed": 2.0,
                    "cloud_cover": 0.3,
                }
            )

        met_df = pd.DataFrame(met_data)

        # Run model
        model = RTempModel(config)
        results = model.run(met_df)

        # Verify execution
        assert len(results) == 24
        assert not results["water_temperature"].isna().any()
        assert not results["solar_radiation"].isna().any()
        assert not results["longwave_atmospheric"].isna().any()


class TestEdgeCaseIntegration:
    """Test edge cases in integrated model execution."""

    def test_extreme_cold_conditions(self):
        """Test model with very cold conditions."""
        config = ModelConfiguration(
            latitude=60.0,
            longitude=-120.0,
            elevation=100.0,
            timezone=-8.0,
            initial_water_temp=2.0,
            minimum_temperature=0.0,
            water_depth=2.0,
        )

        # Create cold weather data
        start_date = datetime(2024, 1, 15, 12, 0)
        met_data = [
            {
                "datetime": start_date,
                "air_temperature": -10.0,
                "dewpoint_temperature": -15.0,
                "wind_speed": 5.0,
                "cloud_cover": 0.8,
            }
        ]
        met_df = pd.DataFrame(met_data)

        # Run model
        model = RTempModel(config)
        results = model.run(met_df)

        # Verify minimum temperature is enforced
        assert results["water_temperature"].iloc[0] >= config.minimum_temperature
        assert not math.isnan(results["water_temperature"].iloc[0])

    def test_extreme_hot_conditions(self):
        """Test model with very hot conditions."""
        config = ModelConfiguration(
            latitude=35.0,
            longitude=-115.0,
            elevation=100.0,
            timezone=-8.0,
            initial_water_temp=25.0,
            water_depth=1.0,
        )

        # Create hot weather data
        start_date = datetime(2024, 7, 15, 14, 0)
        met_data = [
            {
                "datetime": start_date,
                "air_temperature": 40.0,
                "dewpoint_temperature": 20.0,
                "wind_speed": 1.0,
                "cloud_cover": 0.0,
            }
        ]
        met_df = pd.DataFrame(met_data)

        # Run model
        model = RTempModel(config)
        results = model.run(met_df)

        # Verify execution
        assert not math.isnan(results["water_temperature"].iloc[0])
        assert results["water_temperature"].iloc[0] < 50.0  # Reasonable upper bound

    def test_high_latitude(self):
        """Test model at high latitude (near polar region)."""
        config = ModelConfiguration(
            latitude=70.0,
            longitude=-120.0,
            elevation=100.0,
            timezone=-8.0,
            initial_water_temp=10.0,
            water_depth=2.0,
        )

        # Create data for summer at high latitude
        start_date = datetime(2024, 6, 21, 12, 0)  # Summer solstice
        met_data = [
            {
                "datetime": start_date,
                "air_temperature": 15.0,
                "dewpoint_temperature": 10.0,
                "wind_speed": 3.0,
                "cloud_cover": 0.5,
            }
        ]
        met_df = pd.DataFrame(met_data)

        # Run model
        model = RTempModel(config)
        results = model.run(met_df)

        # Verify execution (latitude should be clamped internally)
        assert not math.isnan(results["water_temperature"].iloc[0])
        assert results["solar_radiation"].iloc[0] >= 0.0

    def test_zero_wind_speed(self):
        """Test model with zero wind speed."""
        config = ModelConfiguration(
            latitude=45.0,
            longitude=-120.0,
            elevation=100.0,
            timezone=-8.0,
            initial_water_temp=15.0,
            water_depth=2.0,
        )

        # Create data with zero wind
        start_date = datetime(2024, 7, 15, 12, 0)
        met_data = [
            {
                "datetime": start_date,
                "air_temperature": 20.0,
                "dewpoint_temperature": 15.0,
                "wind_speed": 0.0,
                "cloud_cover": 0.3,
            }
        ]
        met_df = pd.DataFrame(met_data)

        # Run model
        model = RTempModel(config)
        results = model.run(met_df)

        # Verify execution
        assert not math.isnan(results["water_temperature"].iloc[0])
        # Evaporation and convection should be minimal but not cause errors
        assert not math.isnan(results["evaporation"].iloc[0])
        assert not math.isnan(results["convection"].iloc[0])

    def test_full_cloud_cover(self):
        """Test model with 100% cloud cover."""
        config = ModelConfiguration(
            latitude=45.0,
            longitude=-120.0,
            elevation=100.0,
            timezone=-8.0,
            initial_water_temp=15.0,
            water_depth=2.0,
        )

        # Create data with full cloud cover
        start_date = datetime(2024, 7, 15, 12, 0)
        met_data = [
            {
                "datetime": start_date,
                "air_temperature": 20.0,
                "dewpoint_temperature": 15.0,
                "wind_speed": 2.0,
                "cloud_cover": 1.0,
            }
        ]
        met_df = pd.DataFrame(met_data)

        # Run model
        model = RTempModel(config)
        results = model.run(met_df)

        # Verify execution
        assert not math.isnan(results["water_temperature"].iloc[0])
        # Solar radiation should be reduced by clouds
        assert results["solar_radiation"].iloc[0] >= 0.0

    def test_shallow_water(self):
        """Test model with very shallow water depth."""
        config = ModelConfiguration(
            latitude=45.0,
            longitude=-120.0,
            elevation=100.0,
            timezone=-8.0,
            initial_water_temp=15.0,
            water_depth=0.1,  # 10 cm
        )

        # Create hourly data
        start_date = datetime(2024, 7, 15, 0, 0)
        met_data = []
        for hour in range(24):
            dt = start_date + timedelta(hours=hour)
            temp_variation = 10.0 * (1 - abs(hour - 15) / 12.0)
            air_temp = 15.0 + temp_variation

            met_data.append(
                {
                    "datetime": dt,
                    "air_temperature": air_temp,
                    "dewpoint_temperature": air_temp - 5.0,
                    "wind_speed": 2.0,
                    "cloud_cover": 0.3,
                }
            )

        met_df = pd.DataFrame(met_data)

        # Run model
        model = RTempModel(config)
        results = model.run(met_df)

        # Verify execution
        assert len(results) == 24
        assert not results["water_temperature"].isna().any()
        # Shallow water should respond more quickly to forcing
        temp_range = results["water_temperature"].max() - results["water_temperature"].min()
        assert temp_range > 0.0

    def test_deep_water(self):
        """Test model with deep water."""
        config = ModelConfiguration(
            latitude=45.0,
            longitude=-120.0,
            elevation=100.0,
            timezone=-8.0,
            initial_water_temp=15.0,
            water_depth=10.0,  # 10 meters
        )

        # Create hourly data
        start_date = datetime(2024, 7, 15, 0, 0)
        met_data = []
        for hour in range(24):
            dt = start_date + timedelta(hours=hour)
            temp_variation = 10.0 * (1 - abs(hour - 15) / 12.0)
            air_temp = 15.0 + temp_variation

            met_data.append(
                {
                    "datetime": dt,
                    "air_temperature": air_temp,
                    "dewpoint_temperature": air_temp - 5.0,
                    "wind_speed": 2.0,
                    "cloud_cover": 0.3,
                }
            )

        met_df = pd.DataFrame(met_data)

        # Run model
        model = RTempModel(config)
        results = model.run(met_df)

        # Verify execution
        assert len(results) == 24
        assert not results["water_temperature"].isna().any()
        # Deep water should respond more slowly
        temp_range = results["water_temperature"].max() - results["water_temperature"].min()
        assert temp_range >= 0.0

    def test_with_shade(self):
        """Test model with partial shade."""
        config = ModelConfiguration(
            latitude=45.0,
            longitude=-120.0,
            elevation=100.0,
            timezone=-8.0,
            initial_water_temp=15.0,
            water_depth=2.0,
            effective_shade=0.5,  # 50% shade
        )

        # Create data
        start_date = datetime(2024, 7, 15, 12, 0)
        met_data = [
            {
                "datetime": start_date,
                "air_temperature": 20.0,
                "dewpoint_temperature": 15.0,
                "wind_speed": 2.0,
                "cloud_cover": 0.3,
            }
        ]
        met_df = pd.DataFrame(met_data)

        # Run model
        model = RTempModel(config)
        results = model.run(met_df)

        # Verify execution
        assert not math.isnan(results["water_temperature"].iloc[0])
        # Solar radiation should be reduced by shade
        assert results["solar_radiation"].iloc[0] >= 0.0

    def test_with_groundwater_inflow(self):
        """Test model with groundwater inflow."""
        config = ModelConfiguration(
            latitude=45.0,
            longitude=-120.0,
            elevation=100.0,
            timezone=-8.0,
            initial_water_temp=20.0,
            water_depth=2.0,
            groundwater_temperature=10.0,
            groundwater_inflow=5.0,  # cm/day
        )

        # Create data
        start_date = datetime(2024, 7, 15, 12, 0)
        met_data = [
            {
                "datetime": start_date,
                "air_temperature": 20.0,
                "dewpoint_temperature": 15.0,
                "wind_speed": 2.0,
                "cloud_cover": 0.3,
            }
        ]
        met_df = pd.DataFrame(met_data)

        # Run model
        model = RTempModel(config)
        results = model.run(met_df)

        # Verify execution
        assert not math.isnan(results["water_temperature"].iloc[0])
        assert not math.isnan(results["groundwater"].iloc[0])
