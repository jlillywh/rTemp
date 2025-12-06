"""Debug solar position calculation to find remaining azimuth difference."""

from datetime import datetime
from rtemp.solar.position import NOAASolarPosition
import math

# Test case from VBA sample - Timestep 1
lat = 48.45
lon = -122.33
timezone = -8
dt = datetime(2003, 10, 1, 0, 0)

print("=" * 80)
print("Solar Position Debug - Timestep 1")
print("=" * 80)
print()
print(f"Location: {lat}°N, {lon}°W")
print(f"Date/Time: {dt} (local time, timezone UTC{timezone})")
print()

# Calculate using Python
azimuth, elevation, distance = NOAASolarPosition.calc_solar_position(
    lat, lon, dt, timezone, 0
)

print("Python Results:")
print(f"  Azimuth: {azimuth:.4f}°")
print(f"  Elevation: {elevation:.4f}°")
print()

print("VBA Results:")
print(f"  Azimuth: 0.29°")
print(f"  Elevation: -44.61°")
print()

print("Differences:")
print(f"  Azimuth: {azimuth - 0.29:.4f}°")
print(f"  Elevation: {elevation - (-44.61):.4f}°")
print()

# Let's trace through the calculation step by step
print("=" * 80)
print("Step-by-Step Calculation")
print("=" * 80)
print()

# Julian day
jd = NOAASolarPosition.calc_julian_day(dt.year, dt.month, dt.day)
print(f"Julian Day: {jd:.6f}")

# Time fraction
time_frac = (dt.hour + dt.minute / 60.0 + dt.second / 3600.0) / 24.0
jd_time = jd + time_frac
print(f"Time fraction: {time_frac:.6f}")
print(f"JD with time: {jd_time:.6f}")

# Julian century
t = NOAASolarPosition.calc_time_julian_cent(jd_time)
print(f"Julian century: {t:.10f}")

# Solar declination
decl = NOAASolarPosition.calc_sun_declination(t)
print(f"Solar declination: {decl:.6f}°")

# Equation of time
eq_time = NOAASolarPosition.calc_equation_of_time(t)
print(f"Equation of time: {eq_time:.6f} minutes")

# Hour angle
time_offset = eq_time + 4.0 * lon - 60.0 * timezone
true_solar_time = (dt.hour * 60.0 + dt.minute + dt.second / 60.0 + time_offset) % 1440.0
hour_angle = true_solar_time / 4.0 - 180.0
print(f"Time offset: {time_offset:.6f} minutes")
print(f"True solar time: {true_solar_time:.6f} minutes")
print(f"Hour angle: {hour_angle:.6f}°")

# Zenith angle
lat_rad = lat * math.pi / 180.0
decl_rad = decl * math.pi / 180.0
ha_rad = hour_angle * math.pi / 180.0

cos_zenith = (math.sin(lat_rad) * math.sin(decl_rad) + 
              math.cos(lat_rad) * math.cos(decl_rad) * math.cos(ha_rad))
cos_zenith = max(-1.0, min(1.0, cos_zenith))
zenith = math.acos(cos_zenith) * 180.0 / math.pi

print(f"Zenith angle: {zenith:.6f}°")
print(f"Elevation (90-zenith): {90.0 - zenith:.6f}°")

# Azimuth calculation
cos_azimuth = ((math.sin(lat_rad) * math.cos(zenith * math.pi / 180.0)) - math.sin(decl_rad)) / \
              (math.cos(lat_rad) * math.sin(zenith * math.pi / 180.0))
cos_azimuth = max(-1.0, min(1.0, cos_azimuth))

print(f"cos(azimuth): {cos_azimuth:.10f}")

azimuth_calc = 180.0 - (math.acos(cos_azimuth) * 180.0 / math.pi)
print(f"Azimuth (180 - acos): {azimuth_calc:.6f}°")

if hour_angle > 0:
    azimuth_calc = -azimuth_calc
    print(f"Hour angle > 0, negate: {azimuth_calc:.6f}°")

if azimuth_calc < 0:
    azimuth_calc = azimuth_calc + 360.0
    print(f"Normalize to 0-360: {azimuth_calc:.6f}°")

print()
print(f"Final calculated azimuth: {azimuth_calc:.6f}°")
print(f"VBA azimuth: 0.29°")
print(f"Difference: {azimuth_calc - 0.29:.6f}°")
