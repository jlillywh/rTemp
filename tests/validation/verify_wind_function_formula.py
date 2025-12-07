"""
Verify which Brady-Graves-Geyer formula matches VBA output.
"""

from rtemp.utils.conversions import UnitConversions

# Timestep 3 data
wind_speed_7m = 0.8436  # m/s (adjusted from 10m to 7m)
vapor_pressure_water = 10.4533  # mmHg
vapor_pressure_air = 10.1541  # mmHg
vba_evap = -3.13  # W/m²

vapor_diff = vapor_pressure_water - vapor_pressure_air

print("=" * 80)
print("BRADY-GRAVES-GEYER FORMULA VERIFICATION")
print("=" * 80)
print()
print(f"Wind speed at 7m: {wind_speed_7m} m/s")
print(f"Vapor pressure difference: {vapor_diff:.4f} mmHg")
print(f"VBA evaporation: {vba_evap} W/m²")
print()

# Formula 1: Python current implementation
print("Formula 1: f(W) = 9.2 + 0.46 * W²")
f_w_1 = 9.2 + 0.46 * (wind_speed_7m**2)
evap_1_cal = -f_w_1 * vapor_diff
evap_1_w_m2 = UnitConversions.cal_cm2_day_to_watts_m2(evap_1_cal)
print(f"  f(W) = {f_w_1:.4f}")
print(f"  Evaporation = {evap_1_w_m2:.4f} W/m²")
print(
    f"  Error vs VBA: {abs(evap_1_w_m2 - vba_evap):.4f} W/m² ({abs(evap_1_w_m2 - vba_evap) / abs(vba_evap) * 100:.1f}%)"
)
print()

# Formula 2: VBA implementation
print("Formula 2: f(W) = 19 + 0.95 * W² (from VBA code)")
f_w_2 = 19 + 0.95 * (wind_speed_7m**2)
evap_2_cal = -f_w_2 * vapor_diff
evap_2_w_m2 = UnitConversions.cal_cm2_day_to_watts_m2(evap_2_cal)
print(f"  f(W) = {f_w_2:.4f}")
print(f"  Evaporation = {evap_2_w_m2:.4f} W/m²")
print(
    f"  Error vs VBA: {abs(evap_2_w_m2 - vba_evap):.4f} W/m² ({abs(evap_2_w_m2 - vba_evap) / abs(vba_evap) * 100:.1f}%)"
)
print()

print("=" * 80)
print("CONCLUSION")
print("=" * 80)
if abs(evap_2_w_m2 - vba_evap) < abs(evap_1_w_m2 - vba_evap):
    print("✓ Formula 2 (VBA: 19 + 0.95 * W²) matches VBA output much better!")
    print(
        f"  Error reduced from {abs(evap_1_w_m2 - vba_evap):.2f} to {abs(evap_2_w_m2 - vba_evap):.2f} W/m²"
    )
else:
    print("✗ Formula 1 (Python: 9.2 + 0.46 * W²) is closer")
print()

# Check all three timesteps
print("=" * 80)
print("VERIFICATION ACROSS ALL TIMESTEPS")
print("=" * 80)
print()

timesteps = [
    {"wind_10m": 0.89, "vp_water": 10.4533, "vp_air": 10.4533, "vba_evap": -2.17},  # Timestep 1
    {"wind_10m": 0.89, "vp_water": 10.4533, "vp_air": 10.3541, "vba_evap": -2.82},  # Timestep 2
    {"wind_10m": 0.89, "vp_water": 10.4533, "vp_air": 10.1541, "vba_evap": -3.13},  # Timestep 3
]

for i, ts in enumerate(timesteps, 1):
    # Adjust wind from 10m to 7m
    wind_7m = ts["wind_10m"] * (7.0 / 10.0) ** 0.143
    vapor_diff = ts["vp_water"] - ts["vp_air"]

    # VBA formula
    f_w_vba = 19 + 0.95 * (wind_7m**2)
    evap_vba_formula = -f_w_vba * vapor_diff
    evap_vba_formula_w_m2 = UnitConversions.cal_cm2_day_to_watts_m2(evap_vba_formula)

    error = abs(evap_vba_formula_w_m2 - ts["vba_evap"])
    pct_error = error / abs(ts["vba_evap"]) * 100

    print(f"Timestep {i}:")
    print(f"  VBA output: {ts['vba_evap']:.2f} W/m²")
    print(f"  Python with VBA formula: {evap_vba_formula_w_m2:.2f} W/m²")
    print(f"  Error: {error:.2f} W/m² ({pct_error:.1f}%)")
    print()
