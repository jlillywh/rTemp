"""Debug script to trace longwave radiation calculations."""

from rtemp.atmospheric.emissivity import EmissivityBrutsaert
from rtemp.atmospheric.longwave import LongwaveRadiation
from rtemp.utils.atmospheric import AtmosphericHelpers

# VBA input values from first timestep
air_temp = 11.61  # °C
dewpoint = 11.67  # °C
cloud_cover = 0.13
brutsaert_coeff = 1.24
kcl3 = 0.17
kcl4 = 2.0

print("=" * 80)
print("Longwave Radiation Debug - Timestep 1")
print("=" * 80)
print()
print("Input Values:")
print(f"  Air Temperature: {air_temp}°C")
print(f"  Dewpoint: {dewpoint}°C")
print(f"  Cloud Cover: {cloud_cover}")
print(f"  Brutsaert Coefficient: {brutsaert_coeff}")
print(f"  KCL3: {kcl3}")
print(f"  KCL4: {kcl4}")
print()

# Calculate vapor pressure
vapor_pressure_water = AtmosphericHelpers.saturation_vapor_pressure(dewpoint)
vapor_pressure_air = AtmosphericHelpers.saturation_vapor_pressure(dewpoint)

print("Vapor Pressure Calculations:")
print(f"  Saturation VP at dewpoint: {vapor_pressure_water:.4f} mmHg")
print(f"  Air VP: {vapor_pressure_air:.4f} mmHg")
print()

# Calculate emissivity
emissivity_model = EmissivityBrutsaert(coefficient=brutsaert_coeff)
emissivity = emissivity_model.calculate(air_temp, vapor_pressure_air)

print("Emissivity Calculation:")
print(f"  Clear-sky emissivity: {emissivity:.6f}")
print()

# Calculate longwave atmospheric radiation
longwave_atm = LongwaveRadiation.calculate_atmospheric(
    emissivity=emissivity,
    air_temp_c=air_temp,
    cloud_cover=cloud_cover,
    cloud_method="Eqn 1",
    kcl3=kcl3,
    kcl4=kcl4,
)

print("Longwave Atmospheric Radiation:")
print(f"  Python calculated: {longwave_atm:.4f} W/m²")
print(f"  VBA value: 291.46 W/m²")
print(f"  Difference: {longwave_atm - 291.46:.4f} W/m²")
print(f"  Ratio (Python/VBA): {longwave_atm / 291.46:.4f}")
print()

# Calculate longwave back radiation
water_temp = 12.0  # °C
longwave_back = LongwaveRadiation.calculate_back_radiation(water_temp)

print("Longwave Back Radiation:")
print(f"  Python calculated: {longwave_back:.4f} W/m² (positive)")
print(f"  Python (VBA sign): {-longwave_back:.4f} W/m² (negative)")
print(f"  VBA value: -363.27 W/m²")
print(f"  Difference: {-longwave_back - (-363.27):.4f} W/m²")
print(f"  Ratio (Python/VBA): {longwave_back / 363.27:.4f}")
print()

# Let's also manually calculate using Stefan-Boltzmann
from rtemp.constants import STEFAN_BOLTZMANN, CELSIUS_TO_KELVIN, ATMOSPHERIC_REFLECTION

air_temp_k = air_temp + CELSIUS_TO_KELVIN
water_temp_k = water_temp + CELSIUS_TO_KELVIN

print("Manual Stefan-Boltzmann Calculations:")
print(f"  Air temp: {air_temp_k:.2f} K")
print(f"  Water temp: {water_temp_k:.2f} K")
print(f"  Stefan-Boltzmann constant: {STEFAN_BOLTZMANN} W/(m²·K⁴)")
print()

# Cloud correction
cloud_factor = 1.0 + kcl3 * (cloud_cover**kcl4)
emissivity_cloudy = emissivity * cloud_factor
emissivity_cloudy = max(0.0, min(1.0, emissivity_cloudy))

print(f"  Cloud factor: {cloud_factor:.6f}")
print(f"  Cloudy emissivity: {emissivity_cloudy:.6f}")
print()

# Atmospheric radiation
longwave_raw = emissivity_cloudy * STEFAN_BOLTZMANN * (air_temp_k**4)
longwave_with_reflection = longwave_raw * (1.0 - ATMOSPHERIC_REFLECTION)

print(f"  Longwave (before reflection): {longwave_raw:.4f} W/m²")
print(f"  Atmospheric reflection factor: {1.0 - ATMOSPHERIC_REFLECTION}")
print(f"  Longwave (after reflection): {longwave_with_reflection:.4f} W/m²")
print()

# Back radiation
back_raw = 0.97 * STEFAN_BOLTZMANN * (water_temp_k**4)
print(f"  Back radiation (water emissivity=0.97): {back_raw:.4f} W/m²")
print()

print("=" * 80)
print("Analysis:")
print("=" * 80)
print()
print("The Python implementation calculates significantly lower longwave radiation.")
print("This suggests either:")
print("  1. Different emissivity calculation")
print("  2. Different Stefan-Boltzmann constant or units")
print("  3. Different cloud correction method")
print("  4. VBA may be using different input values or intermediate calculations")
