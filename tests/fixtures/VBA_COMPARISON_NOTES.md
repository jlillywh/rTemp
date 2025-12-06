# VBA Comparison Notes

This document tracks differences between the Python and VBA implementations of rTemp.

## Status

**Last Updated**: [Date]  
**Comparison Status**: Pending VBA reference data collection  
**Overall Compatibility**: To be determined

## Known Differences

### 1. Numerical Precision

**Category**: Acceptable  
**Impact**: Negligible (< 1e-10)

**Description**:
Python uses 64-bit IEEE 754 floating-point arithmetic throughout, while VBA may use different precision in some calculations. This leads to minor differences in the least significant digits.

**Example**:
- Python pi: 3.141592653589793
- VBA pi: 3.14159265358979 (as defined in VBA code)
- Difference: < 1e-14

**Resolution**: Documented as acceptable. Tolerance thresholds account for this.

---

### 2. Constant Definitions

**Category**: Acceptable  
**Impact**: Negligible

**Description**:
Some physical constants may have slightly different values due to:
- More recent scientific standards
- Different source references
- Rounding in VBA code

**Examples**:
- Stefan-Boltzmann constant
- Gas constants
- Conversion factors

**Resolution**: Python uses more precise values from current scientific standards. Differences are within tolerance.

---

### 3. Algorithm Improvements

**Category**: Intentional Improvement  
**Impact**: Minor (within tolerance)

**Description**:
The Python implementation may include improvements over the VBA version:
- More robust edge case handling
- Improved numerical stability
- Bug fixes identified during porting

**Examples**:
- [To be documented as identified]

**Resolution**: Improvements are documented and justified. Results remain within tolerance.

---

### 4. Input Validation

**Category**: Enhancement  
**Impact**: None on valid inputs

**Description**:
Python implementation includes more comprehensive input validation:
- Type checking with type hints
- Range validation for all parameters
- Clear error messages

**Resolution**: Enhanced validation does not affect results for valid inputs. Provides better user experience.

---

### 5. Missing Data Handling

**Category**: To be verified  
**Impact**: To be determined

**Description**:
Need to verify that missing data handling (values ≤ -999) matches VBA behavior exactly.

**Test Cases Needed**:
- Missing air temperature
- Missing dewpoint
- Missing wind speed
- Missing cloud cover

**Resolution**: Pending verification with VBA reference data.

---

### 6. Timestep Handling

**Category**: To be verified  
**Impact**: To be determined

**Description**:
Need to verify that variable timestep handling matches VBA:
- Large timestep warnings (> 2 hours)
- Temperature reset for very large gaps (> 4 hours)
- Duplicate timestep detection

**Test Cases Needed**:
- Regular hourly data
- Irregular timesteps
- Large gaps
- Duplicate timestamps

**Resolution**: Pending verification with VBA reference data.

---

## Test Results Summary

### Solar Position Tests

| Test Case | Python Azimuth | VBA Azimuth | Diff | Python Elevation | VBA Elevation | Diff | Status |
|-----------|----------------|-------------|------|------------------|---------------|------|--------|
| Summer noon mid-lat | TBD | TBD | TBD | TBD | TBD | TBD | Pending |
| Winter noon mid-lat | TBD | TBD | TBD | TBD | TBD | TBD | Pending |
| High latitude | TBD | TBD | TBD | TBD | TBD | TBD | Pending |
| Equator equinox | TBD | TBD | TBD | TBD | TBD | TBD | Pending |

**Tolerance**: ±0.01°

---

### Solar Radiation Tests

| Test Case | Method | Python (W/m²) | VBA (W/m²) | Diff | Status |
|-----------|--------|---------------|------------|------|--------|
| Clear sky summer | Bras | TBD | TBD | TBD | Pending |
| Clear sky summer | Bird | TBD | TBD | TBD | Pending |
| Clear sky summer | Ryan-Stolz | TBD | TBD | TBD | Pending |
| Clear sky summer | Iqbal | TBD | TBD | TBD | Pending |
| Cloudy summer | Bras | TBD | TBD | TBD | Pending |

**Tolerance**: ±0.1 W/m²

---

### Heat Flux Tests

| Test Case | Flux Component | Python (W/m²) | VBA (W/m²) | Diff | Status |
|-----------|----------------|---------------|------------|------|--------|
| Summer midday | Solar | TBD | TBD | TBD | Pending |
| Summer midday | Longwave atm | TBD | TBD | TBD | Pending |
| Summer midday | Longwave back | TBD | TBD | TBD | Pending |
| Summer midday | Evaporation | TBD | TBD | TBD | Pending |
| Summer midday | Convection | TBD | TBD | TBD | Pending |

**Tolerance**: ±0.1 W/m²

---

### Temperature Tests

| Test Case | Timestep | Python (°C) | VBA (°C) | Diff | Status |
|-----------|----------|-------------|----------|------|--------|
| Day-night cycle | 0 | TBD | TBD | TBD | Pending |
| Day-night cycle | 12 | TBD | TBD | TBD | Pending |
| Day-night cycle | 24 | TBD | TBD | TBD | Pending |

**Tolerance**: ±0.01°C

---

## Issues Identified

### Issue #1: [Title]

**Status**: [Open/Resolved]  
**Priority**: [High/Medium/Low]  
**Category**: [Bug/Enhancement/Documentation]

**Description**:
[Detailed description of the issue]

**Impact**:
[How this affects comparison with VBA]

**Test Case**:
[Specific test case that reveals the issue]

**Resolution**:
[How the issue was resolved or plan to resolve]

---

## Recommendations

### For Python Implementation

1. [Recommendation 1]
2. [Recommendation 2]

### For VBA Implementation

1. [Recommendation 1]
2. [Recommendation 2]

### For Documentation

1. [Recommendation 1]
2. [Recommendation 2]

---

## Validation Sign-off

### Phase 1: Reference Data Collection
- [ ] Solar position data collected
- [ ] Solar radiation data collected
- [ ] Heat flux data collected
- [ ] Temperature data collected
- [ ] Full scenario data collected

**Completed by**: [Name]  
**Date**: [Date]

### Phase 2: Initial Comparison
- [ ] All tests executed
- [ ] Results within tolerance
- [ ] Differences documented
- [ ] Issues identified

**Completed by**: [Name]  
**Date**: [Date]

### Phase 3: Issue Resolution
- [ ] All issues investigated
- [ ] Critical issues resolved
- [ ] Acceptable differences justified
- [ ] Documentation updated

**Completed by**: [Name]  
**Date**: [Date]

### Phase 4: Final Validation
- [ ] All tests passing
- [ ] Documentation complete
- [ ] Sign-off obtained

**Completed by**: [Name]  
**Date**: [Date]

---

## References

- VBA Implementation: `rTemp_VBA.basic`
- Python Implementation: `rtemp/` package
- Requirements: `.kiro/specs/rtemp-python-complete/requirements.md`
- Design: `.kiro/specs/rtemp-python-complete/design.md`
- Test Code: `tests/integration/test_vba_comparison.py`

---

## Change Log

| Date | Author | Change |
|------|--------|--------|
| [Date] | [Name] | Initial document creation |
