# VBA Validation Tests

This directory contains validation tests comparing the Python rTemp implementation against the original VBA version.

## Purpose

These tests validate that the Python implementation produces results consistent with the original VBA rTemp model by Greg Pelletier (Washington State Department of Ecology).

## Files

### Main Validation Script
- **`vba_validation.py`** - Main validation script that:
  - Reads VBA sample data from `tests/fixtures/vba_sample_data.txt`
  - Runs Python rTemp with identical inputs
  - Compares results timestep-by-timestep
  - Generates detailed comparison report

### Debug Scripts (for development/troubleshooting)
- **`debug_longwave.py`** - Traces longwave radiation calculations
- **`debug_solar_position.py`** - Traces solar position calculations step-by-step
- **`check_azimuth.py`** - Analyzes azimuth convention differences
- **`test_azimuth_convention.py`** - Tests azimuth at midnight and noon

### Output Files
- **`vba_validation_output.csv`** - Python model output for comparison

## Running the Validation

From the project root directory:

```bash
# Activate virtual environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Run validation
python tests/validation/vba_validation.py
```

## Expected Results

The validation should show:
- **Solar Position**: < 0.13° difference
- **Longwave Radiation**: < 0.15% difference
- **Water Temperature**: < 0.08°C difference
- **Convection/Evaporation**: ~37-52% difference (known, doesn't affect temperature)

See `docs/validation/COMPREHENSIVE_VALIDATION_RESULTS.md` for detailed results.

## Test Data

The validation uses sample data from the original VBA implementation:
- **Location**: 48.45°N, 122.33°W (Puget Sound, Washington)
- **Date**: October 1, 2003, 00:00-00:30
- **Timesteps**: 3 (15-minute intervals)
- **Conditions**: Nighttime, no solar radiation

## Validation Status

✅ **VALIDATED** - Python implementation matches VBA with excellent accuracy:
- Water temperature: ± 0.08°C
- Solar position: ± 0.13°
- Longwave radiation: ± 0.15%

## Documentation

Full validation documentation is available in `docs/validation/`:
- **COMPREHENSIVE_VALIDATION_RESULTS.md** - Detailed comparison of all parameters
- **BUG_FIXES_SUMMARY.md** - Bugs found and fixed during validation
- **VBA_VALIDATION_RESULTS.md** - Summary of validation findings

## Notes

This is an **informal validation test** (not automated unit tests) used for:
1. Initial validation against VBA reference implementation
2. Debugging and troubleshooting
3. Documenting known differences
4. Providing confidence in the Python implementation

For automated regression tests, see `tests/integration/test_vba_comparison.py`.
