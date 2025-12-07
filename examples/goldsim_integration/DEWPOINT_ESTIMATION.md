# Dewpoint Estimation Guide

## Problem

You may not have dewpoint data available for your GoldSim model. Dewpoint is needed for calculating atmospheric humidity and longwave radiation in rTemp.

## Solution

The modified adapter (`rtemp_goldsim_adapter_with_dewpoint_estimation.py`) can estimate dewpoint from air temperature when dewpoint data is not available.

## How It Works

The adapter uses typical dewpoint depression values:

- Dewpoint Min = Air Temp Min - 2°C (humid nighttime conditions)
- Dewpoint Max = Air Temp Max - 8°C (drier daytime conditions)

These are reasonable approximations for temperate climates. The actual dewpoint depression varies with humidity:
- Humid conditions: 2-5°C depression
- Moderate conditions: 5-10°C depression  
- Dry conditions: 10-20°C depression

## Usage Option 1: Always Estimate Dewpoint

Set both dewpoint inputs to -999 in GoldSim:

```
Dewpoint_Min = -999
Dewpoint_Max = -999
```

The adapter will automatically estimate dewpoint from air temperature.

## Usage Option 2: Estimate Only When Missing

If you have dewpoint data for some periods but not others, you can:
- Use actual dewpoint values when available
- Set to -999 when missing

The adapter will estimate only when it sees -999.

## Adjusting Depression Values

If you know your climate is particularly humid or dry, you can adjust the constants in the adapter script:

```python
# For humid climates (coastal, tropical)
DEWPOINT_DEPRESSION_MIN = 1.0  # °C
DEWPOINT_DEPRESSION_MAX = 5.0  # °C

# For dry climates (arid, desert)
DEWPOINT_DEPRESSION_MIN = 5.0  # °C
DEWPOINT_DEPRESSION_MAX = 15.0  # °C

# For moderate climates (default)
DEWPOINT_DEPRESSION_MIN = 2.0  # °C
DEWPOINT_DEPRESSION_MAX = 8.0  # °C
```

## Installation

1. Replace your current `rtemp_goldsim_adapter.py` with `rtemp_goldsim_adapter_with_dewpoint_estimation.py`
2. Rename it to `rtemp_goldsim_adapter.py`
3. In GoldSim, set dewpoint inputs to -999 (or keep your actual values if you have them)
4. Run your simulation

## Verification

Check the log file (`GSPy_314.log`) for messages like:

```
Dewpoint estimated from air temperature: Td_min=13.0°C, Td_max=22.0°C (depressions: 2.0°C, 8.0°C)
```

This confirms the estimation is working.

## Accuracy

Dewpoint estimation is less accurate than measured data, but it's acceptable for many applications:

- Good for: Screening studies, preliminary analysis, locations without humidity data
- Less good for: Detailed energy balance studies, calibration, validation

If possible, obtain actual dewpoint or relative humidity data for better accuracy.

## Alternative: Relative Humidity

If you have relative humidity instead of dewpoint, you can calculate dewpoint using:

```
Td = T - ((100 - RH) / 5)
```

Where:
- Td = dewpoint (°C)
- T = air temperature (°C)
- RH = relative humidity (%)

This is the Magnus formula approximation, accurate within ±1°C for typical conditions.
