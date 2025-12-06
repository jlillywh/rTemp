"""
Debug convection calculation differences.
"""

from rtemp.utils.atmospheric import AtmosphericHelpers
from rtemp.wind.adjustment import WindAdjustment
from rtemp.wind.functions import WindFunctionBradyGravesGeyer
from rtemp.heat_flux.calculator import HeatFluxCalculator
from rtemp.utils.conversions import UnitConversions
from rtemp.constants import BOWEN_RATIO

# Timestep 1 data
air_temp = 11.61  # °C
water_temp = 12.00  # °C
wind_speed_10m = 0.89  # m/s
vba_convection = -1.75  # W/m²

print("=" * 80)
print("CONVECTION CALCULATION DEBUG")
print("=" * 80)
print()
print("Input Data (Timestep 1):")
print(f"  Air temperature: {air_temp}°C")
print(f"  Water temperature: {water_temp}°C")
print(f"  Wind speed (10m): {wind_speed_10m} m/s")
print(f"  VBA convection: {vba_convection} W/m²")
print()

# Adjust wind
wind_adjuster = WindAdjustment()
wind_7m = wind_adjuster.adjust_for_height(wind_speed_10m, 10.0, 7.0)
print(f"Wind at 7m: {wind_7m:.4f} m/s")
print()

# Calculate wind function
wind_func = WindFunctionBradyGravesGeyer()
f_w = wind_func.calculate(wind_7m, air_temp, water_temp, 0, 0)
print(f"Wind function f(W): {f_w:.4f} cal/(cm²·day·mmHg)")
print()

# Calculate convection
temp_diff = water_temp - air_temp
print(f"Temperature difference (water - air): {temp_diff}°C")
print(f"Bowen ratio: {BOWEN_RATIO} mmHg/°C")
print()

conv_cal = HeatFluxCalculator.calculate_convection(f_w, water_temp, air_temp, BOWEN_RATIO)
conv_w_m2 = UnitConversions.cal_cm2_day_to_watts_m2(conv_cal)

print("Convection calculation:")
print(f"  Formula: conv = -Bowen * f(W) * (T_water - T_air)")
print(f"  conv = -{BOWEN_RATIO} * {f_w:.4f} * {temp_diff}")
print(f"  conv = {conv_cal:.4f} cal/(cm²·day)")
print(f"  conv = {conv_w_m2:.4f} W/m²")
print()

print("Comparison:")
print(f"  VBA: {vba_convection:.4f} W/m²")
print(f"  Python: {conv_w_m2:.4f} W/m²")
print(f"  Difference: {conv_w_m2 - vba_convection:.4f} W/m²")
print(f"  Error: {abs(conv_w_m2 - vba_convection) / abs(vba_convection) * 100:.1f}%")
print()

# Back-calculate what Bowen ratio would match VBA
vba_conv_cal = UnitConversions.watts_m2_to_cal_cm2_day(vba_convection)
required_bowen = -vba_conv_cal / (f_w * temp_diff)
print(f"Required Bowen ratio to match VBA: {required_bowen:.4f} mmHg/°C")
print(f"Python uses: {BOWEN_RATIO} mmHg/°C")
print(f"Ratio: {required_bowen / BOWEN_RATIO:.4f}")
