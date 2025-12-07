"""
Detailed debug of sediment temperature updating in Python model.
"""

from rtemp import ModelConfiguration, RTempModel
import pandas as pd
from datetime import datetime

print("=" * 80)
print("DETAILED SEDIMENT TEMPERATURE DEBUG")
print("=" * 80)
print()

# Configuration matching VBA
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
    enable_diagnostics=True,
)

print("Configuration:")
print(f"  Initial water temp: {config.initial_water_temp}°C")
print(f"  Initial sediment temp: {config.initial_sediment_temp}°C")
print(f"  Sediment conductivity: {config.sediment_thermal_conductivity} W/(m·°C)")
print(f"  Sediment thickness: {config.sediment_thickness} cm")
print()

# Meteorological data
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

print("Meteorological data:")
print(met_data)
print()

# Run model
model = RTempModel(config)
results = model.run(met_data)

print("=" * 80)
print("RESULTS")
print("=" * 80)
print()

# Display key columns
columns_to_show = [
    "datetime",
    "water_temperature",
    "sediment_temperature",
    "sediment_conduction",
    "evaporation",
    "convection",
]

print(results[columns_to_show].to_string(index=False))
print()

# Check if sediment conduction is zero
print("=" * 80)
print("ANALYSIS")
print("=" * 80)
print()

for i in range(len(results)):
    water_temp = results["water_temperature"].iloc[i]
    sed_temp = results["sediment_temperature"].iloc[i]
    sed_cond = results["sediment_conduction"].iloc[i]

    print(f"Timestep {i+1}:")
    print(f"  Water temp: {water_temp:.4f}°C")
    print(f"  Sediment temp: {sed_temp:.4f}°C")
    print(f"  Temp difference: {sed_temp - water_temp:.4f}°C")
    print(f"  Sediment conduction: {sed_cond:.4f} W/m²")

    # Manual calculation
    from rtemp.heat_flux.calculator import HeatFluxCalculator
    from rtemp.utils.conversions import UnitConversions

    manual_flux_cal = HeatFluxCalculator.calculate_sediment_conduction(
        water_temp=water_temp,
        sediment_temp=sed_temp,
        thermal_conductivity=1.57,
        sediment_thickness=10.0,
    )
    manual_flux_w_m2 = UnitConversions.cal_cm2_day_to_watts_m2(manual_flux_cal)

    print(f"  Manual calculation: {manual_flux_w_m2:.4f} W/m²")
    print(f"  Match: {'YES' if abs(sed_cond - manual_flux_w_m2) < 0.01 else 'NO'}")
    print()

# Check if the issue is that sediment conductivity is being set to zero
print("=" * 80)
print("CHECKING MODEL CONFIGURATION")
print("=" * 80)
print()
print(f"Model config sediment_thermal_conductivity: {model.config.sediment_thermal_conductivity}")
print(f"Model config sediment_thickness: {model.config.sediment_thickness}")
print(f"Model config sediment_thermal_diffusivity: {model.config.sediment_thermal_diffusivity}")
