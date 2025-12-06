# VBA Comparison Quick Start Guide

## Overview

This guide provides step-by-step instructions for using the VBA comparison test suite.

## Prerequisites

- Python rTemp implementation installed
- Access to VBA rTemp implementation
- pytest installed (`pip install pytest`)

## Quick Start (5 Steps)

### Step 1: Generate Templates

```bash
cd tests/fixtures
python generate_vba_template.py
```

**Output**: 5 CSV template files created
- `vba_solar_position_template.csv`
- `vba_solar_radiation_template.csv`
- `vba_heat_flux_template.csv`
- `vba_temperature_template.csv`
- `vba_full_scenario_template.csv`

### Step 2: Run VBA Implementation

For each row in each template:

1. Open VBA rTemp workbook
2. Enter parameters from template row
3. Run calculation
4. Record outputs in template

**Example** (solar position):
```
Input from template:
- datetime: 2024-07-15 12:00:00
- latitude: 45.0
- longitude: -120.0
- timezone: 8.0

VBA outputs to record:
- azimuth: [record value]
- elevation: [record value]
```

### Step 3: Update Test Code

Edit `tests/integration/test_vba_comparison.py`:

```python
# Find VBAReferenceData class
# Replace placeholder values with actual VBA outputs

@staticmethod
def get_solar_position_reference() -> List[Dict]:
    return [
        {
            'datetime': datetime(2024, 7, 15, 12, 0, 0),
            'latitude': 45.0,
            'longitude': -120.0,
            'timezone': 8.0,
            'expected_azimuth': 180.0,  # ← Replace with VBA value
            'expected_elevation': 68.5,  # ← Replace with VBA value
            'description': 'Summer noon at mid-latitude',
        },
        # ... more cases
    ]
```

### Step 4: Remove Skip Decorators

Remove `@pytest.mark.skip()` from test methods:

```python
# Before:
@pytest.mark.skip(reason="Requires actual VBA reference data")
@pytest.mark.parametrize("ref_data", VBAReferenceData.get_solar_position_reference())
def test_solar_position_accuracy(self, ref_data):

# After:
@pytest.mark.parametrize("ref_data", VBAReferenceData.get_solar_position_reference())
def test_solar_position_accuracy(self, ref_data):
```

### Step 5: Run Tests

```bash
pytest tests/integration/test_vba_comparison.py -v
```

**Expected**: All tests pass within tolerance

## Detailed Workflow

### Phase 1: Solar Position (Easiest)

1. Generate template: `python generate_vba_template.py`
2. Open `vba_solar_position_template.csv`
3. For each row:
   - Enter lat/lon/datetime/timezone in VBA
   - Record azimuth and elevation
4. Update `get_solar_position_reference()` in test code
5. Remove skip decorator from `test_solar_position_accuracy`
6. Run: `pytest tests/integration/test_vba_comparison.py::TestSolarPositionComparison -v`

### Phase 2: Solar Radiation

1. Open `vba_solar_radiation_template.csv`
2. For each row:
   - Set solar method (Bras/Bird/Ryan-Stolzenbach/Iqbal)
   - Enter parameters and cloud cover
   - Record solar radiation
3. Update `get_solar_radiation_reference()` in test code
4. Remove skip decorator from `test_solar_radiation_accuracy`
5. Run: `pytest tests/integration/test_vba_comparison.py::TestSolarRadiationComparison -v`

### Phase 3: Heat Fluxes

1. Open `vba_heat_flux_template.csv`
2. For each row:
   - Enter all parameters
   - Record all flux components
3. Update `get_heat_flux_reference()` in test code
4. Remove skip decorator from `test_heat_flux_components_accuracy`
5. Run: `pytest tests/integration/test_vba_comparison.py::TestHeatFluxComparison -v`

### Phase 4: Temperature

1. Open `vba_temperature_template.csv`
2. Run 24-hour simulation in VBA
3. Record water and sediment temperatures for each timestep
4. Update `get_temperature_reference()` in test code
5. Remove skip decorator from `test_temperature_accuracy`
6. Run: `pytest tests/integration/test_vba_comparison.py::TestTemperatureComparison -v`

## Troubleshooting

### Problem: Tests fail with large differences

**Cause**: Placeholder values still in use

**Solution**: 
```bash
# Check if you updated the reference data
grep "Placeholder" tests/integration/test_vba_comparison.py
```

### Problem: Can't access VBA workbook

**Cause**: VBA file not available

**Solution**: 
1. Use VBA code in `rTemp_VBA.basic`
2. Contact original author (Greg Pelletier)
3. Use published results from papers

### Problem: Tests skip even after updating data

**Cause**: Skip decorator not removed

**Solution**:
```python
# Remove this line:
@pytest.mark.skip(reason="...")
```

### Problem: Small differences (< tolerance)

**Cause**: Numerical precision or acceptable differences

**Solution**:
1. Check if within tolerance
2. Document in `VBA_COMPARISON_NOTES.md`
3. Tests should pass if within tolerance

## Test Execution Options

### Run all tests
```bash
pytest tests/integration/test_vba_comparison.py -v
```

### Run specific test class
```bash
pytest tests/integration/test_vba_comparison.py::TestSolarPositionComparison -v
```

### Run specific test
```bash
pytest tests/integration/test_vba_comparison.py::TestSolarPositionComparison::test_solar_position_accuracy -v
```

### Show detailed output
```bash
pytest tests/integration/test_vba_comparison.py -v -s
```

### Show skipped tests
```bash
pytest tests/integration/test_vba_comparison.py -v -rs
```

### Run only passing tests (skip VBA data tests)
```bash
pytest tests/integration/test_vba_comparison.py -v -k "not skip"
```

## Validation Checklist

Use this checklist to track progress:

### Data Collection
- [ ] Templates generated
- [ ] Solar position data collected (4 cases)
- [ ] Solar radiation data collected (12 cases)
- [ ] Heat flux data collected (3 cases)
- [ ] Temperature data collected (24 timesteps)

### Code Updates
- [ ] Solar position reference updated
- [ ] Solar radiation reference updated
- [ ] Heat flux reference updated
- [ ] Temperature reference updated
- [ ] Skip decorators removed

### Testing
- [ ] Solar position tests pass
- [ ] Solar radiation tests pass
- [ ] Heat flux tests pass
- [ ] Temperature tests pass
- [ ] Full scenario tests pass

### Documentation
- [ ] Differences documented in VBA_COMPARISON_NOTES.md
- [ ] Acceptable differences justified
- [ ] Unacceptable differences investigated
- [ ] Resolution plan created

## Expected Results

### Passing Tests

When all reference data is collected and tests run:

```
tests/integration/test_vba_comparison.py::TestSolarPositionComparison::test_solar_position_accuracy[ref_data0] PASSED
tests/integration/test_vba_comparison.py::TestSolarPositionComparison::test_solar_position_accuracy[ref_data1] PASSED
tests/integration/test_vba_comparison.py::TestSolarPositionComparison::test_solar_position_accuracy[ref_data2] PASSED
tests/integration/test_vba_comparison.py::TestSolarPositionComparison::test_solar_position_accuracy[ref_data3] PASSED
...
17 passed in X.XXs
```

### Acceptable Failures

Some differences may be acceptable:
- Numerical precision (< 1e-10)
- Improved constants
- Bug fixes

Document these in `VBA_COMPARISON_NOTES.md`.

## Time Estimate

- **Template generation**: 5 minutes
- **VBA data collection**: 2-4 hours (depending on VBA access)
- **Code updates**: 30 minutes
- **Test execution**: 5 minutes
- **Documentation**: 30 minutes

**Total**: 3-5 hours

## Support

### Documentation
- Full guide: `tests/integration/README_VBA_COMPARISON.md`
- Data collection: `tests/fixtures/README_VBA_COMPARISON.md`
- Difference tracking: `tests/fixtures/VBA_COMPARISON_NOTES.md`
- Summary: `VBA_COMPARISON_SUMMARY.md`

### Requirements
- Requirements 19.1-19.5 in `.kiro/specs/rtemp-python-complete/requirements.md`
- Design section in `.kiro/specs/rtemp-python-complete/design.md`

### Code
- Test suite: `tests/integration/test_vba_comparison.py`
- Template generator: `tests/fixtures/generate_vba_template.py`
- VBA code: `rTemp_VBA.basic`

## Next Steps

After completing VBA comparison:

1. **Document results** in VBA_COMPARISON_NOTES.md
2. **Create report** summarizing compatibility
3. **Update README** with validation status
4. **Consider automation** for ongoing regression testing
5. **Extend test cases** as needed

## Quick Reference

| Task | Command |
|------|---------|
| Generate templates | `python tests/fixtures/generate_vba_template.py` |
| Run all tests | `pytest tests/integration/test_vba_comparison.py -v` |
| Run solar tests | `pytest tests/integration/test_vba_comparison.py::TestSolarPositionComparison -v` |
| Show skipped | `pytest tests/integration/test_vba_comparison.py -v -rs` |
| Detailed output | `pytest tests/integration/test_vba_comparison.py -v -s` |

## Success Criteria

✅ All tests pass within tolerance  
✅ Differences documented  
✅ Acceptable differences justified  
✅ Python implementation validated against VBA

---

**Ready to start?** Run `python tests/fixtures/generate_vba_template.py` to begin!
