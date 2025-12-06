# VBA Comparison Reference Data

This directory contains reference data from the VBA implementation for comparison testing.

## Purpose

The Python implementation of rTemp must produce results that match the original VBA implementation within specified tolerances:

- Solar position: ±0.01°
- Solar radiation: ±0.1 W/m²
- Heat fluxes: ±0.1 W/m²
- Temperature: ±0.01°C

## Generating Reference Data

To populate the reference data for comparison tests:

### 1. Prepare Test Cases

Use the test cases defined in `test_vba_comparison.py`:

```python
# Example test cases
test_cases = [
    {
        'datetime': '2024-07-15 12:00:00',
        'latitude': 45.0,
        'longitude': -120.0,
        'timezone': 8.0,
        'description': 'Summer noon at mid-latitude'
    },
    {
        'datetime': '2024-01-15 12:00:00',
        'latitude': 45.0,
        'longitude': -120.0,
        'timezone': 8.0,
        'description': 'Winter noon at mid-latitude'
    },
    # ... more test cases
]
```

### 2. Run VBA Implementation

For each test case:

1. Open the rTemp VBA workbook
2. Enter the site parameters (latitude, longitude, timezone, elevation)
3. Enter the meteorological data
4. Run the calculation
5. Record the outputs

### 3. Record VBA Outputs

Create CSV files with the following formats:

#### Solar Position Reference (`vba_solar_position.csv`)

```csv
datetime,latitude,longitude,timezone,azimuth,elevation,description
2024-07-15 12:00:00,45.0,-120.0,8.0,180.0,68.5,Summer noon at mid-latitude
2024-01-15 12:00:00,45.0,-120.0,8.0,180.0,21.5,Winter noon at mid-latitude
```

#### Solar Radiation Reference (`vba_solar_radiation.csv`)

```csv
datetime,latitude,longitude,timezone,elevation_m,method,cloud_cover,solar_radiation,description
2024-07-15 12:00:00,45.0,-120.0,8.0,100.0,Bras,0.0,850.0,Clear sky summer noon - Bras
2024-07-15 12:00:00,45.0,-120.0,8.0,100.0,Bird,0.0,900.0,Clear sky summer noon - Bird
```

#### Heat Flux Reference (`vba_heat_flux.csv`)

```csv
datetime,latitude,longitude,timezone,elevation_m,water_depth,initial_water_temp,air_temp,dewpoint,wind_speed,cloud_cover,solar_radiation,longwave_atm,longwave_back,evaporation,convection,description
2024-07-15 12:00:00,45.0,-120.0,8.0,100.0,2.0,20.0,25.0,18.0,2.0,0.3,700.0,350.0,-450.0,-80.0,-20.0,Summer midday
```

#### Temperature Reference (`vba_temperature.csv`)

```csv
timestep,datetime,latitude,longitude,timezone,elevation_m,water_depth,initial_water_temp,air_temp,dewpoint,wind_speed,cloud_cover,water_temperature,sediment_temperature,description
0,2024-07-15 00:00:00,45.0,-120.0,8.0,100.0,2.0,15.0,15.0,10.0,2.0,0.3,15.0,15.0,Day-night cycle
1,2024-07-15 12:00:00,45.0,-120.0,8.0,100.0,2.0,15.0,25.0,18.0,2.5,0.2,16.5,15.2,Day-night cycle
2,2024-07-16 00:00:00,45.0,-120.0,8.0,100.0,2.0,15.0,16.0,11.0,2.0,0.4,16.2,15.3,Day-night cycle
```

### 4. Update Test Code

Once reference data is collected, update the `VBAReferenceData` class in `test_vba_comparison.py`:

```python
@staticmethod
def get_solar_position_reference() -> List[Dict]:
    return [
        {
            'datetime': datetime(2024, 7, 15, 12, 0, 0),
            'latitude': 45.0,
            'longitude': -120.0,
            'timezone': 8.0,
            'expected_azimuth': 180.0,  # Replace with actual VBA output
            'expected_elevation': 68.5,  # Replace with actual VBA output
            'description': 'Summer noon at mid-latitude',
        },
        # ... more cases
    ]
```

## Test Execution

Run the comparison tests:

```bash
# Run all VBA comparison tests
pytest tests/integration/test_vba_comparison.py -v

# Run specific test class
pytest tests/integration/test_vba_comparison.py::TestSolarPositionComparison -v

# Run with detailed output
pytest tests/integration/test_vba_comparison.py -v -s
```

## Documenting Differences

If tests fail, document the differences:

1. **Acceptable Differences**:
   - Numerical precision (< 1e-10)
   - Improved constants (e.g., more precise pi)
   - Bug fixes from VBA version

2. **Unacceptable Differences**:
   - Differences exceeding tolerance thresholds
   - Systematic errors in calculations
   - Missing functionality

Document all differences in `VBA_COMPARISON_NOTES.md`.

## Reference Data Files

Expected files in this directory:

- `vba_solar_position.csv` - Solar position reference data
- `vba_solar_radiation.csv` - Solar radiation reference data
- `vba_heat_flux.csv` - Heat flux reference data
- `vba_temperature.csv` - Temperature calculation reference data
- `vba_full_scenario.csv` - Complete 24-hour scenario reference
- `VBA_COMPARISON_NOTES.md` - Documentation of differences

## Validation Checklist

- [ ] Solar position data collected for all test cases
- [ ] Solar radiation data collected for all methods
- [ ] Heat flux data collected for representative conditions
- [ ] Temperature data collected for multi-timestep scenarios
- [ ] Full 24-hour scenario data collected
- [ ] All reference data loaded into test code
- [ ] Tests executed and results documented
- [ ] Differences analyzed and documented
- [ ] Acceptable differences justified
- [ ] Unacceptable differences investigated and resolved

## Notes

- VBA implementation file: `rTemp_VBA.basic`
- VBA workbook location: [Specify location]
- VBA version: [Specify version]
- Date reference data collected: [Specify date]
- Person who collected data: [Specify name]

## Contact

For questions about VBA comparison testing:
- Review the design document: `.kiro/specs/rtemp-python-complete/design.md`
- Check requirements: `.kiro/specs/rtemp-python-complete/requirements.md`
- See task list: `.kiro/specs/rtemp-python-complete/tasks.md`
