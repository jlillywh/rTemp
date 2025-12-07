"""
Generate templates for VBA reference data collection.

This script creates CSV templates that can be filled with VBA outputs
for comparison testing.
"""

from datetime import datetime, timedelta
import pandas as pd


def generate_solar_position_template():
    """Generate template for solar position reference data."""
    test_cases = [
        {
            "datetime": datetime(2024, 7, 15, 12, 0, 0),
            "latitude": 45.0,
            "longitude": -120.0,
            "timezone": 8.0,
            "description": "Summer noon at mid-latitude",
        },
        {
            "datetime": datetime(2024, 1, 15, 12, 0, 0),
            "latitude": 45.0,
            "longitude": -120.0,
            "timezone": 8.0,
            "description": "Winter noon at mid-latitude",
        },
        {
            "datetime": datetime(2024, 6, 21, 12, 0, 0),
            "latitude": 60.0,
            "longitude": -120.0,
            "timezone": 8.0,
            "description": "Summer solstice at high latitude",
        },
        {
            "datetime": datetime(2024, 12, 21, 12, 0, 0),
            "latitude": 60.0,
            "longitude": -120.0,
            "timezone": 8.0,
            "description": "Winter solstice at high latitude",
        },
        {
            "datetime": datetime(2024, 3, 20, 12, 0, 0),
            "latitude": 0.0,
            "longitude": 0.0,
            "timezone": 0.0,
            "description": "Equinox at equator",
        },
        {
            "datetime": datetime(2024, 7, 15, 6, 0, 0),
            "latitude": 45.0,
            "longitude": -120.0,
            "timezone": 8.0,
            "description": "Summer sunrise",
        },
        {
            "datetime": datetime(2024, 7, 15, 18, 0, 0),
            "latitude": 45.0,
            "longitude": -120.0,
            "timezone": 8.0,
            "description": "Summer sunset",
        },
    ]

    df = pd.DataFrame(test_cases)
    df["azimuth"] = None
    df["elevation"] = None
    df["notes"] = "Fill with VBA output"

    return df


def generate_solar_radiation_template():
    """Generate template for solar radiation reference data."""
    test_cases = []

    methods = ["Bras", "Bird", "Ryan-Stolzenbach", "Iqbal"]
    cloud_covers = [0.0, 0.3, 0.5, 1.0]

    for method in methods:
        for cloud_cover in cloud_covers:
            test_cases.append(
                {
                    "datetime": datetime(2024, 7, 15, 12, 0, 0),
                    "latitude": 45.0,
                    "longitude": -120.0,
                    "timezone": 8.0,
                    "elevation_m": 100.0,
                    "method": method,
                    "cloud_cover": cloud_cover,
                    "description": f"{method} method, cloud cover {cloud_cover}",
                }
            )

    df = pd.DataFrame(test_cases)
    df["solar_radiation"] = None
    df["notes"] = "Fill with VBA output"

    return df


def generate_heat_flux_template():
    """Generate template for heat flux reference data."""
    test_cases = [
        {
            "datetime": datetime(2024, 7, 15, 12, 0, 0),
            "latitude": 45.0,
            "longitude": -120.0,
            "timezone": 8.0,
            "elevation_m": 100.0,
            "water_depth": 2.0,
            "initial_water_temp": 20.0,
            "air_temperature": 25.0,
            "dewpoint_temperature": 18.0,
            "wind_speed": 2.0,
            "cloud_cover": 0.3,
            "description": "Summer midday conditions",
        },
        {
            "datetime": datetime(2024, 1, 15, 12, 0, 0),
            "latitude": 45.0,
            "longitude": -120.0,
            "timezone": 8.0,
            "elevation_m": 100.0,
            "water_depth": 2.0,
            "initial_water_temp": 5.0,
            "air_temperature": 0.0,
            "dewpoint_temperature": -5.0,
            "wind_speed": 3.0,
            "cloud_cover": 0.7,
            "description": "Winter midday conditions",
        },
        {
            "datetime": datetime(2024, 7, 15, 0, 0, 0),
            "latitude": 45.0,
            "longitude": -120.0,
            "timezone": 8.0,
            "elevation_m": 100.0,
            "water_depth": 2.0,
            "initial_water_temp": 18.0,
            "air_temperature": 15.0,
            "dewpoint_temperature": 10.0,
            "wind_speed": 2.0,
            "cloud_cover": 0.3,
            "description": "Summer night conditions",
        },
    ]

    df = pd.DataFrame(test_cases)
    df["solar_radiation"] = None
    df["longwave_atmospheric"] = None
    df["longwave_back"] = None
    df["evaporation"] = None
    df["convection"] = None
    df["sediment_conduction"] = None
    df["hyporheic_exchange"] = None
    df["groundwater"] = None
    df["net_flux"] = None
    df["notes"] = "Fill with VBA output"

    return df


def generate_temperature_template():
    """Generate template for temperature calculation reference data."""
    # Create 24-hour scenario
    start_date = datetime(2024, 7, 15, 0, 0, 0)
    test_cases = []

    for hour in range(25):  # 0 to 24 hours
        dt = start_date + timedelta(hours=hour)
        # Sinusoidal temperature variation
        temp_variation = 10.0 * (1 - abs(hour - 15) / 12.0) if hour <= 24 else 0
        air_temp = 15.0 + temp_variation

        test_cases.append(
            {
                "timestep": hour,
                "datetime": dt,
                "latitude": 45.0,
                "longitude": -120.0,
                "timezone": 8.0,
                "elevation_m": 100.0,
                "water_depth": 2.0,
                "initial_water_temp": 15.0 if hour == 0 else None,
                "air_temperature": air_temp,
                "dewpoint_temperature": air_temp - 5.0,
                "wind_speed": 2.0,
                "cloud_cover": 0.3,
            }
        )

    df = pd.DataFrame(test_cases)
    df["water_temperature"] = None
    df["sediment_temperature"] = None
    df["notes"] = "Fill with VBA output"

    return df


def generate_full_scenario_template():
    """Generate template for complete 24-hour scenario."""
    start_date = datetime(2024, 7, 15, 0, 0, 0)
    test_cases = []

    for hour in range(25):
        dt = start_date + timedelta(hours=hour)
        temp_variation = 10.0 * (1 - abs(hour - 15) / 12.0) if hour <= 24 else 0
        air_temp = 15.0 + temp_variation

        test_cases.append(
            {
                "timestep": hour,
                "datetime": dt,
                "air_temperature": air_temp,
                "dewpoint_temperature": air_temp - 5.0,
                "wind_speed": 2.0,
                "cloud_cover": 0.3,
            }
        )

    df = pd.DataFrame(test_cases)

    # Add all output columns
    output_columns = [
        "solar_azimuth",
        "solar_elevation",
        "solar_radiation",
        "longwave_atmospheric",
        "longwave_back",
        "evaporation",
        "convection",
        "sediment_conduction",
        "hyporheic_exchange",
        "groundwater",
        "net_flux",
        "water_temperature",
        "sediment_temperature",
    ]

    for col in output_columns:
        df[col] = None

    df["notes"] = "Fill with VBA output"

    return df


def main():
    """Generate all templates."""
    print("Generating VBA reference data templates...")

    # Generate templates
    solar_pos = generate_solar_position_template()
    solar_rad = generate_solar_radiation_template()
    heat_flux = generate_heat_flux_template()
    temperature = generate_temperature_template()
    full_scenario = generate_full_scenario_template()

    # Save to CSV
    solar_pos.to_csv("vba_solar_position_template.csv", index=False)
    print("✓ Created vba_solar_position_template.csv")

    solar_rad.to_csv("vba_solar_radiation_template.csv", index=False)
    print("✓ Created vba_solar_radiation_template.csv")

    heat_flux.to_csv("vba_heat_flux_template.csv", index=False)
    print("✓ Created vba_heat_flux_template.csv")

    temperature.to_csv("vba_temperature_template.csv", index=False)
    print("✓ Created vba_temperature_template.csv")

    full_scenario.to_csv("vba_full_scenario_template.csv", index=False)
    print("✓ Created vba_full_scenario_template.csv")

    print("\nTemplates created successfully!")
    print("\nNext steps:")
    print("1. Run VBA implementation with the test cases in each template")
    print("2. Fill in the VBA output columns")
    print("3. Save as vba_*_reference.csv (remove '_template' from filename)")
    print("4. Update VBAReferenceData class in test_vba_comparison.py")
    print("5. Run comparison tests: pytest tests/integration/test_vba_comparison.py")


if __name__ == "__main__":
    main()
