# Simplified GoldSim External Element Input Order

## 12 Inputs (Dewpoint Removed - Estimated Automatically)

1. Current_Water_Temp (°C)
2. Current_Sediment_Temp (°C)
3. Water_Depth (meters)
4. Latitude (degrees, -90 to 90)
5. Longitude (degrees, -180 to 180)
6. Elevation (meters)
7. Timezone (hours from UTC)
8. Air_Temp_Min (°C)
9. Air_Temp_Max (°C)
10. Wind_Speed_Avg (m/s)
11. Cloud_Cover_Avg (fraction, 0-1)
12. Simulation_Date (elapsed days)

## 3 Outputs (Unchanged)

1. New_Water_Temp (°C)
2. New_Sediment_Temp (°C)
3. Daily_Avg_Net_Flux (W/m²)

## What Changed

Removed from inputs:
- Dewpoint_Min (now estimated as Air_Temp_Min - 2°C)
- Dewpoint_Max (now estimated as Air_Temp_Max - 8°C)

The adapter automatically estimates dewpoint from air temperature using typical dewpoint depression values suitable for moderate climates.

## Adjusting for Your Climate

Edit `rtemp_goldsim_adapter.py` lines 42-43:

```python
# For humid climates (coastal, tropical)
DEWPOINT_DEPRESSION_MIN = 1.0
DEWPOINT_DEPRESSION_MAX = 5.0

# For moderate climates (default)
DEWPOINT_DEPRESSION_MIN = 2.0
DEWPOINT_DEPRESSION_MAX = 8.0

# For dry climates (arid, desert)
DEWPOINT_DEPRESSION_MIN = 5.0
DEWPOINT_DEPRESSION_MAX = 15.0
```

## Files Updated

- `rtemp_goldsim_adapter.py` - Simplified adapter (12 inputs)
- `GSPy_314.json` - Updated configuration (12 inputs)
- `DEWPOINT_ESTIMATION_GUIDE.md` - Usage guide

## GoldSim Configuration

In your External Element:
1. Remove Dewpoint_Min input (was input 9)
2. Remove Dewpoint_Max input (was input 10)
3. Keep all other inputs in the same order
4. Outputs remain unchanged

The adapter will log estimated dewpoint values in the log file for verification.
