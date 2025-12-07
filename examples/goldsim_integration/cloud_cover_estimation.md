# Estimating Cloud Cover from Precipitation

If you have daily precipitation data but no cloud cover measurements, you can estimate cloud cover using this simple approach or something similar.

## Stepped Approach

```
If Precip = 0:
    Cloud_Cover = 0.3
Else if Precip < 2.5:
    Cloud_Cover = 0.5
Else if Precip < 10:
    Cloud_Cover = 0.7
Else:
    Cloud_Cover = 0.9
```

Provides:
- 0.3 for dry days (30% clouds)
- 0.5 for light rain (50% clouds)
- 0.7 for moderate rain (70% clouds)
- 0.9 for heavy rain (90% clouds)

## Typical Cloud Cover Values

- Clear sky: 0.0 - 0.2
- Partly cloudy: 0.3 - 0.5
- Mostly cloudy: 0.6 - 0.8
- Overcast/rain: 0.8 - 1.0

## Default Value

If you have no precipitation data, use 0.3-0.5 as a reasonable baseline for average conditions.

## Impact on Water Temperature

Cloud cover affects:
- Solar radiation (more clouds = less solar heating)
- Longwave radiation (more clouds = more atmospheric radiation)
- Net effect: Higher cloud cover generally reduces water temperature

For sensitivity analysis, vary cloud cover between 0.2 (clear) and 0.8 (overcast) to see the impact on your results.
