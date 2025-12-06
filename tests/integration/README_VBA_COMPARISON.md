# VBA Comparison Test Suite

## Overview

This test suite validates that the Python implementation of rTemp produces results matching the original VBA implementation within specified tolerances.

## Requirements Validated

- **Requirement 19.1**: Solar position accuracy within ±0.01°
- **Requirement 19.2**: Solar radiation accuracy within ±0.1 W/m²
- **Requirement 19.3**: Heat flux accuracy within ±0.1 W/m²
- **Requirement 19.4**: Temperature accuracy within ±0.01°C
- **Requirement 19.5**: Complete scenario compatibility

## Test Structure

### Test Classes

1. **TestSolarPositionComparison**
   - Validates solar azimuth and elevation calculations
   - Tests multiple locations, dates, and times
   - Ensures deterministic behavior

2. **TestSolarRadiationComparison**
   - Validates all solar radiation methods (Bras, Bird, Ryan-Stolzenbach, Iqbal)
   - Tests various cloud cover conditions
   - Verifies zero radiation at night

3. **TestHeatFluxComparison**
   - Validates all heat flux components
   - Tests energy balance (sum of components = net flux)
   - Covers various meteorological conditions

4. **TestTemperatureComparison**
   - Validates water and sediment temperature calculations
   - Tests multi-timestep scenarios
   - Verifies minimum temperature enforcement

5. **TestFullScenarioComparison**
   - Validates complete 24-hour simulations
   - Tests all method combinations
   - Ensures end-to-end compatibility

6. **TestDifferenceDocumentation**
   - Documents known differences
   - Explains acceptable variations
   - Records intentional improvements

## Current Status

**Status**: Framework complete, awaiting VBA reference data

The test framework is fully implemented with:
- ✅ Test structure and organization
- ✅ Tolerance definitions
- ✅ Parameterized test cases
- ✅ Helper utilities
- ✅ Documentation
- ⏳ VBA reference data (placeholder values currently used)

## Running Tests

### Run All VBA Comparison Tests

```bash
pytest tests/integration/test_vba_comparison.py -v
```

### Run Specific Test Class

```bash
pytest tests/integration/test_vba_comparison.py::TestSolarPositionComparison -v
```

### Run Tests That Don't Require VBA Data

```bash
pytest tests/integration/test_vba_comparison.py -v -k "not skip"
```

### Show Skipped Tests

```bash
pytest tests/integration/test_vba_comparison.py -v -rs
```

## Collecting VBA Reference Data

### Step 1: Generate Templates

Run the template generator:

```bash
cd tests/fixtures
python generate_vba_template.py
```

This creates CSV templates:
- `vba_solar_position_template.csv`
- `vba_solar_radiation_template.csv`
- `vba_heat_flux_template.csv`
- `vba_temperature_template.csv`
- `vba_full_scenario_template.csv`

### Step 2: Run VBA Implementation

For each test case in the templates:

1. Open the rTemp VBA workbook (`rTemp_VBA.basic`)
2. Enter the site parameters from the template
3. Enter the meteorological data from the template
4. Run the VBA calculation
5. Record all outputs

### Step 3: Fill Templates

Fill in the VBA output columns in each template CSV file.

### Step 4: Update Test Code

Update the `VBAReferenceData` class in `test_vba_comparison.py` with actual VBA values:

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

### Step 5: Remove Skip Decorators

Once actual VBA data is available, remove the `@pytest.mark.skip()` decorators from the test methods.

### Step 6: Run Tests

```bash
pytest tests/integration/test_vba_comparison.py -v
```

## Test Cases

### Solar Position Test Cases

| Case | Date | Latitude | Longitude | Timezone | Description |
|------|------|----------|-----------|----------|-------------|
| 1 | 2024-07-15 12:00 | 45.0 | -120.0 | 8.0 | Summer noon mid-latitude |
| 2 | 2024-01-15 12:00 | 45.0 | -120.0 | 8.0 | Winter noon mid-latitude |
| 3 | 2024-06-21 12:00 | 60.0 | -120.0 | 8.0 | Summer solstice high latitude |
| 4 | 2024-03-20 12:00 | 0.0 | 0.0 | 0.0 | Equinox at equator |

### Solar Radiation Test Cases

Tests all four methods (Bras, Bird, Ryan-Stolzenbach, Iqbal) with:
- Clear sky (cloud cover = 0.0)
- Partly cloudy (cloud cover = 0.3, 0.5)
- Overcast (cloud cover = 1.0)

### Heat Flux Test Cases

| Case | Conditions | Description |
|------|------------|-------------|
| 1 | Summer midday | High solar, warm air, moderate wind |
| 2 | Winter midday | Low solar, cold air, higher wind |
| 3 | Summer night | No solar, cool air, moderate wind |

### Temperature Test Cases

24-hour simulation with hourly timesteps:
- Initial temperature: 15°C
- Air temperature: 15-25°C (sinusoidal)
- Dewpoint: 5°C below air temperature
- Wind speed: 2 m/s
- Cloud cover: 0.3

## Tolerance Thresholds

As specified in Requirements 19.1-19.5:

| Metric | Tolerance | Units |
|--------|-----------|-------|
| Solar azimuth | ±0.01 | degrees |
| Solar elevation | ±0.01 | degrees |
| Solar radiation | ±0.1 | W/m² |
| Longwave radiation | ±0.1 | W/m² |
| Evaporation flux | ±0.1 | W/m² |
| Convection flux | ±0.1 | W/m² |
| Other heat fluxes | ±0.1 | W/m² |
| Water temperature | ±0.01 | °C |
| Sediment temperature | ±0.01 | °C |

## Documenting Differences

If tests fail, document differences in `tests/fixtures/VBA_COMPARISON_NOTES.md`:

### Acceptable Differences

- Numerical precision (< 1e-10)
- Improved physical constants
- Bug fixes from VBA version
- Enhanced edge case handling

### Unacceptable Differences

- Differences exceeding tolerance
- Systematic calculation errors
- Missing functionality
- Incorrect algorithm implementation

## Troubleshooting

### Tests Are Skipped

**Cause**: VBA reference data not yet collected  
**Solution**: Follow steps in "Collecting VBA Reference Data" section

### Tests Fail With Large Differences

**Cause**: Placeholder values still in use  
**Solution**: Replace placeholder values with actual VBA outputs

### Tests Fail With Small Differences

**Cause**: May be acceptable numerical precision differences  
**Solution**: 
1. Check if difference is < tolerance
2. Document in VBA_COMPARISON_NOTES.md
3. Investigate if difference is systematic

### VBA Implementation Not Available

**Cause**: VBA workbook not accessible  
**Solution**: 
1. Contact original author (Greg Pelletier, WA Dept of Ecology)
2. Use VBA code in `rTemp_VBA.basic` to recreate workbook
3. Consider using published results from papers/reports

## Files

### Test Files
- `test_vba_comparison.py` - Main test suite
- `README_VBA_COMPARISON.md` - This file

### Fixture Files
- `tests/fixtures/generate_vba_template.py` - Template generator
- `tests/fixtures/README_VBA_COMPARISON.md` - Fixture documentation
- `tests/fixtures/VBA_COMPARISON_NOTES.md` - Difference documentation
- `tests/fixtures/vba_*_template.csv` - Data collection templates (generated)
- `tests/fixtures/vba_*_reference.csv` - Actual VBA data (to be created)

### Reference Files
- `rTemp_VBA.basic` - Original VBA implementation
- `.kiro/specs/rtemp-python-complete/requirements.md` - Requirements
- `.kiro/specs/rtemp-python-complete/design.md` - Design document

## Contributing

When adding new VBA comparison tests:

1. Add test case to appropriate `VBAReferenceData` method
2. Collect VBA output for the new test case
3. Update documentation
4. Run tests to verify
5. Document any differences

## References

- Original VBA implementation by Greg Pelletier, Washington State Department of Ecology
- NOAA Solar Position Algorithm
- Requirements document: `.kiro/specs/rtemp-python-complete/requirements.md`
- Design document: `.kiro/specs/rtemp-python-complete/design.md`

## Contact

For questions about VBA comparison testing:
- Review the requirements (Requirement 19.1-19.5)
- Check the design document testing strategy section
- See task list: `.kiro/specs/rtemp-python-complete/tasks.md` (Task 24)
