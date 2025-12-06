"""
Detailed diagnostic comparison of solar position calculations for December 3, 2003.
Compares Python NOAA implementation with VBA output step-by-step.
"""

import pandas as pd
from datetime import datetime
from rtemp.solar.position import NOAASolarPosition

# Load VBA output for December 3, 2003
vba_output = pd.read_csv('tests/fixtures/vba_ts_output.csv', skiprows=1)
vba_output['datetime'] = pd.to_datetime(vba_output['date-time'])
dec3_vba = vba_output[vba_output['datetime'].dt.date == pd.Timestamp('2003-12-03').date()].copy()

# Configuration from VBA params
config = {
    'latitude': 48.45,
    'longitude': -122.33,
    'timezone': -8.0,
    'daylight_savings': 0  # Standard time (no DST in December)
}

print("=" * 100)
print("SOLAR POSITION DIAGNOSTIC - December 3, 2003")
print("=" * 100)
print()
print(f"Location: {config['latitude']}°N, {config['longitude']}°W")
print(f"Timezone: UTC{config['timezone']}")
print(f"Daylight Savings: {config['daylight_savings']}")
print()

# Key times to check
times = [
    ('06:00', 'Early morning'),
    ('09:00', 'Morning'),
    ('12:00', 'Solar noon'),
    ('15:00', 'Afternoon'),
    ('16:00', 'Late afternoon'),
    ('17:00', 'Sunset'),
]

print("=" * 100)
print("ELEVATION COMPARISON")
print("=" * 100)
print()
print(f"{'Time':<10} {'Description':<20} {'VBA Elev':>10} {'Python Elev':>12} {'Difference':>12}")
print("-" * 100)

for time_str, desc in times:
    dt = datetime(2003, 12, 3, int(time_str.split(':')[0]), int(time_str.split(':')[1]))
    
    # Get VBA value
    vba_row = dec3_vba[dec3_vba['datetime'] == dt].iloc[0]
    vba_elevation = vba_row['solar elevation (deg)']
    
    # Calculate Python value
    azimuth, elevation, distance = NOAASolarPosition.calc_solar_position(
        lat=config['latitude'],
        lon=config['longitude'],
        dt=dt,
        timezone=config['timezone'],
        dlstime=config['daylight_savings']
    )
    
    diff = elevation - vba_elevation
    
    print(f"{time_str:<10} {desc:<20} {vba_elevation:10.2f}° {elevation:12.2f}° {diff:12.2f}°")

print()
print("=" * 100)
print("DETAILED CALCULATION BREAKDOWN FOR 12:00 (Solar Noon)")
print("=" * 100)
print()

dt_noon = datetime(2003, 12, 3, 12, 0)
vba_noon = dec3_vba[dec3_vba['datetime'] == dt_noon].iloc[0]

# Calculate step-by-step
year, month, day = dt_noon.year, dt_noon.month, dt_noon.day
hour = dt_noon.hour + dt_noon.minute/60.0

print(f"Date/Time: {dt_noon}")
print(f"Year: {year}, Month: {month}, Day: {day}, Hour: {hour}")
print()

# Julian Day
jd = NOAASolarPosition.calc_julian_day(year, month, day)
print(f"Julian Day: {jd:.6f}")

# Add time of day
time_fraction = (hour + config['timezone']) / 24.0
jd_with_time = jd + time_fraction
print(f"Time fraction: {time_fraction:.6f}")
print(f"JD with time: {jd_with_time:.6f}")

# Julian Century
t = NOAASolarPosition.calc_time_julian_cent(jd_with_time)
print(f"Julian Century (T): {t:.10f}")
print()

# Geometric mean longitude
l0 = NOAASolarPosition.calc_geom_mean_long_sun(t)
print(f"Geometric Mean Longitude: {l0:.6f}°")

# Geometric mean anomaly
m = NOAASolarPosition.calc_geom_mean_anomaly_sun(t)
print(f"Geometric Mean Anomaly: {m:.6f}°")

# Equation of center
c = NOAASolarPosition.calc_sun_eq_of_center(t)
print(f"Equation of Center: {c:.6f}°")

# True longitude
true_long = NOAASolarPosition.calc_sun_true_long(t)
print(f"True Longitude: {true_long:.6f}°")

# Apparent longitude
app_long = NOAASolarPosition.calc_sun_app_long(t)
print(f"Apparent Longitude: {app_long:.6f}°")

# Mean obliquity
mean_obliq = NOAASolarPosition.calc_mean_obliquity_of_ecliptic(t)
print(f"Mean Obliquity: {mean_obliq:.6f}°")

# Corrected obliquity
obliq_corr = NOAASolarPosition.calc_obliquity_correction(t)
print(f"Corrected Obliquity: {obliq_corr:.6f}°")

# Declination
decl = NOAASolarPosition.calc_sun_declination(t)
print(f"Solar Declination: {decl:.6f}°")
print()

# Equation of time
eq_time = NOAASolarPosition.calc_equation_of_time(t)
print(f"Equation of Time: {eq_time:.6f} minutes")

# Hour angle
ha = NOAASolarPosition.calc_hour_angle(hour, config['longitude'], eq_time, config['timezone'], config['daylight_savings'])
print(f"Hour Angle: {ha:.6f}°")
print()

# Solar zenith
zenith = NOAASolarPosition.calc_solar_zenith_angle(config['latitude'], decl, ha)
print(f"Solar Zenith Angle: {zenith:.6f}°")

# Solar elevation
elevation = 90.0 - zenith
print(f"Solar Elevation: {elevation:.6f}°")
print()

print(f"VBA Solar Elevation: {vba_noon['solar elevation (deg)']:.6f}°")
print(f"Difference: {elevation - vba_noon['solar elevation (deg)']:.6f}°")
print()

# Check if the issue is in timezone/DST handling
print("=" * 100)
print("TIMEZONE/DST ANALYSIS")
print("=" * 100)
print()

print("Testing different timezone interpretations:")
for tz_offset in [-8.0, -7.0]:
    for dst in [0, 1]:
        azimuth, elev, dist = NOAASolarPosition.calc_solar_position(
            lat=config['latitude'],
            lon=config['longitude'],
            dt=dt_noon,
            timezone=tz_offset,
            dlstime=dst
        )
        print(f"  TZ={tz_offset:+.1f}, DST={dst}: Elevation={elev:.2f}° (diff from VBA: {elev - vba_noon['solar elevation (deg)']:+.2f}°)")
