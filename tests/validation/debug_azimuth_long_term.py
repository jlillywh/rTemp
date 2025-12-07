"""Debug azimuth values in long-term validation."""

import pandas as pd
import os

# Load the VBA output
script_dir = os.path.dirname(os.path.abspath(__file__))
fixtures_dir = os.path.join(script_dir, "..", "fixtures")
vba_output_file = os.path.join(fixtures_dir, "vba_ts_output.csv")

# Read VBA output
vba_df = pd.read_csv(vba_output_file, skiprows=1)
vba_df["datetime"] = pd.to_datetime(vba_df["date-time"])

# Load Python output
python_output_file = os.path.join(script_dir, "long_term_python_output.csv")
python_df = pd.read_csv(python_output_file)
python_df["datetime"] = pd.to_datetime(python_df["datetime"])

print("First 10 timesteps comparison:")
print()
print("VBA Solar Azimuth:")
print(vba_df["solar azimuth (deg)"].head(10).values)
print()
print("Python Solar Azimuth:")
print(python_df["solar_azimuth"].head(10).values)
print()
print("Differences:")
diffs = python_df["solar_azimuth"].head(10).values - vba_df["solar azimuth (deg)"].head(10).values
print(diffs)
print()

# Check if there's a radians/degrees issue
print("Checking for radians/degrees conversion:")
import numpy as np

python_rad = python_df["solar_azimuth"].head(10).values
python_as_deg = np.degrees(python_rad)
print(f"Python values as-is: {python_rad}")
print(f"Python converted to degrees: {python_as_deg}")
print()

# Check if Python values are in radians
print("If Python is in radians, converting to degrees:")
for i in range(10):
    vba_val = vba_df["solar azimuth (deg)"].iloc[i]
    python_val = python_df["solar_azimuth"].iloc[i]
    python_as_deg = np.degrees(python_val)
    print(
        f"  Timestep {i+1}: VBA={vba_val:.4f}°, Python={python_val:.4f}, Python as deg={python_as_deg:.4f}°"
    )
