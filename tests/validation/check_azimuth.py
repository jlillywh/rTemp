"""Quick check of solar azimuth calculation."""

from rtemp import ModelConfiguration, RTempModel
import pandas as pd
from datetime import datetime

config = ModelConfiguration(
    latitude=48.45,
    longitude=-122.33,
    elevation=100,
    timezone=-8,
    initial_water_temp=12.0,
    water_depth=0.4
)

met = pd.DataFrame([{
    'datetime': datetime(2003, 10, 1, 0, 0),
    'air_temperature': 11.61,
    'dewpoint_temperature': 11.67,
    'wind_speed': 0.89,
    'cloud_cover': 0.13
}])

model = RTempModel(config)
results = model.run(met)

print(f"Solar azimuth: {results['solar_azimuth'].iloc[0]:.4f}°")
print(f"Solar elevation: {results['solar_elevation'].iloc[0]:.4f}°")
print()
print("VBA expected:")
print("  Solar azimuth: 0.29°")
print("  Solar elevation: -44.61°")
print()
print("Difference:")
print(f"  Azimuth: {results['solar_azimuth'].iloc[0] - 0.29:.4f}°")
print(f"  Elevation: {results['solar_elevation'].iloc[0] - (-44.61):.4f}°")
