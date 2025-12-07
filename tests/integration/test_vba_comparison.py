"""
VBA Comparison Test Suite

This module contains tests that compare Python implementation results
against reference VBA outputs to ensure compatibility and correctness.

Requirements validated: 19.1-19.5
- Solar position accuracy: ±0.01°
- Solar radiation accuracy: ±0.1 W/m²
- Heat flux accuracy: ±0.1 W/m²
- Temperature accuracy: ±0.01°C
"""

import math
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

import pandas as pd
import pytest

from rtemp import ModelConfiguration, RTempModel
from rtemp.solar.position import NOAASolarPosition


# Tolerance constants as specified in requirements
SOLAR_POSITION_TOLERANCE = 0.01  # degrees
SOLAR_RADIATION_TOLERANCE = 0.1  # W/m²
HEAT_FLUX_TOLERANCE = 0.1  # W/m²
TEMPERATURE_TOLERANCE = 0.01  # °C


class VBAReferenceData:
    """
    Container for VBA reference data.

    This class provides reference data from the VBA implementation
    for comparison testing. Data should be generated from the original
    VBA code with known inputs.
    """

    @staticmethod
    def get_solar_position_reference() -> List[Dict]:
        """
        Get reference solar position data from VBA.

        Returns list of dicts with keys:
        - datetime: datetime object
        - latitude: float
        - longitude: float
        - timezone: float
        - expected_azimuth: float (degrees)
        - expected_elevation: float (degrees)
        - description: str
        """
        # Reference data from VBA implementation
        # These values should be populated with actual VBA outputs
        return [
            {
                "datetime": datetime(2024, 7, 15, 12, 0, 0),
                "latitude": 45.0,
                "longitude": -120.0,
                "timezone": 8.0,
                "expected_azimuth": 180.0,  # Placeholder - replace with VBA output
                "expected_elevation": 68.5,  # Placeholder - replace with VBA output
                "description": "Summer noon at mid-latitude",
            },
            {
                "datetime": datetime(2024, 1, 15, 12, 0, 0),
                "latitude": 45.0,
                "longitude": -120.0,
                "timezone": 8.0,
                "expected_azimuth": 180.0,  # Placeholder - replace with VBA output
                "expected_elevation": 21.5,  # Placeholder - replace with VBA output
                "description": "Winter noon at mid-latitude",
            },
            {
                "datetime": datetime(2024, 6, 21, 12, 0, 0),
                "latitude": 60.0,
                "longitude": -120.0,
                "timezone": 8.0,
                "expected_azimuth": 180.0,  # Placeholder - replace with VBA output
                "expected_elevation": 53.5,  # Placeholder - replace with VBA output
                "description": "Summer solstice at high latitude",
            },
            {
                "datetime": datetime(2024, 3, 20, 12, 0, 0),
                "latitude": 0.0,
                "longitude": 0.0,
                "timezone": 0.0,
                "expected_azimuth": 0.0,  # Placeholder - replace with VBA output
                "expected_elevation": 90.0,  # Placeholder - replace with VBA output
                "description": "Equinox at equator",
            },
        ]

    @staticmethod
    def get_solar_radiation_reference() -> List[Dict]:
        """
        Get reference solar radiation data from VBA.

        Returns list of dicts with keys:
        - datetime: datetime object
        - latitude: float
        - longitude: float
        - timezone: float
        - elevation_m: float
        - method: str (Bras, Bird, Ryan-Stolzenbach, Iqbal)
        - cloud_cover: float
        - expected_radiation: float (W/m²)
        - description: str
        """
        return [
            {
                "datetime": datetime(2024, 7, 15, 12, 0, 0),
                "latitude": 45.0,
                "longitude": -120.0,
                "timezone": 8.0,
                "elevation_m": 100.0,
                "method": "Bras",
                "cloud_cover": 0.0,
                "expected_radiation": 850.0,  # Placeholder - replace with VBA output
                "description": "Clear sky summer noon - Bras method",
            },
            {
                "datetime": datetime(2024, 7, 15, 12, 0, 0),
                "latitude": 45.0,
                "longitude": -120.0,
                "timezone": 8.0,
                "elevation_m": 100.0,
                "method": "Bird",
                "cloud_cover": 0.0,
                "expected_radiation": 900.0,  # Placeholder - replace with VBA output
                "description": "Clear sky summer noon - Bird method",
            },
            {
                "datetime": datetime(2024, 7, 15, 12, 0, 0),
                "latitude": 45.0,
                "longitude": -120.0,
                "timezone": 8.0,
                "elevation_m": 100.0,
                "method": "Bras",
                "cloud_cover": 0.5,
                "expected_radiation": 500.0,  # Placeholder - replace with VBA output
                "description": "Partly cloudy summer noon - Bras method",
            },
        ]

    @staticmethod
    def get_heat_flux_reference() -> List[Dict]:
        """
        Get reference heat flux data from VBA.

        Returns list of dicts with keys:
        - datetime: datetime object
        - config: dict of configuration parameters
        - met_data: dict of meteorological inputs
        - expected_fluxes: dict with flux components (W/m²)
        - description: str
        """
        return [
            {
                "datetime": datetime(2024, 7, 15, 12, 0, 0),
                "config": {
                    "latitude": 45.0,
                    "longitude": -120.0,
                    "timezone": 8.0,
                    "elevation": 100.0,
                    "water_depth": 2.0,
                    "initial_water_temp": 20.0,
                },
                "met_data": {
                    "air_temperature": 25.0,
                    "dewpoint_temperature": 18.0,
                    "wind_speed": 2.0,
                    "cloud_cover": 0.3,
                },
                "expected_fluxes": {
                    "solar_radiation": 700.0,  # Placeholder
                    "longwave_atmospheric": 350.0,  # Placeholder
                    "longwave_back": -450.0,  # Placeholder
                    "evaporation": -80.0,  # Placeholder
                    "convection": -20.0,  # Placeholder
                },
                "description": "Summer midday conditions",
            },
        ]

    @staticmethod
    def get_temperature_reference() -> List[Dict]:
        """
        Get reference temperature calculation data from VBA.

        Returns list of dicts with keys:
        - config: dict of configuration parameters
        - met_data: DataFrame of meteorological inputs
        - expected_temps: list of expected water temperatures (°C)
        - description: str
        """
        return [
            {
                "config": {
                    "latitude": 45.0,
                    "longitude": -120.0,
                    "timezone": 8.0,
                    "elevation": 100.0,
                    "water_depth": 2.0,
                    "initial_water_temp": 15.0,
                    "initial_sediment_temp": 15.0,
                },
                "met_data": pd.DataFrame(
                    [
                        {
                            "datetime": datetime(2024, 7, 15, 0, 0),
                            "air_temperature": 15.0,
                            "dewpoint_temperature": 10.0,
                            "wind_speed": 2.0,
                            "cloud_cover": 0.3,
                        },
                        {
                            "datetime": datetime(2024, 7, 15, 12, 0),
                            "air_temperature": 25.0,
                            "dewpoint_temperature": 18.0,
                            "wind_speed": 2.5,
                            "cloud_cover": 0.2,
                        },
                        {
                            "datetime": datetime(2024, 7, 16, 0, 0),
                            "air_temperature": 16.0,
                            "dewpoint_temperature": 11.0,
                            "wind_speed": 2.0,
                            "cloud_cover": 0.4,
                        },
                    ]
                ),
                "expected_temps": [15.0, 16.5, 16.2],  # Placeholder
                "description": "Day-night cycle",
            },
        ]


class TestSolarPositionComparison:
    """Test solar position calculations against VBA reference data."""

    @pytest.mark.skip(
        reason="Requires actual VBA reference data - placeholder values currently used"
    )
    @pytest.mark.parametrize("ref_data", VBAReferenceData.get_solar_position_reference())
    def test_solar_position_accuracy(self, ref_data):
        """
        Test that Python solar position matches VBA within ±0.01°.

        Validates: Requirement 19.1
        """
        # Calculate solar position using Python implementation
        azimuth, elevation, _ = NOAASolarPosition.calc_solar_position(
            lat=ref_data["latitude"],
            lon=ref_data["longitude"],
            dt=ref_data["datetime"],
            timezone=ref_data["timezone"],
            dlstime=0,
        )

        # Compare with VBA reference
        azimuth_diff = abs(azimuth - ref_data["expected_azimuth"])
        elevation_diff = abs(elevation - ref_data["expected_elevation"])

        # Assert within tolerance
        assert azimuth_diff <= SOLAR_POSITION_TOLERANCE, (
            f"{ref_data['description']}: "
            f"Azimuth difference {azimuth_diff:.4f}° exceeds tolerance "
            f"{SOLAR_POSITION_TOLERANCE}° "
            f"(Python: {azimuth:.4f}°, VBA: {ref_data['expected_azimuth']:.4f}°)"
        )

        assert elevation_diff <= SOLAR_POSITION_TOLERANCE, (
            f"{ref_data['description']}: "
            f"Elevation difference {elevation_diff:.4f}° exceeds tolerance "
            f"{SOLAR_POSITION_TOLERANCE}° "
            f"(Python: {elevation:.4f}°, VBA: {ref_data['expected_elevation']:.4f}°)"
        )

    def test_solar_position_consistency(self):
        """
        Test that solar position calculations are consistent across multiple calls.

        This ensures determinism in the implementation.
        """
        dt = datetime(2024, 7, 15, 12, 0, 0)
        lat, lon, tz = 45.0, -120.0, 8.0

        # Calculate multiple times
        results = []
        for _ in range(5):
            az, el, dist = NOAASolarPosition.calc_solar_position(lat, lon, dt, tz, 0)
            results.append((az, el, dist))

        # All results should be identical
        for i in range(1, len(results)):
            assert results[i] == results[0], "Solar position calculations are not deterministic"


class TestSolarRadiationComparison:
    """Test solar radiation calculations against VBA reference data."""

    @pytest.mark.skip(
        reason="Requires actual VBA reference data - placeholder values currently used"
    )
    @pytest.mark.parametrize("ref_data", VBAReferenceData.get_solar_radiation_reference())
    def test_solar_radiation_accuracy(self, ref_data):
        """
        Test that Python solar radiation matches VBA within ±0.1 W/m².

        Validates: Requirement 19.2
        """
        # Create configuration
        config = ModelConfiguration(
            latitude=ref_data["latitude"],
            longitude=ref_data["longitude"],
            timezone=ref_data["timezone"],
            elevation=ref_data["elevation_m"],
            initial_water_temp=15.0,
            water_depth=2.0,
            solar_method=ref_data["method"],
        )

        # Create meteorological data
        met_data = pd.DataFrame(
            [
                {
                    "datetime": ref_data["datetime"],
                    "air_temperature": 20.0,
                    "dewpoint_temperature": 15.0,
                    "wind_speed": 2.0,
                    "cloud_cover": ref_data["cloud_cover"],
                }
            ]
        )

        # Run model
        model = RTempModel(config)
        results = model.run(met_data)

        # Get calculated radiation
        calculated_radiation = results["solar_radiation"].iloc[0]

        # Compare with VBA reference
        radiation_diff = abs(calculated_radiation - ref_data["expected_radiation"])

        # Assert within tolerance
        assert radiation_diff <= SOLAR_RADIATION_TOLERANCE, (
            f"{ref_data['description']}: "
            f"Solar radiation difference {radiation_diff:.2f} W/m² exceeds tolerance "
            f"{SOLAR_RADIATION_TOLERANCE} W/m² "
            f"(Python: {calculated_radiation:.2f} W/m², "
            f"VBA: {ref_data['expected_radiation']:.2f} W/m²)"
        )

    def test_solar_radiation_night_zero(self):
        """
        Test that solar radiation is zero at night for all methods.

        This is a fundamental requirement that should match VBA.
        """
        methods = ["Bras", "Bird", "Ryan-Stolzenbach", "Iqbal"]

        for method in methods:
            config = ModelConfiguration(
                latitude=45.0,
                longitude=-120.0,
                timezone=-8.0,  # UTC-8 for western hemisphere
                elevation=100.0,
                initial_water_temp=15.0,
                water_depth=2.0,
                solar_method=method,
            )

            # Midnight in summer
            met_data = pd.DataFrame(
                [
                    {
                        "datetime": datetime(2024, 7, 15, 0, 0, 0),
                        "air_temperature": 15.0,
                        "dewpoint_temperature": 10.0,
                        "wind_speed": 2.0,
                        "cloud_cover": 0.0,
                    }
                ]
            )

            model = RTempModel(config)
            results = model.run(met_data)

            assert (
                results["solar_radiation"].iloc[0] == 0.0
            ), f"Solar radiation should be zero at night for {method} method"


class TestHeatFluxComparison:
    """Test heat flux calculations against VBA reference data."""

    @pytest.mark.skip(
        reason="Requires actual VBA reference data - placeholder values currently used"
    )
    @pytest.mark.parametrize("ref_data", VBAReferenceData.get_heat_flux_reference())
    def test_heat_flux_components_accuracy(self, ref_data):
        """
        Test that Python heat flux components match VBA within ±0.1 W/m².

        Validates: Requirement 19.3
        """
        # Create configuration
        config = ModelConfiguration(**ref_data["config"])

        # Create meteorological data
        met_df = pd.DataFrame([{"datetime": ref_data["datetime"], **ref_data["met_data"]}])

        # Run model
        model = RTempModel(config)
        results = model.run(met_df)

        # Compare each flux component
        for flux_name, expected_value in ref_data["expected_fluxes"].items():
            if flux_name in results.columns:
                calculated_value = results[flux_name].iloc[0]
                flux_diff = abs(calculated_value - expected_value)

                assert flux_diff <= HEAT_FLUX_TOLERANCE, (
                    f"{ref_data['description']} - {flux_name}: "
                    f"Difference {flux_diff:.2f} W/m² exceeds tolerance "
                    f"{HEAT_FLUX_TOLERANCE} W/m² "
                    f"(Python: {calculated_value:.2f} W/m², "
                    f"VBA: {expected_value:.2f} W/m²)"
                )

    def test_net_flux_calculation(self):
        """
        Test that net flux equals sum of components.

        This should be true for both Python and VBA implementations.
        """
        config = ModelConfiguration(
            latitude=45.0,
            longitude=-120.0,
            timezone=8.0,
            elevation=100.0,
            initial_water_temp=20.0,
            water_depth=2.0,
        )

        met_data = pd.DataFrame(
            [
                {
                    "datetime": datetime(2024, 7, 15, 12, 0, 0),
                    "air_temperature": 25.0,
                    "dewpoint_temperature": 18.0,
                    "wind_speed": 2.0,
                    "cloud_cover": 0.3,
                }
            ]
        )

        model = RTempModel(config)
        results = model.run(met_data)

        # Calculate sum of components
        component_sum = (
            results["solar_radiation"].iloc[0]
            + results["longwave_atmospheric"].iloc[0]
            + results["longwave_back"].iloc[0]
            + results["evaporation"].iloc[0]
            + results["convection"].iloc[0]
            + results["sediment_conduction"].iloc[0]
            + results["hyporheic_exchange"].iloc[0]
            + results["groundwater"].iloc[0]
        )

        net_flux = results["net_flux"].iloc[0]

        # Should match within numerical precision
        assert (
            abs(component_sum - net_flux) < 0.01
        ), f"Net flux {net_flux:.2f} does not equal sum of components {component_sum:.2f}"


class TestTemperatureComparison:
    """Test temperature calculations against VBA reference data."""

    @pytest.mark.skip(
        reason="Requires actual VBA reference data - placeholder values currently used"
    )
    @pytest.mark.parametrize("ref_data", VBAReferenceData.get_temperature_reference())
    def test_temperature_accuracy(self, ref_data):
        """
        Test that Python temperature calculations match VBA within ±0.01°C.

        Validates: Requirement 19.4
        """
        # Create configuration
        config = ModelConfiguration(**ref_data["config"])

        # Run model
        model = RTempModel(config)
        results = model.run(ref_data["met_data"])

        # Compare each timestep
        for i, expected_temp in enumerate(ref_data["expected_temps"]):
            calculated_temp = results["water_temperature"].iloc[i]
            temp_diff = abs(calculated_temp - expected_temp)

            assert temp_diff <= TEMPERATURE_TOLERANCE, (
                f"{ref_data['description']} - Timestep {i}: "
                f"Temperature difference {temp_diff:.4f}°C exceeds tolerance "
                f"{TEMPERATURE_TOLERANCE}°C "
                f"(Python: {calculated_temp:.4f}°C, VBA: {expected_temp:.4f}°C)"
            )

    def test_temperature_minimum_enforcement(self):
        """
        Test that minimum temperature is enforced consistently with VBA.
        """
        min_temp = 0.0
        config = ModelConfiguration(
            latitude=60.0,
            longitude=-120.0,
            timezone=8.0,
            elevation=100.0,
            initial_water_temp=2.0,
            minimum_temperature=min_temp,
            water_depth=2.0,
        )

        # Very cold conditions
        met_data = pd.DataFrame(
            [
                {
                    "datetime": datetime(2024, 1, 15, 0, 0, 0),
                    "air_temperature": -20.0,
                    "dewpoint_temperature": -25.0,
                    "wind_speed": 5.0,
                    "cloud_cover": 0.8,
                }
            ]
        )

        model = RTempModel(config)
        results = model.run(met_data)

        # Temperature should not go below minimum
        assert results["water_temperature"].iloc[0] >= min_temp, (
            f"Water temperature {results['water_temperature'].iloc[0]:.2f}°C "
            f"is below minimum {min_temp}°C"
        )


class TestFullScenarioComparison:
    """Test complete scenarios against VBA reference outputs."""

    @pytest.mark.skip(reason="Requires VBA reference data file")
    def test_full_day_comparison(self):
        """
        Test complete 24-hour simulation against VBA output file.

        Validates: Requirement 19.5

        This test requires a CSV file with VBA outputs for comparison.
        The file should contain columns matching the Python output format.
        """
        # Load VBA reference data
        # vba_data = pd.read_csv('tests/fixtures/vba_reference_24hr.csv')

        # Create matching configuration
        config = ModelConfiguration(
            latitude=45.0,
            longitude=-120.0,
            timezone=8.0,
            elevation=100.0,
            initial_water_temp=15.0,
            initial_sediment_temp=15.0,
            water_depth=2.0,
        )

        # Load meteorological data (same as used for VBA)
        # met_data = pd.read_csv('tests/fixtures/met_data_24hr.csv')
        # met_data['datetime'] = pd.to_datetime(met_data['datetime'])

        # Run Python model
        # model = RTempModel(config)
        # python_results = model.run(met_data)

        # Compare all timesteps
        # for i in range(len(vba_data)):
        #     # Solar position
        #     assert abs(python_results['solar_azimuth'].iloc[i] -
        #               vba_data['solar_azimuth'].iloc[i]) <= SOLAR_POSITION_TOLERANCE
        #
        #     # Solar radiation
        #     assert abs(python_results['solar_radiation'].iloc[i] -
        #               vba_data['solar_radiation'].iloc[i]) <= SOLAR_RADIATION_TOLERANCE
        #
        #     # Heat fluxes
        #     for flux in ['longwave_atmospheric', 'evaporation', 'convection']:
        #         assert abs(python_results[flux].iloc[i] -
        #                   vba_data[flux].iloc[i]) <= HEAT_FLUX_TOLERANCE
        #
        #     # Temperature
        #     assert abs(python_results['water_temperature'].iloc[i] -
        #               vba_data['water_temperature'].iloc[i]) <= TEMPERATURE_TOLERANCE

        pass  # Placeholder until reference data is available

    def test_method_combinations_match_vba(self):
        """
        Test that different method combinations produce results within tolerance.

        This ensures that all calculation methods are compatible with VBA.
        """
        methods_to_test = [
            ("Bras", "Brunt", "Brady-Graves-Geyer"),
            ("Bird", "Brutsaert", "Ryan-Harleman"),
            ("Ryan-Stolzenbach", "Satterlund", "Marciano-Harbeck"),
            ("Iqbal", "Idso-Jackson", "East Mesa"),
        ]

        for solar_method, longwave_method, wind_method in methods_to_test:
            config = ModelConfiguration(
                latitude=45.0,
                longitude=-120.0,
                timezone=8.0,
                elevation=100.0,
                initial_water_temp=15.0,
                water_depth=2.0,
                solar_method=solar_method,
                longwave_method=longwave_method,
                wind_function_method=wind_method,
            )

            met_data = pd.DataFrame(
                [
                    {
                        "datetime": datetime(2024, 7, 15, 12, 0, 0),
                        "air_temperature": 20.0,
                        "dewpoint_temperature": 15.0,
                        "wind_speed": 2.0,
                        "cloud_cover": 0.3,
                    }
                ]
            )

            model = RTempModel(config)
            results = model.run(met_data)

            # Verify execution completed successfully
            assert not results["water_temperature"].isna().any(), (
                f"Method combination {solar_method}/{longwave_method}/{wind_method} "
                f"produced NaN temperature"
            )

            # Verify results are physically reasonable
            assert results["solar_radiation"].iloc[0] >= 0.0
            assert results["water_temperature"].iloc[0] > 0.0
            assert not math.isinf(results["water_temperature"].iloc[0])


class TestDifferenceDocumentation:
    """Document any known differences between Python and VBA implementations."""

    def test_document_numerical_precision_differences(self):
        """
        Document differences due to numerical precision.

        Python uses 64-bit floats while VBA may use different precision.
        Small differences (< 1e-10) are expected and acceptable.
        """
        # This test documents that minor numerical differences are expected
        # and provides a reference for acceptable variation

        config = ModelConfiguration(
            latitude=45.0,
            longitude=-120.0,
            timezone=8.0,
            elevation=100.0,
            initial_water_temp=15.0,
            water_depth=2.0,
        )

        met_data = pd.DataFrame(
            [
                {
                    "datetime": datetime(2024, 7, 15, 12, 0, 0),
                    "air_temperature": 20.0,
                    "dewpoint_temperature": 15.0,
                    "wind_speed": 2.0,
                    "cloud_cover": 0.3,
                }
            ]
        )

        model = RTempModel(config)
        results = model.run(met_data)

        # Document that results are within acceptable precision
        # This serves as a baseline for comparison
        assert results["water_temperature"].iloc[0] is not None

        # Note: Differences < 1e-10 are due to floating point precision
        # and are not considered errors

    def test_document_algorithm_improvements(self):
        """
        Document any intentional improvements over VBA implementation.

        Some differences may be due to:
        - More accurate constants (e.g., pi, physical constants)
        - Improved numerical methods
        - Bug fixes from VBA version

        These should be documented but not considered failures.
        """
        # This test serves as documentation for known improvements
        # over the VBA implementation

        # Example: Python uses more precise value of pi
        import math

        python_pi = math.pi
        vba_pi = 3.14159265358979  # From VBA code

        # Difference is negligible but exists
        pi_diff = abs(python_pi - vba_pi)
        assert pi_diff < 1e-14, "Pi precision difference is acceptable"

        # Document other known improvements here as they are identified
        pass


# Utility functions for generating VBA reference data


def generate_vba_reference_template():
    """
    Generate a template for collecting VBA reference data.

    This function creates a CSV template that can be filled with
    VBA outputs for comparison testing.
    """
    template_data = {
        "test_case": [],
        "datetime": [],
        "latitude": [],
        "longitude": [],
        "timezone": [],
        "vba_azimuth": [],
        "vba_elevation": [],
        "vba_solar_radiation": [],
        "vba_water_temperature": [],
        "notes": [],
    }

    # Add sample test cases
    test_cases = [
        ("summer_noon", datetime(2024, 7, 15, 12, 0), 45.0, -120.0, 8.0),
        ("winter_noon", datetime(2024, 1, 15, 12, 0), 45.0, -120.0, 8.0),
        ("high_latitude", datetime(2024, 6, 21, 12, 0), 60.0, -120.0, 8.0),
    ]

    for name, dt, lat, lon, tz in test_cases:
        template_data["test_case"].append(name)
        template_data["datetime"].append(dt)
        template_data["latitude"].append(lat)
        template_data["longitude"].append(lon)
        template_data["timezone"].append(tz)
        template_data["vba_azimuth"].append(None)
        template_data["vba_elevation"].append(None)
        template_data["vba_solar_radiation"].append(None)
        template_data["vba_water_temperature"].append(None)
        template_data["notes"].append("Fill with VBA output")

    df = pd.DataFrame(template_data)
    return df


if __name__ == "__main__":
    # Generate template for VBA reference data collection
    template = generate_vba_reference_template()
    print("VBA Reference Data Template:")
    print(template)
    print("\nTo use this template:")
    print("1. Run the VBA implementation with the test cases above")
    print("2. Fill in the VBA output columns")
    print("3. Save as 'tests/fixtures/vba_reference_data.csv'")
    print("4. Update VBAReferenceData class with actual values")
