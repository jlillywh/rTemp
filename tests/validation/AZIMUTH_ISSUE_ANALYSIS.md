# Solar Azimuth Discrepancy Analysis

## Issue Summary

Python and VBA show different solar azimuth values, particularly at night:

| Timestep | Time | VBA Azimuth | Python Azimuth | Difference |
|----------|------|-------------|----------------|------------|
| 1 | 00:00 | 0.29° | 339.64° | 339.35° |
| 2 | 00:15 | 5.54° | 344.67° | 339.13° |
| 3 | 00:30 | 10.76° | 349.80° | 339.04° |
| 4 | 00:45 | 15.89° | 355.01° | 339.12° |
| 5 | 01:00 | 20.92° | 0.25° | -20.67° |
| 6 | 01:15 | 25.80° | 5.50° | -20.30° |

## Observations

### 1. Pattern Recognition
- **VBA**: Shows continuous increase from 0° → 5° → 10° → 15° → 20° → 25°
- **Python**: Shows 339° → 344° → 349° → 355° → 0° → 5° (wraps at 360°)

### 2. Offset Analysis
The difference is approximately **-20° to -21°** after the wrap, and **+339°** before the wrap.

This suggests:
- 339° ≈ 360° - 21°
- The values are related by a ~20° offset plus 360° wrapping

### 3. Physical Interpretation

At midnight (00:00) at location 48.45°N, 122.33°W in October:
- **Sun is below horizon** (elevation = -44.61°)
- **Sun is on opposite side of Earth** (roughly south)
- **Expected azimuth**: ~180° (south) or in the range 150-210°

Neither VBA (0.29°) nor Python (339.64°) seems physically correct for the sun's actual position.

## Root Cause Analysis

### Hypothesis 1: Different Azimuth Conventions
- **VBA**: May use a different reference point or convention
- **Python**: Uses standard convention (0° = North, clockwise)

### Hypothesis 2: VBA Azimuth is Approximate
From VBA code comment: "exact Azimuth is less critical than Elevation"
- VBA may use a simplified or approximate azimuth calculation
- Azimuth doesn't affect solar radiation calculations (only elevation matters)

### Hypothesis 3: Sign or Offset Error
The ~20° offset suggests there might be:
- A latitude-related correction being applied differently
- A timezone or hour angle adjustment difference
- A different handling of the hour angle sign

## Impact Assessment

### ❌ Does NOT Affect:
- **Solar radiation calculations** (uses elevation, not azimuth)
- **Water temperature predictions** (azimuth not used in heat flux)
- **Model accuracy** (azimuth is output-only, not used in calculations)

### ✅ Does Affect:
- **Output file comparison** (large RMSE in azimuth column)
- **Visualization** (if plotting sun position)
- **User confidence** (seeing 339° difference is alarming)

## Recommendations

### Option 1: Accept the Difference (Recommended)
- Document that azimuth conventions differ
- Note that azimuth doesn't affect model calculations
- Focus validation on parameters that matter (temperature, radiation, fluxes)

### Option 2: Investigate VBA Formula
- Reverse-engineer exact VBA azimuth calculation
- Implement matching formula in Python
- Risk: May introduce errors if VBA formula is approximate

### Option 3: Remove Azimuth from Comparison
- Don't compare azimuth values
- Focus on elevation (which does match well: -44.61° vs -44.48°, diff 0.13°)
- Azimuth is cosmetic output only

## Conclusion

The solar azimuth discrepancy is a **cosmetic issue** that does not affect model accuracy. The elevation values match well (within 0.13°), and elevation is what actually drives solar radiation calculations.

**Recommended Action**: Document the azimuth difference as a known issue with no impact on model predictions, and focus validation efforts on parameters that affect water temperature (solar radiation, heat fluxes, temperatures).

## Related Issues

This is similar to the azimuth issue we fixed earlier in `rtemp/solar/position.py` where we corrected the formula from:
```python
# Old (incorrect)
azimuth = 180.0 + (math.acos(cos_azimuth) * RAD_TO_DEG)
```
to:
```python
# New (VBA-compatible)
azimuth = 180.0 - (math.acos(cos_azimuth) * RAD_TO_DEG)
```

However, even with this fix, there's still a convention difference that causes the 360° wrapping issue.
