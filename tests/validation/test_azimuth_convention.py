"""Test to understand azimuth convention differences."""

from datetime import datetime
from rtemp.solar.position import NOAASolarPosition

# Test case from VBA sample
lat = 48.45
lon = -122.33
timezone = -8
dt = datetime(2003, 10, 1, 0, 0)  # Midnight

print("=" * 80)
print("Solar Azimuth Convention Test")
print("=" * 80)
print()
print(f"Location: {lat}°N, {lon}°W")
print(f"Date/Time: {dt} (local time, timezone UTC{timezone})")
print()

# Calculate solar position
azimuth, elevation, distance = NOAASolarPosition.calc_solar_position(
    lat, lon, dt, timezone, 0
)

print("Python (NOAA) Results:")
print(f"  Azimuth: {azimuth:.2f}°")
print(f"  Elevation: {elevation:.2f}°")
print()

print("VBA Results:")
print(f"  Azimuth: 0.29°")
print(f"  Elevation: -44.61°")
print()

print("Analysis:")
print(f"  Azimuth difference: {azimuth - 0.29:.2f}°")
print()

# At midnight, the sun should be roughly opposite (south for northern hemisphere)
# If VBA shows 0.29° (nearly north), Python shows 173.24° (nearly south)
# This suggests:
#   - VBA: 0° = North, but measuring where sun is below horizon
#   - Python: 0° = North, measuring actual position

print("Interpretation:")
print("  At midnight in October at 48°N:")
print("  - Sun is below horizon (elevation = -44°)")
print("  - Sun's position (if visible through Earth) is roughly south")
print()
print("  VBA azimuth 0.29° suggests: Nearly due North")
print("  Python azimuth 173.24° suggests: Nearly due South (180° = South)")
print()
print("  The ~173° difference suggests VBA may be using a different")
print("  reference or measuring the antisolar point (opposite direction).")
print()

# Test with a daytime position to see if pattern holds
print("=" * 80)
print("Daytime Test (noon)")
print("=" * 80)
print()

dt_noon = datetime(2003, 10, 1, 12, 0)
azimuth_noon, elevation_noon, _ = NOAASolarPosition.calc_solar_position(
    lat, lon, dt_noon, timezone, 0
)

print(f"Date/Time: {dt_noon} (local time)")
print(f"Python Azimuth: {azimuth_noon:.2f}°")
print(f"Python Elevation: {elevation_noon:.2f}°")
print()
print("At solar noon, azimuth should be close to 180° (due south)")
print(f"Result: {azimuth_noon:.2f}° - {'✓ Correct' if 170 < azimuth_noon < 190 else '✗ Unexpected'}")
