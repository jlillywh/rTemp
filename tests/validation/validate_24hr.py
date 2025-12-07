"""
24-hour validation comparing Python rTemp with VBA output.
Focuses on the first day (October 1, 2003) for detailed analysis.
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

from rtemp import ModelConfiguration, RTempModel


def main():
    """Run 24-hour validation."""

    print("=" * 80)
    print("24-HOUR VBA VALIDATION (October 1, 2003)")
    print("=" * 80)
    print()

    # Get file paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    fixtures_dir = os.path.join(script_dir, "..", "fixtures")

    # Load VBA data
    vba_output = pd.read_csv(os.path.join(fixtures_dir, "vba_ts_output.csv"), skiprows=1)
    vba_output["datetime"] = pd.to_datetime(vba_output["date-time"])

    vba_input = pd.read_csv(os.path.join(fixtures_dir, "vba_ts_input.csv"), skiprows=1)
    vba_input["datetime"] = pd.to_datetime(
        vba_input[["year", "month", "day", "hour", "minute"]].rename(
            columns={
                "year": "year",
                "month": "month",
                "day": "day",
                "hour": "hour",
                "minute": "minute",
            }
        )
    )

    # Filter to first 24 hours (96 timesteps at 15-minute intervals)
    start_time = datetime(2003, 10, 1, 0, 0)
    end_time = start_time + timedelta(hours=24)

    vba_output_24hr = vba_output[
        (vba_output["datetime"] >= start_time) & (vba_output["datetime"] < end_time)
    ].copy()

    vba_input_24hr = vba_input[
        (vba_input["datetime"] >= start_time) & (vba_input["datetime"] < end_time)
    ].copy()

    print(f"Time period: {start_time} to {end_time}")
    print(f"Timesteps: {len(vba_output_24hr)} (15-minute intervals)")
    print()

    # Prepare met data for Python
    # Include measured solar radiation from VBA input
    met_data = vba_input_24hr[
        [
            "datetime",
            "air temperature (deg C)",
            "dewpoint temperature (deg C)",
            "wind speed (m/s)",
            "cloud cover (fraction)",
            "shortwave solar radiation before shade and reflection (W/m^2)",
        ]
    ].copy()
    met_data.columns = [
        "datetime",
        "air_temperature",
        "dewpoint_temperature",
        "wind_speed",
        "cloud_cover",
        "solar_radiation",
    ]

    # Create model configuration
    config = ModelConfiguration(
        latitude=48.45,
        longitude=-122.33,
        elevation=100.0,
        timezone=-8.0,
        daylight_savings=0,
        initial_water_temp=12.0,
        initial_sediment_temp=12.0,
        minimum_temperature=0.0,
        water_depth=0.4,
        effective_shade=0.15,
        wind_height=10.0,
        effective_wind_factor=1.0,
        sediment_thermal_conductivity=1.57,
        sediment_thermal_diffusivity=0.00645,
        sediment_thickness=10.0,
        hyporheic_exchange_rate=0.0,
        groundwater_temperature=10.0,
        groundwater_inflow=0.0,
        solar_method="Bras",
        longwave_method="Brutsaert",
        wind_function_method="Brady-Graves-Geyer",
        atmospheric_turbidity=2.0,
        atmospheric_transmission_coeff=0.8,
        brutsaert_coefficient=1.24,
        solar_cloud_kcl1=0.65,
        solar_cloud_kcl2=2.0,
        longwave_cloud_method="Eqn 1",
        longwave_cloud_kcl3=0.17,
        longwave_cloud_kcl4=2.0,
        stability_criteria=0.5,
        enable_diagnostics=False,
    )

    # Run Python model
    print("Running Python rTemp model...")
    model = RTempModel(config)
    python_results = model.run(met_data)
    print(f"  Generated {len(python_results)} output records")
    print()

    # Export results
    output_csv = os.path.join(script_dir, "validate_24hr_output.csv")
    model.export_results(output_csv)
    print(f"Python results exported to: {output_csv}")
    print()

    # Rename VBA columns for easier comparison
    vba_output_24hr = vba_output_24hr.rename(
        columns={
            "solar azimuth (deg)": "solar_azimuth",
            "solar elevation (deg)": "solar_elevation",
            "potential solar radiation at the ground surface before shade and reflection (W/m^2)": "potential_solar",
            "solar radiation entering the water after shade and reflection (W/m^2)": "solar_radiation",
            "longwave atmospheric radiation (W/m^2)": "longwave_atmospheric",
            "longwave back radiation from water (W/m^2)": "longwave_back",
            "convection (W/m^2)": "convection",
            "evaporation (W/m^2)": "evaporation",
            "sediment conduction heat flux to the surface water (W/m^2)": "sediment_conduction",
            "response water temperature (deg C)": "water_temperature",
            "response sediment temperature (deg C)": "sediment_temperature",
        }
    )

    # Compare results
    print("=" * 80)
    print("COMPARISON: Python vs VBA (24 hours)")
    print("=" * 80)
    print()

    # Key fields to compare
    comparison_fields = [
        ("solar_elevation", "Solar Elevation (deg)"),
        ("potential_solar", "Potential Solar (W/m²)"),
        ("solar_radiation", "Solar Radiation (W/m²)"),
        ("longwave_atmospheric", "Longwave Atmospheric (W/m²)"),
        ("longwave_back", "Longwave Back (W/m²)"),
        ("convection", "Convection (W/m²)"),
        ("evaporation", "Evaporation (W/m²)"),
        ("sediment_conduction", "Sediment Conduction (W/m²)"),
        ("water_temperature", "Water Temperature (°C)"),
        ("sediment_temperature", "Sediment Temperature (°C)"),
    ]

    # Calculate statistics
    stats = []
    for field, label in comparison_fields:
        if field == "potential_solar":
            # Python doesn't output potential solar, skip
            continue

        vba_vals = vba_output_24hr[field].values
        python_vals = python_results[field].values

        diff = python_vals - vba_vals
        abs_diff = np.abs(diff)

        stats.append(
            {
                "field": label,
                "vba_mean": np.mean(vba_vals),
                "python_mean": np.mean(python_vals),
                "vba_min": np.min(vba_vals),
                "vba_max": np.max(vba_vals),
                "python_min": np.min(python_vals),
                "python_max": np.max(python_vals),
                "max_abs_diff": np.max(abs_diff),
                "mean_abs_diff": np.mean(abs_diff),
                "rmse": np.sqrt(np.mean(diff**2)),
            }
        )

        print(f"{label}:")
        print(
            f"  VBA:    mean={np.mean(vba_vals):8.2f}  min={np.min(vba_vals):8.2f}  max={np.max(vba_vals):8.2f}"
        )
        print(
            f"  Python: mean={np.mean(python_vals):8.2f}  min={np.min(python_vals):8.2f}  max={np.max(python_vals):8.2f}"
        )
        print(
            f"  Diff:   mean={np.mean(diff):8.2f}  max_abs={np.max(abs_diff):8.2f}  RMSE={np.sqrt(np.mean(diff**2)):8.2f}"
        )
        print()

    # Detailed comparison at key times
    print("=" * 80)
    print("DETAILED COMPARISON AT KEY TIMES")
    print("=" * 80)
    print()

    # Midnight, sunrise, noon, sunset, midnight
    key_times = [
        0,  # 00:00 - Midnight
        24,  # 06:00 - Early morning
        37,  # 09:15 - Morning (first daytime in VBA data)
        48,  # 12:00 - Noon
        60,  # 15:00 - Afternoon
        72,  # 18:00 - Evening
        95,  # 23:45 - End of day
    ]

    for idx in key_times:
        if idx >= len(python_results):
            continue

        print(f"Time: {python_results['datetime'].iloc[idx]}")
        print("-" * 80)

        for field, label in comparison_fields:
            if field == "potential_solar":
                vba_val = vba_output_24hr[field].iloc[idx]
                print(f"  {label:30s}  VBA: {vba_val:10.2f}  (Python: N/A)")
            else:
                vba_val = vba_output_24hr[field].iloc[idx]
                python_val = python_results[field].iloc[idx]
                diff = python_val - vba_val
                print(
                    f"  {label:30s}  VBA: {vba_val:10.2f}  Python: {python_val:10.2f}  Diff: {diff:10.2f}"
                )
        print()

    # Summary table
    print("=" * 80)
    print("SUMMARY TABLE")
    print("=" * 80)
    print()
    print(f"{'Parameter':<30} {'VBA Mean':>10} {'Py Mean':>10} {'Max Diff':>10} {'RMSE':>10}")
    print("-" * 80)
    for s in stats:
        print(
            f"{s['field']:<30} {s['vba_mean']:10.2f} {s['python_mean']:10.2f} "
            f"{s['max_abs_diff']:10.2f} {s['rmse']:10.2f}"
        )
    print()

    print("=" * 80)
    print("24-Hour Validation Complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
