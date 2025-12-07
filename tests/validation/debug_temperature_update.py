"""
Debug why water temperature is not updating.
"""

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

print("=" * 80)
print("TEMPERATURE UPDATE DEBUG")
print("=" * 80)
print()

# Show all heat flux components
flux_columns = [
    "solar_radiation",
    "longwave_atmospheric",
    "longwave_back",
    "evaporation",
    "convection",
    "sediment_conduction",
    "hyporheic_exchange",
    "groundwater",
    "net_flux",
]

print("Heat Fluxes (W/m²):")
print(results[flux_columns].to_string(index=False))
print()

print("Temperatures:")
print(results[["datetime", "water_temperature", "sediment_temperature"]].to_string(index=False))
print()

# Calculate expected temperature change
print("=" * 80)
print("EXPECTED TEMPERATURE CHANGE CALCULATION")
print("=" * 80)
print()

from rtemp.constants import WATER_DENSITY, WATER_SPECIFIC_HEAT
from rtemp.utils.conversions import UnitConversions

water_depth_cm = 0.4 * 100  # 40 cm
timestep_hours = 0.25  # 15 minutes
timestep_days = timestep_hours / 24.0

for i in range(len(results)):
    net_flux_w_m2 = results["net_flux"].iloc[i]
    net_flux_cal = UnitConversions.watts_m2_to_cal_cm2_day(net_flux_w_m2)

    # Temperature change rate in °C/day
    # dT/dt = Q / (ρ * Cp * depth)
    # where Q is in cal/(cm²·day), ρ in g/cm³, Cp in cal/(g·°C), depth in cm

    rho_g_cm3 = WATER_DENSITY / 1000.0  # kg/m³ to g/cm³
    cp_cal = WATER_SPECIFIC_HEAT / 4.184  # J/(kg·°C) to cal/(g·°C)

    temp_change_rate = net_flux_cal / (rho_g_cm3 * cp_cal * water_depth_cm)
    temp_change = temp_change_rate * timestep_days

    print(f"Timestep {i+1}:")
    print(f"  Net flux: {net_flux_w_m2:.4f} W/m² = {net_flux_cal:.4f} cal/(cm²·day)")
    print(f"  Water depth: {water_depth_cm} cm")
    print(f"  Density: {rho_g_cm3} g/cm³")
    print(f"  Specific heat: {cp_cal:.4f} cal/(g·°C)")
    print(f"  Temp change rate: {temp_change_rate:.6f} °C/day")
    print(f"  Timestep: {timestep_days} days ({timestep_hours} hours)")
    print(f"  Expected temp change: {temp_change:.6f} °C")
    print(f"  Current water temp: {results['water_temperature'].iloc[i]:.6f} °C")
    if i > 0:
        actual_change = (
            results["water_temperature"].iloc[i] - results["water_temperature"].iloc[i - 1]
        )
        print(f"  Actual temp change: {actual_change:.6f} °C")
    print()

# Compare with VBA
print("=" * 80)
print("COMPARISON WITH VBA")
print("=" * 80)
print()

vba_temps = [12.00, 11.96, 11.92]
for i in range(len(results)):
    python_temp = results["water_temperature"].iloc[i]
    vba_temp = vba_temps[i]
    print(f"Timestep {i+1}:")
    print(f"  Python: {python_temp:.4f}°C")
    print(f"  VBA: {vba_temp:.4f}°C")
    print(f"  Difference: {python_temp - vba_temp:.4f}°C")
    print()
