"""
Debug sediment conduction calculation differences.
"""

from rtemp.heat_flux.calculator import HeatFluxCalculator
from rtemp.utils.conversions import UnitConversions

print("=" * 80)
print("SEDIMENT CONDUCTION DEBUG")
print("=" * 80)
print()

# VBA sample data configuration
sediment_conductivity = 1.57  # W/(m·°C)
sediment_thickness = 10.0  # cm

# Timestep data from VBA output
timesteps = [
    {"name": "Timestep 1", "water_temp": 12.00, "sediment_temp": 12.00, "vba_flux": 0.00},
    {"name": "Timestep 2", "water_temp": 11.96, "sediment_temp": 12.00, "vba_flux": 0.00},
    {"name": "Timestep 3", "water_temp": 11.92, "sediment_temp": 12.00, "vba_flux": 1.28},
]

print("Configuration:")
print(f"  Sediment thermal conductivity: {sediment_conductivity} W/(m·°C)")
print(f"  Sediment thickness: {sediment_thickness} cm")
print()

for ts in timesteps:
    print(f"{ts['name']}: {ts['name'].split()[1]}")
    print("-" * 80)
    print(f"  Water temperature: {ts['water_temp']}°C")
    print(f"  Sediment temperature: {ts['sediment_temp']}°C")
    print(
        f"  Temperature difference (sediment - water): {ts['sediment_temp'] - ts['water_temp']}°C"
    )
    print()

    # Calculate using Python
    flux_cal = HeatFluxCalculator.calculate_sediment_conduction(
        water_temp=ts["water_temp"],
        sediment_temp=ts["sediment_temp"],
        thermal_conductivity=sediment_conductivity,
        sediment_thickness=sediment_thickness,
    )
    flux_w_m2 = UnitConversions.cal_cm2_day_to_watts_m2(flux_cal)

    print(f"  Python calculation:")
    print(f"    Flux: {flux_cal:.4f} cal/(cm²·day)")
    print(f"    Flux: {flux_w_m2:.4f} W/m²")
    print()

    print(f"  VBA output: {ts['vba_flux']:.4f} W/m²")
    print(f"  Difference: {flux_w_m2 - ts['vba_flux']:.4f} W/m²")
    print()

print("=" * 80)
print("ANALYSIS")
print("=" * 80)
print()

# Check if VBA might be using different sediment temperature
print("Hypothesis: VBA updates sediment temperature during simulation")
print()

# For timestep 3, what sediment temp would give VBA's flux?
water_temp_3 = 11.92
vba_flux_3 = 1.28
vba_flux_3_cal = UnitConversions.watts_m2_to_cal_cm2_day(vba_flux_3)

# Formula: flux = k * (T_sed - T_water) / thickness * seconds_per_day
# Rearrange: T_sed = T_water + (flux * thickness) / (k * seconds_per_day)

from rtemp.constants import W_M_C_TO_CAL_S_CM_C, SECONDS_PER_DAY

k_cal = sediment_conductivity * W_M_C_TO_CAL_S_CM_C
flux_per_second = vba_flux_3_cal / SECONDS_PER_DAY
temp_diff_required = (flux_per_second * sediment_thickness) / k_cal

required_sediment_temp = water_temp_3 + temp_diff_required

print(f"For timestep 3:")
print(f"  Water temp: {water_temp_3}°C")
print(f"  VBA flux: {vba_flux_3} W/m² = {vba_flux_3_cal:.4f} cal/(cm²·day)")
print(f"  Required temp difference: {temp_diff_required:.4f}°C")
print(f"  Required sediment temp: {required_sediment_temp:.4f}°C")
print(f"  VBA shows sediment temp: 12.00°C")
print()

# Check if Python is updating sediment temperature
print("Checking if Python model updates sediment temperature...")
print()

from rtemp import ModelConfiguration, RTempModel
import pandas as pd
from datetime import datetime

config = ModelConfiguration(
    latitude=48.45,
    longitude=-122.33,
    elevation=100.0,
    timezone=-8.0,
    initial_water_temp=12.0,
    initial_sediment_temp=12.0,
    water_depth=0.4,
    sediment_thermal_conductivity=1.57,
    sediment_thermal_diffusivity=0.00645,
    sediment_thickness=10.0,
    enable_diagnostics=True,
)

met_data = pd.DataFrame(
    [
        {
            "datetime": datetime(2003, 10, 1, 0, 0),
            "air_temperature": 11.61,
            "dewpoint_temperature": 11.67,
            "wind_speed": 0.89,
            "cloud_cover": 0.13,
        },
        {
            "datetime": datetime(2003, 10, 1, 0, 15),
            "air_temperature": 11.50,
            "dewpoint_temperature": 11.57,
            "wind_speed": 0.89,
            "cloud_cover": 0.10,
        },
        {
            "datetime": datetime(2003, 10, 1, 0, 30),
            "air_temperature": 11.40,
            "dewpoint_temperature": 11.48,
            "wind_speed": 0.89,
            "cloud_cover": 0.07,
        },
    ]
)

model = RTempModel(config)
results = model.run(met_data)

print("Python model results:")
for i in range(len(results)):
    print(f"  Timestep {i+1}:")
    print(f"    Water temp: {results['water_temperature'].iloc[i]:.2f}°C")
    print(f"    Sediment temp: {results['sediment_temperature'].iloc[i]:.2f}°C")
    print(f"    Sediment conduction: {results['sediment_conduction'].iloc[i]:.4f} W/m²")
print()

print("=" * 80)
print("CONCLUSION")
print("=" * 80)
print()
print("The issue is that Python is not updating sediment temperature between timesteps.")
print("VBA appears to update sediment temperature, which creates a temperature gradient")
print("and thus a non-zero sediment conduction flux by timestep 3.")
