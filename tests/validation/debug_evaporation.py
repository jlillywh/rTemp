"""
Debug script to investigate evaporation calculation differences between VBA and Python.
"""

from rtemp.utils.atmospheric import AtmosphericHelpers
from rtemp.wind.adjustment import WindAdjustment
from rtemp.wind.functions import WindFunctionBradyGravesGeyer
from rtemp.heat_flux.calculator import HeatFluxCalculator
from rtemp.utils.conversions import UnitConversions

# Timestep 3 data from VBA sample
air_temp = 11.40  # °C
dewpoint = 11.48  # °C
wind_speed_10m = 0.89  # m/s at 10m height
water_temp = 11.92  # °C (from VBA output timestep 3)

# Configuration
wind_height = 10.0  # m (measurement height)
effective_wind_factor = 1.0

print("=" * 80)
print("EVAPORATION CALCULATION DEBUG")
print("=" * 80)
print()
print("Input Data (Timestep 3):")
print(f"  Air temperature: {air_temp}°C")
print(f"  Dewpoint: {dewpoint}°C")
print(f"  Wind speed (10m): {wind_speed_10m} m/s")
print(f"  Water temperature: {water_temp}°C")
print()

# Step 1: Adjust wind speed from 10m to 7m
wind_adjuster = WindAdjustment()
wind_speed_7m = wind_adjuster.adjust_for_height(
    wind_speed=wind_speed_10m, measured_height=wind_height, target_height=7.0
)
print("Step 1: Wind Speed Adjustment")
print(f"  Wind at 10m: {wind_speed_10m} m/s")
print(f"  Wind at 7m: {wind_speed_7m} m/s")
print()

# Step 2: Apply effective wind factor
wind_speed_effective = wind_speed_7m * effective_wind_factor
print("Step 2: Apply Effective Wind Factor")
print(f"  Effective wind factor: {effective_wind_factor}")
print(f"  Effective wind speed: {wind_speed_effective} m/s")
print()

# Step 3: Calculate vapor pressures
vapor_pressure_air = AtmosphericHelpers.saturation_vapor_pressure(dewpoint)
vapor_pressure_water = AtmosphericHelpers.saturation_vapor_pressure(water_temp)

print("Step 3: Vapor Pressures")
print(f"  Vapor pressure (air): {vapor_pressure_air:.4f} mmHg")
print(f"  Vapor pressure (water): {vapor_pressure_water:.4f} mmHg")
print(f"  Difference: {vapor_pressure_water - vapor_pressure_air:.4f} mmHg")
print()

# Step 4: Calculate wind function
wind_func = WindFunctionBradyGravesGeyer()
f_w = wind_func.calculate(
    wind_speed=wind_speed_effective,
    air_temp=air_temp,
    water_temp=water_temp,
    vapor_pressure_air=vapor_pressure_air,
    vapor_pressure_water=vapor_pressure_water,
)

print("Step 4: Wind Function (Brady-Graves-Geyer)")
print(f"  Formula: f(W) = 9.2 + 0.46 * W²")
print(f"  f(W) = 9.2 + 0.46 * {wind_speed_effective}²")
print(f"  f(W) = {f_w:.4f} cal/(cm²·day·mmHg)")
print()

# Step 5: Calculate evaporation
evap_cal = HeatFluxCalculator.calculate_evaporation(
    wind_function=f_w,
    vapor_pressure_water=vapor_pressure_water,
    vapor_pressure_air=vapor_pressure_air,
)

evap_w_m2 = UnitConversions.cal_cm2_day_to_watts_m2(evap_cal)

print("Step 5: Evaporation Calculation")
print(f"  Formula: evap = -f(W) * (e_water - e_air)")
print(f"  evap = -{f_w:.4f} * ({vapor_pressure_water:.4f} - {vapor_pressure_air:.4f})")
print(f"  evap = -{f_w:.4f} * {vapor_pressure_water - vapor_pressure_air:.4f}")
print(f"  evap = {evap_cal:.4f} cal/(cm²·day)")
print(f"  evap = {evap_w_m2:.4f} W/m²")
print()

# VBA comparison
vba_evap = -3.13  # W/m² from VBA output
print("=" * 80)
print("COMPARISON")
print("=" * 80)
print(f"  VBA evaporation: {vba_evap:.4f} W/m²")
print(f"  Python evaporation: {evap_w_m2:.4f} W/m²")
print(f"  Difference: {evap_w_m2 - vba_evap:.4f} W/m²")
print(f"  Percent error: {abs(evap_w_m2 - vba_evap) / abs(vba_evap) * 100:.2f}%")
print()

# Check if VBA might be using different wind function formula
print("=" * 80)
print("INVESTIGATING POSSIBLE CAUSES")
print("=" * 80)
print()

# Hypothesis 1: VBA uses different wind function formula
print("Hypothesis 1: Different wind function formula")
print("  VBA might use: f(W) = 19 + 0.95 * W²")
f_w_alt = 19 + 0.95 * (wind_speed_effective**2)
evap_alt_cal = -f_w_alt * (vapor_pressure_water - vapor_pressure_air)
evap_alt_w_m2 = UnitConversions.cal_cm2_day_to_watts_m2(evap_alt_cal)
print(f"  Alternative f(W) = {f_w_alt:.4f}")
print(f"  Alternative evap = {evap_alt_w_m2:.4f} W/m²")
print(f"  Difference from VBA: {evap_alt_w_m2 - vba_evap:.4f} W/m²")
print()

# Hypothesis 2: VBA doesn't adjust wind from 10m to 7m
print("Hypothesis 2: VBA uses wind at 10m directly")
f_w_10m = 9.2 + 0.46 * (wind_speed_10m**2)
evap_10m_cal = -f_w_10m * (vapor_pressure_water - vapor_pressure_air)
evap_10m_w_m2 = UnitConversions.cal_cm2_day_to_watts_m2(evap_10m_cal)
print(f"  f(W) at 10m = {f_w_10m:.4f}")
print(f"  evap at 10m = {evap_10m_cal:.4f} cal/(cm²·day)")
print(f"  evap at 10m = {evap_10m_w_m2:.4f} W/m²")
print(f"  Difference from VBA: {evap_10m_w_m2 - vba_evap:.4f} W/m²")
print()

# Hypothesis 3: VBA uses different wind adjustment formula
print("Hypothesis 3: Different wind adjustment formula")
# Try different exponent
wind_7m_alt = wind_speed_10m * (7.0 / 10.0) ** 0.2  # Different exponent
f_w_alt2 = 9.2 + 0.46 * (wind_7m_alt**2)
evap_alt2_cal = -f_w_alt2 * (vapor_pressure_water - vapor_pressure_air)
evap_alt2_w_m2 = UnitConversions.cal_cm2_day_to_watts_m2(evap_alt2_cal)
print(f"  Wind at 7m (alt formula) = {wind_7m_alt:.4f} m/s")
print(f"  f(W) = {f_w_alt2:.4f}")
print(f"  evap = {evap_alt2_w_m2:.4f} W/m²")
print(f"  Difference from VBA: {evap_alt2_w_m2 - vba_evap:.4f} W/m²")
print()

# Hypothesis 4: Check what wind function would give VBA result
print("Hypothesis 4: Back-calculate required wind function")
vba_evap_cal = UnitConversions.watts_m2_to_cal_cm2_day(vba_evap)
vapor_diff = vapor_pressure_water - vapor_pressure_air
required_f_w = -vba_evap_cal / vapor_diff
print(f"  VBA evap in cal/(cm²·day): {vba_evap_cal:.4f}")
print(f"  Vapor pressure diff: {vapor_diff:.4f} mmHg")
print(f"  Required f(W) to match VBA: {required_f_w:.4f}")
print(f"  Python f(W): {f_w:.4f}")
print(f"  Ratio: {required_f_w / f_w:.4f}")
print()

# What wind speed would give this f(W)?
# f(W) = 9.2 + 0.46 * W²
# W² = (f(W) - 9.2) / 0.46
# W = sqrt((f(W) - 9.2) / 0.46)
import math

if required_f_w > 9.2:
    required_wind = math.sqrt((required_f_w - 9.2) / 0.46)
    print(f"  Wind speed that would give this f(W): {required_wind:.4f} m/s")
    print(f"  Python uses: {wind_speed_effective:.4f} m/s")
    print(f"  Ratio: {required_wind / wind_speed_effective:.4f}")
else:
    print(f"  Required f(W) is too low for Brady-Graves-Geyer formula")
print()
