"""Debug solar radiation differences between Python and VBA."""

import pandas as pd
import numpy as np
import os
from datetime import datetime

from rtemp import ModelConfiguration, RTempModel
from rtemp.solar.position import NOAASolarPosition
from rtemp.solar.radiation_bras import SolarRadiationBras

# Load VBA data
script_dir = os.path.dirname(os.path.abspath(__file__))
fixtures_dir = os.path.join(script_dir, "..", "fixtures")

vba_output = pd.read_csv(os.path.join(fixtures_dir, "vba_ts_output.csv"), skiprows=1)
vba_output["datetime"] = pd.to_datetime(vba_output["date-time"])

vba_input = pd.read_csv(os.path.join(fixtures_dir, "vba_ts_input.csv"), skiprows=1)
vba_input["datetime"] = pd.to_datetime(
    vba_input[["year", "month", "day", "hour", "minute"]].rename(
        columns={"year": "year", "month": "month", "day": "day", "hour": "hour", "minute": "minute"}
    )
)

print("=" * 80)
print("SOLAR RADIATION DEBUG")
print("=" * 80)
print()

# Find a daytime timestep with significant solar radiation
daytime_mask = (
    vba_output["solar radiation entering the water after shade and reflection (W/m^2)"] > 100
)
daytime_indices = vba_output[daytime_mask].index[:5]

if len(daytime_indices) == 0:
    print("No daytime timesteps found with solar radiation > 100 W/m²")
    print("Checking all timesteps with solar radiation > 0:")
    daytime_mask = (
        vba_output["solar radiation entering the water after shade and reflection (W/m^2)"] > 0
    )
    daytime_indices = vba_output[daytime_mask].index[:10]

print(f"Found {len(daytime_indices)} daytime timesteps")
print()

# Configuration
config = ModelConfiguration(
    latitude=48.45,
    longitude=-122.33,
    elevation=100.0,
    timezone=-8.0,
    initial_water_temp=12.0,
    water_depth=0.4,
    effective_shade=0.15,
    solar_method="Bras",
    atmospheric_turbidity=2.0,
    solar_cloud_kcl1=0.65,
    solar_cloud_kcl2=2.0,
)

for idx in daytime_indices[:3]:
    dt = vba_output["datetime"].iloc[idx]
    vba_solar = vba_output[
        "solar radiation entering the water after shade and reflection (W/m^2)"
    ].iloc[idx]
    vba_potential = vba_output[
        "potential solar radiation at the ground surface before shade and reflection (W/m^2)"
    ].iloc[idx]
    vba_elevation = vba_output["solar elevation (deg)"].iloc[idx]

    # Get met data
    met_row = vba_input[vba_input["datetime"] == dt].iloc[0]
    cloud_cover = met_row["cloud cover (fraction)"]

    print(f"Timestep: {dt}")
    print(f"  VBA Solar Elevation: {vba_elevation:.2f}°")
    print(f"  VBA Potential Solar: {vba_potential:.2f} W/m²")
    print(f"  VBA Final Solar (after shade): {vba_solar:.2f} W/m²")
    print(f"  Cloud cover: {cloud_cover:.2f}")
    print()

    # Calculate Python solar position
    azimuth, elevation, distance = NOAASolarPosition.calc_solar_position(
        lat=48.45, lon=-122.33, dt=dt, timezone=-8.0, dlstime=0
    )

    print(f"  Python Solar Elevation: {elevation:.2f}°")
    print(f"  Elevation difference: {elevation - vba_elevation:.2f}°")
    print()

    # Calculate Python potential solar radiation
    if elevation > 0:
        potential_solar = SolarRadiationBras.calculate(
            elevation=elevation, earth_sun_distance=distance, turbidity=2.0
        )
        print(f"  Python Potential Solar: {potential_solar:.2f} W/m²")
        print(f"  Potential difference: {potential_solar - vba_potential:.2f} W/m²")
        print()

        # Apply corrections
        from rtemp.solar.corrections import SolarRadiationCorrections

        # Cloud correction
        solar_after_cloud = SolarRadiationCorrections.apply_cloud_correction(
            potential_solar, cloud_cover, kcl1=0.65, kcl2=2.0
        )
        print(f"  After cloud correction: {solar_after_cloud:.2f} W/m²")

        # Shade correction
        solar_after_shade = SolarRadiationCorrections.apply_shade_correction(
            solar_after_cloud, effective_shade=0.15
        )
        print(f"  After shade correction: {solar_after_shade:.2f} W/m²")

        # Albedo correction
        albedo = SolarRadiationCorrections.calculate_anderson_albedo(elevation, cloud_cover)
        solar_final = SolarRadiationCorrections.apply_albedo_correction(solar_after_shade, albedo)
        print(f"  Albedo: {albedo:.4f}")
        print(f"  After albedo correction: {solar_final:.2f} W/m²")
        print()

        print(f"  VBA Final: {vba_solar:.2f} W/m²")
        print(f"  Python Final: {solar_final:.2f} W/m²")
        print(
            f"  Difference: {solar_final - vba_solar:.2f} W/m² ({(solar_final - vba_solar) / vba_solar * 100:.1f}%)"
        )
    else:
        print(f"  Sun below horizon (elevation = {elevation:.2f}°)")

    print()
    print("-" * 80)
    print()

# Summary statistics
print("=" * 80)
print("OVERALL STATISTICS")
print("=" * 80)
print()

# Load Python output
python_output = pd.read_csv(os.path.join(script_dir, "long_term_python_output.csv"))

vba_solar_all = vba_output[
    "solar radiation entering the water after shade and reflection (W/m^2)"
].values
python_solar_all = python_output["solar_radiation"].values

print(f"Total timesteps: {len(vba_solar_all)}")
print(f"VBA solar mean: {np.mean(vba_solar_all):.2f} W/m²")
print(f"Python solar mean: {np.mean(python_solar_all):.2f} W/m²")
print(f"Difference: {np.mean(python_solar_all) - np.mean(vba_solar_all):.2f} W/m²")
print()

# Daytime only (elevation > 0)
daytime_vba = vba_solar_all[vba_solar_all > 0]
daytime_python = python_solar_all[vba_solar_all > 0]

print(f"Daytime timesteps (VBA solar > 0): {len(daytime_vba)}")
print(f"VBA daytime mean: {np.mean(daytime_vba):.2f} W/m²")
print(f"Python daytime mean: {np.mean(daytime_python):.2f} W/m²")
print(f"Difference: {np.mean(daytime_python) - np.mean(daytime_vba):.2f} W/m²")
print(
    f"Percent difference: {(np.mean(daytime_python) - np.mean(daytime_vba)) / np.mean(daytime_vba) * 100:.1f}%"
)
