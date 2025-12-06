"""Check solar elevation at times that showed large differences."""

from datetime import datetime
from rtemp.solar.position import NOAASolarPosition
import pandas as pd

vba = pd.read_csv('tests/fixtures/vba_ts_output.csv', skiprows=1)
vba['datetime'] = pd.to_datetime(vba['date-time'])

# Times that showed large solar radiation differences
times = [
    datetime(2003, 10, 25, 16, 45),
    datetime(2003, 10, 31, 16, 45),
    datetime(2003, 10, 29, 16, 45),
    datetime(2003, 12, 3, 16, 0),
    datetime(2003, 12, 3, 9, 0),
]

print("Checking solar elevation at times with large solar radiation differences:")
print()
print(f"{'DateTime':<20} {'VBA Elev':>10} {'Python Elev':>12} {'Difference':>12}")
print("-" * 60)

for dt in times:
    vba_row = vba[vba['datetime'] == dt].iloc[0]
    vba_elev = vba_row['solar elevation (deg)']
    
    # Calculate Python elevation
    az, el, dist = NOAASolarPosition.calc_solar_position(48.45, -122.33, dt, -8.0, 0)
    
    diff = el - vba_elev
    
    print(f"{dt.strftime('%Y-%m-%d %H:%M'):<20} {vba_elev:10.2f}° {el:12.2f}° {diff:12.2f}°")

print()
print("Analysis:")
print("  - If differences are small (<1°), the solar position algorithm is correct")
print("  - If differences are large (>5°), there's an algorithm or configuration issue")
