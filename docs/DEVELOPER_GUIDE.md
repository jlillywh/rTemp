# rTemp Developer Guide

This guide is for developers who want to contribute to the rTemp project, extend its functionality, or understand its internal architecture.

## About This Implementation

This Python implementation is based on the original VBA rTemp model by Greg Pelletier (Washington State Department of Ecology). The implementation has been:

- ✅ **Validated**: 0.13°C RMSE against VBA over 3 months
- ✅ **Tested**: 346 automated tests passing
- ✅ **Documented**: Comprehensive inline and external documentation
- ✅ **Production-Ready**: Suitable for research and regulatory applications

### Key Improvements Over VBA

1. **Fixed Bugs**: Corrected three formula errors in Bras solar radiation method
2. **Enhanced Testing**: Comprehensive unit, property, and integration tests
3. **Better Validation**: Input checking with informative warnings
4. **Modern Tools**: Uses pandas, numpy, and Python ecosystem
5. **Cross-Platform**: Runs on Windows, macOS, and Linux

## Table of Contents

1. [Development Setup](#development-setup)
2. [Project Architecture](#project-architecture)
3. [Code Organization](#code-organization)
4. [Development Workflow](#development-workflow)
5. [Testing](#testing)
6. [Validation](#validation)
7. [Code Style](#code-style)
8. [Adding New Features](#adding-new-features)
9. [Performance Optimization](#performance-optimization)
10. [Documentation](#documentation)
11. [Release Process](#release-process)

---

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- pip package manager
- Virtual environment tool (venv or conda)

### Initial Setup

1. **Clone the repository:**
```bash
git clone <repository-url>
cd rtemp
```

2. **Create virtual environment:**
```bash
python -m venv .venv

# Activate on Windows:
.venv\Scripts\activate

# Activate on macOS/Linux:
source .venv/bin/activate
```

3. **Install in development mode:**
```bash
pip install -e ".[dev]"
```

This installs:
- Core dependencies (numpy, pandas, python-dateutil)
- Development tools (pytest, hypothesis, black, mypy, flake8, isort)

4. **Verify installation:**
```bash
pytest tests/
```

### IDE Setup

**VS Code:**

Recommended extensions:
- Python (Microsoft)
- Pylance
- Python Test Explorer

Settings (`.vscode/settings.json`):
```json
{
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.mypyEnabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.unittestEnabled": false,
    "editor.formatOnSave": true
}
```

**PyCharm:**

1. Set interpreter to virtual environment
2. Enable pytest as test runner
3. Configure black as formatter
4. Enable mypy type checking

---

## Project Architecture

### High-Level Design

The rTemp model follows a modular, layered architecture:

```
┌─────────────────────────────────────────────────────────┐
│                    User Interface                        │
│              (RTempModel.run() method)                   │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                  Model Layer                             │
│  - Configuration management                              │
│  - Timestep iteration                                    │
│  - State management                                      │
│  - Validation and error handling                         │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                 Physics Layer                            │
│  ┌──────────────┬──────────────┬──────────────┐        │
│  │   Solar      │ Atmospheric  │  Heat Flux   │        │
│  │ Calculations │  Radiation   │ Calculations │        │
│  └──────────────┴──────────────┴──────────────┘        │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                Utilities Layer                           │
│  - Unit conversions                                      │
│  - Atmospheric helpers                                   │
│  - Input validation                                      │
│  - Constants                                             │
└─────────────────────────────────────────────────────────┘
```

### Design Principles

1. **Separation of Concerns**: Each module has a single, well-defined responsibility
2. **Immutability**: Configuration objects are immutable (dataclasses with frozen=True where appropriate)
3. **Type Safety**: All functions have type hints
4. **Testability**: Pure functions where possible, dependency injection for testing
5. **Extensibility**: Easy to add new calculation methods via inheritance

### Key Design Patterns

**Strategy Pattern**: Used for calculation methods
- Solar radiation methods inherit from base class
- Longwave emissivity methods inherit from base class
- Wind function methods inherit from base class

**Factory Pattern**: Method selection in RTempModel
- Configuration specifies method names
- Model instantiates appropriate classes

**Dataclass Pattern**: Configuration and data structures
- ModelConfiguration
- ModelState
- HeatFluxComponents
- SolarPositionResult

---

## Code Organization

### Directory Structure

```
rtemp/
├── __init__.py                 # Package initialization, exports
├── model.py                    # Main RTempModel class
├── config.py                   # Configuration dataclasses
├── constants.py                # Physical constants
│
├── solar/                      # Solar radiation module
│   ├── __init__.py
│   ├── position.py            # NOAA solar position algorithm
│   ├── radiation_bras.py      # Bras solar radiation model
│   ├── radiation_bird.py      # Bird-Hulstrom model
│   ├── radiation_ryan.py      # Ryan-Stolzenbach model
│   ├── radiation_iqbal.py     # Iqbal model
│   └── corrections.py         # Cloud, shade, albedo corrections
│
├── atmospheric/                # Atmospheric radiation module
│   ├── __init__.py
│   ├── emissivity.py          # Emissivity models (all methods)
│   └── longwave.py            # Longwave radiation calculations
│
├── wind/                       # Wind function module
│   ├── __init__.py
│   ├── functions.py           # Wind function models (all methods)
│   └── adjustment.py          # Wind height adjustment
│
├── heat_flux/                  # Heat flux module
│   ├── __init__.py
│   └── calculator.py          # Heat flux calculations
│
└── utils/                      # Utilities module
    ├── __init__.py
    ├── atmospheric.py         # Atmospheric helper functions
    ├── conversions.py         # Unit conversions
    └── validation.py          # Input validation

tests/
├── unit/                       # Unit tests
│   ├── test_solar_position.py
│   ├── test_solar_radiation.py
│   ├── test_atmospheric.py
│   ├── test_emissivity.py
│   ├── test_wind_functions.py
│   ├── test_wind_adjustment.py
│   ├── test_heat_flux.py
│   ├── test_conversions.py
│   └── test_validation.py
│
├── property/                   # Property-based tests
│   ├── test_properties_solar.py
│   ├── test_properties_atmospheric.py
│   ├── test_properties_wind.py
│   ├── test_properties_heat_flux.py
│   ├── test_properties_conversions.py
│   ├── test_properties_validation.py
│   └── test_properties_model.py
│
├── integration/                # Integration tests
│   ├── test_model_integration.py
│   └── test_vba_comparison.py
│
└── fixtures/                   # Test data and fixtures
    └── ...
```

### Module Responsibilities

**model.py**: Main orchestration
- RTempModel class
- Timestep iteration
- State management
- Method selection and instantiation

**config.py**: Configuration and data structures
- ModelConfiguration dataclass
- ModelState dataclass
- HeatFluxComponents dataclass
- SolarPositionResult dataclass
- DiagnosticOutput dataclass

**constants.py**: Physical constants
- Stefan-Boltzmann constant
- Water properties
- Sediment properties
- Conversion factors

**solar/**: Solar calculations
- Solar position (NOAA algorithm)
- Solar radiation models
- Corrections (cloud, shade, albedo)

**atmospheric/**: Longwave radiation
- Emissivity models
- Longwave radiation calculations
- Cloud corrections

**wind/**: Wind functions
- Wind function models
- Height adjustment

**heat_flux/**: Heat flux calculations
- Evaporation
- Convection
- Sediment conduction
- Hyporheic exchange
- Groundwater flux

**utils/**: Utilities
- Atmospheric helpers (vapor pressure, etc.)
- Unit conversions
- Input validation

---

## Development Workflow

### Branch Strategy

- `main`: Stable release branch
- `develop`: Development branch
- `feature/*`: Feature branches
- `bugfix/*`: Bug fix branches
- `release/*`: Release preparation branches

### Typical Workflow

1. **Create feature branch:**
```bash
git checkout develop
git pull origin develop
git checkout -b feature/my-new-feature
```

2. **Make changes:**
```bash
# Edit code
# Add tests
# Update documentation
```

3. **Run tests and checks:**
```bash
# Format code
black rtemp tests
isort rtemp tests

# Type checking
mypy rtemp

# Linting
flake8 rtemp tests

# Run tests
pytest

# Run with coverage
pytest --cov=rtemp --cov-report=html
```

4. **Commit changes:**
```bash
git add .
git commit -m "Add feature: description"
```

5. **Push and create pull request:**
```bash
git push origin feature/my-new-feature
# Create PR on GitHub
```

### Commit Message Guidelines

Follow conventional commits format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(solar): Add new solar radiation method

Implement Iqbal solar radiation model with atmospheric
transmittance calculations.

Closes #123
```

```
fix(validation): Handle negative wind speeds correctly

Previously negative wind speeds caused errors. Now they
are set to zero with a warning.

Fixes #456
```

---

## Testing

### Test Organization

**Unit Tests** (`tests/unit/`):
- Test individual functions and classes
- Mock external dependencies
- Fast execution
- High coverage

**Property-Based Tests** (`tests/property/`):
- Test universal properties using Hypothesis
- Generate random inputs
- Find edge cases
- Validate correctness properties

**Integration Tests** (`tests/integration/`):
- Test complete model execution
- Test method combinations
- Compare to VBA implementation
- Validate realistic scenarios

### Writing Unit Tests

Example unit test:

```python
# tests/unit/test_conversions.py
import pytest
from rtemp.utils import UnitConversions

def test_watts_to_cal_conversion():
    """Test conversion from W/m² to cal/cm²/day."""
    watts = 100.0
    cal = UnitConversions.watts_m2_to_cal_cm2_day(watts)
    
    # Expected value
    expected = 100.0 / (4.183076 * 10000 / 86400)
    
    assert abs(cal - expected) < 1e-6

def test_conversion_round_trip():
    """Test that forward and backward conversion recovers original value."""
    original = 500.0
    cal = UnitConversions.watts_m2_to_cal_cm2_day(original)
    watts = UnitConversions.cal_cm2_day_to_watts_m2(cal)
    
    assert abs(watts - original) < 1e-6

def test_negative_values():
    """Test that negative values are handled correctly."""
    watts = -100.0
    cal = UnitConversions.watts_m2_to_cal_cm2_day(watts)
    
    assert cal < 0
```

### Writing Property-Based Tests

Example property test:

```python
# tests/property/test_properties_conversions.py
import pytest
from hypothesis import given, strategies as st
from rtemp.utils import UnitConversions

# Feature: rtemp-python-complete, Property 14: Unit Conversion Round Trip
# Validates: Requirements 7.1-7.8
@given(st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False))
def test_unit_conversion_round_trip(value):
    """
    Property: For any numeric value, converting forward and backward
    should recover the original value within numerical precision.
    """
    # Convert forward and backward
    cal = UnitConversions.watts_m2_to_cal_cm2_day(value)
    recovered = UnitConversions.cal_cm2_day_to_watts_m2(cal)
    
    # Should recover original value
    assert abs(recovered - value) < 1e-6 * abs(value) if value != 0 else abs(recovered) < 1e-6
```

**Property Test Guidelines:**

1. **Tag with comment:**
```python
# Feature: rtemp-python-complete, Property X: [description]
# Validates: Requirements Y.Z
```

2. **Use appropriate strategies:**
```python
# Floats with constraints
st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False)

# Integers
st.integers(min_value=1, max_value=365)

# Datetimes
st.datetimes(min_value=datetime(2000, 1, 1), max_value=datetime(2030, 12, 31))

# Custom strategies
@st.composite
def valid_config(draw):
    return ModelConfiguration(
        latitude=draw(st.floats(min_value=-89, max_value=89)),
        longitude=draw(st.floats(min_value=-180, max_value=180)),
        # ... other parameters
    )
```

3. **Configure iterations:**
```python
from hypothesis import settings

@settings(max_examples=100)  # Run 100 iterations
@given(...)
def test_property(...):
    ...
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_conversions.py

# Run specific test
pytest tests/unit/test_conversions.py::test_watts_to_cal_conversion

# Run with coverage
pytest --cov=rtemp --cov-report=html

# Run only unit tests
pytest tests/unit -m unit

# Run only property tests
pytest tests/property -m property

# Run with verbose output
pytest -v

# Run with print statements
pytest -s

# Stop on first failure
pytest -x

# Run failed tests from last run
pytest --lf
```

### Test Coverage

Aim for:
- Overall coverage: > 90%
- Critical modules: > 95%
- Utility functions: 100%

Check coverage:
```bash
pytest --cov=rtemp --cov-report=term-missing
```

View HTML report:
```bash
pytest --cov=rtemp --cov-report=html
open htmlcov/index.html  # macOS
start htmlcov/index.html  # Windows
```

---

## Validation

### Overview

The Python implementation has been rigorously validated against the original VBA rTemp model to ensure accuracy and reliability. This section describes the validation methodology, results, and how to run validation tests.

### Validation Methodology

**Test Dataset:**
- **Period**: October-December 2003 (3 months)
- **Timesteps**: 8,828 (15-minute intervals)
- **Location**: Washington State (48.45°N, 122.33°W)
- **Data Source**: Original VBA model input/output files

**Comparison Approach:**
1. Run Python model with identical inputs as VBA
2. Compare all output variables timestep-by-timestep
3. Calculate RMSE, mean difference, and maximum difference
4. Analyze patterns and edge cases

### Validation Results

**Water Temperature:**
```python
RMSE = 0.13°C              # Excellent
Mean Difference = 0.096°C   # < 2% error
Max Difference = 0.39°C     # Acceptable (1 day out of 92)
```

**Heat Flux Components:**
```python
Solar Radiation RMSE = 6.82 W/m²       # 2.4% error
Longwave Atmospheric RMSE = 0.13 W/m²  # 0.07% error
Longwave Back RMSE = 0.60 W/m²         # 0.59% error
Convection RMSE = 0.64 W/m²
Evaporation RMSE = 0.71 W/m²
Sediment Conduction RMSE = 5.44 W/m²
```

**Solar Position:**
```python
Elevation Difference = 0.02-0.09°  # Excellent
NOAA Algorithm = Verified Correct
```

### Running Validation Tests

**24-Hour Validation:**
```bash
python tests/validation/validate_24hr.py
```

This runs a detailed 24-hour comparison for October 1, 2003, showing:
- Timestep-by-timestep comparison
- Heat flux components
- Temperature evolution
- Summary statistics

**Long-Term Validation:**
```bash
python tests/validation/long_term_validation.py
```

This runs the full 3-month validation, generating:
- `long_term_python_output.csv` - Python model results
- Summary statistics for all variables
- Comparison with VBA output

**Solar Position Diagnostic:**
```bash
python tests/validation/diagnose_solar_position_dec3.py
```

This provides detailed solar position calculations for December 3, 2003, showing:
- Step-by-step NOAA algorithm calculations
- Comparison with VBA at key times
- Timezone/DST analysis

### Key Findings

**1. Bras Solar Radiation Formula Corrections**

Three bugs were found and fixed in the Bras formula:

```python
# Bug 1: Extraterrestrial radiation
# WRONG: I0 = SOLAR_CONSTANT / distance²
# CORRECT: I0 = (SOLAR_CONSTANT / distance²) * sin(elevation)

# Bug 2: Molecular scattering coefficient
# WRONG: a1 = 0.128 (constant)
# CORRECT: a1 = 0.128 - 0.054 * log10(air_mass)

# Bug 3: Clear sky radiation
# WRONG: I = I0 * cos(zenith) * exp(...)
# CORRECT: I = I0 * exp(...)  # I0 already includes sin(elevation)
```

**2. Measured Solar Radiation Support**

VBA uses measured solar radiation when available. Python now does too:

```python
# Check for measured data
if 'solar_radiation' in met_row and not pd.isna(met_row['solar_radiation']):
    solar = met_row['solar_radiation']  # Use measured
else:
    solar = calculate_solar_radiation(...)  # Calculate
```

**3. Cloud Correction Application**

Cloud corrections must be applied to both measured and calculated solar radiation:

```python
# Apply cloud correction
solar_cal = SolarRadiationCorrections.apply_cloud_correction(
    solar_cal, cloud_cover, kcl1, kcl2
)
```

### Validation Test Files

**Location**: `tests/validation/`

**Key Files:**
- `validate_24hr.py` - 24-hour detailed validation
- `long_term_validation.py` - 3-month validation
- `diagnose_solar_position_dec3.py` - Solar position diagnostic
- `vba_validation.py` - Original validation script
- `investigate_solar_radiation.py` - Solar radiation investigation

**Fixture Files:**
- `tests/fixtures/vba_ts_input.csv` - VBA input time series
- `tests/fixtures/vba_ts_output.csv` - VBA output time series
- `tests/fixtures/vba_params.csv` - VBA parameters

### Adding New Validation Tests

When adding new features, create validation tests:

```python
# tests/validation/validate_new_feature.py
import pandas as pd
from rtemp import RTempModel, ModelConfiguration

def validate_new_feature():
    """Validate new feature against VBA or known results."""
    
    # Load reference data
    vba_output = pd.read_csv('tests/fixtures/vba_output.csv')
    
    # Run Python model
    config = ModelConfiguration(...)
    model = RTempModel(config)
    results = model.run(met_data)
    
    # Compare results
    diff = results['new_variable'] - vba_output['new_variable']
    rmse = (diff**2).mean()**0.5
    
    print(f"RMSE: {rmse:.4f}")
    assert rmse < threshold, f"RMSE {rmse} exceeds threshold {threshold}"
```

### Continuous Validation

**Pre-commit Checks:**
```bash
# Run before committing
pytest tests/validation/ -v
```

**CI/CD Integration:**
```yaml
# .github/workflows/validation.yml
- name: Run Validation Tests
  run: |
    pytest tests/validation/ -v
    python tests/validation/validate_24hr.py
```

### Known Limitations

1. **Maximum Temperature Difference**: 0.39°C on December 3, 2003
   - Caused by accumulated small differences throughout the day
   - Solar position algorithm is accurate (0.02-0.06° difference)
   - Acceptable for most applications

2. **Edge Cases**: Small differences near sunrise/sunset
   - When sun elevation < 2°
   - Affects < 0.1% of timesteps
   - Does not significantly impact overall accuracy

3. **Long-Term Accumulation**: Small errors can accumulate
   - Over periods > 3 months
   - Recommend periodic reinitialization for very long simulations

### Validation Documentation

**Summary Documents:**
- [Solar Radiation Fix Summary](../docs/validation/SOLAR_RADIATION_FIX_SUMMARY.md) - Solar radiation validation
- [User Guide - Validation Results](USER_GUIDE.md#validation-results) - User-friendly summary
- [API Reference - Validation](API_REFERENCE.md#validation-and-accuracy) - API-level details

**Detailed Results:**
- [Validation Documentation](../docs/validation/) - All validation documents
- `../tests/validation/LONG_TERM_VALIDATION_SUMMARY.md` - Long-term results
- `../tests/validation/AZIMUTH_ISSUE_ANALYSIS.md` - Solar position analysis

### Validation Checklist

When making changes that affect calculations:

- [ ] Run all unit tests: `pytest tests/unit/`
- [ ] Run property tests: `pytest tests/property/`
- [ ] Run 24-hour validation: `python tests/validation/validate_24hr.py`
- [ ] Run long-term validation: `python tests/validation/long_term_validation.py`
- [ ] Check RMSE values are within acceptable limits
- [ ] Document any changes in validation results
- [ ] Update validation documentation if needed

---

## Code Style

### Python Style Guide

Follow PEP 8 with these tools:

**Black** (code formatting):
```bash
black rtemp tests
```

**isort** (import sorting):
```bash
isort rtemp tests
```

**flake8** (linting):
```bash
flake8 rtemp tests
```

**mypy** (type checking):
```bash
mypy rtemp
```

### Type Hints

All functions must have type hints:

```python
from typing import Tuple, Optional, Dict, Any
import pandas as pd

def calculate_solar_position(
    lat: float,
    lon: float,
    dt: datetime,
    timezone: float,
    dlstime: int
) -> Tuple[float, float, float]:
    """
    Calculate solar position.
    
    Args:
        lat: Latitude in decimal degrees
        lon: Longitude in decimal degrees
        dt: Datetime object
        timezone: Hours from UTC
        dlstime: Daylight savings offset
        
    Returns:
        Tuple of (azimuth, elevation, distance)
    """
    # Implementation
    return azimuth, elevation, distance
```

### Docstring Style

Use Google-style docstrings:

```python
def calculate_heat_flux(
    solar: float,
    longwave: float,
    evap: float,
    conv: float
) -> float:
    """
    Calculate net heat flux.
    
    Sums all heat flux components to determine net energy exchange
    with the water body.
    
    Args:
        solar: Solar radiation in W/m²
        longwave: Net longwave radiation in W/m²
        evap: Evaporation flux in W/m² (negative for cooling)
        conv: Convection flux in W/m² (negative for cooling)
        
    Returns:
        Net heat flux in W/m² (positive = warming)
        
    Raises:
        ValueError: If any flux is NaN or infinite
        
    Example:
        >>> calculate_heat_flux(500, 50, -100, -50)
        400.0
    """
    # Implementation
    return solar + longwave + evap + conv
```

### Code Organization

**Function length**: Keep functions < 50 lines
**Class length**: Keep classes < 300 lines
**Module length**: Keep modules < 500 lines

**Function complexity**: Aim for cyclomatic complexity < 10

**Naming conventions:**
- Classes: `PascalCase`
- Functions: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Private methods: `_leading_underscore`

---

## Adding New Features

### Adding a New Solar Radiation Method

1. **Create new module:**
```python
# rtemp/solar/radiation_mynewmethod.py
from typing import Dict

class SolarRadiationMyNewMethod:
    """
    My new solar radiation method.
    
    Description of the method, references, etc.
    """
    
    @staticmethod
    def calculate(
        elevation: float,
        earth_sun_distance: float,
        # ... other parameters
    ) -> float:
        """
        Calculate solar radiation.
        
        Args:
            elevation: Solar elevation in degrees
            earth_sun_distance: Earth-Sun distance in AU
            
        Returns:
            Solar radiation in W/m²
        """
        # Implementation
        if elevation <= 0:
            return 0.0
            
        # ... calculations
        
        return radiation
```

2. **Add to __init__.py:**
```python
# rtemp/solar/__init__.py
from .radiation_mynewmethod import SolarRadiationMyNewMethod

__all__ = [
    # ... existing exports
    'SolarRadiationMyNewMethod',
]
```

3. **Update model.py:**
```python
# In RTempModel._calculate_solar_radiation()
elif self.config.solar_method == "MyNewMethod":
    from rtemp.solar import SolarRadiationMyNewMethod
    radiation = SolarRadiationMyNewMethod.calculate(
        elevation=solar_elevation,
        earth_sun_distance=earth_sun_distance,
        # ... parameters
    )
```

4. **Add tests:**
```python
# tests/unit/test_solar_radiation.py
def test_mynewmethod_basic():
    """Test MyNewMethod with basic inputs."""
    radiation = SolarRadiationMyNewMethod.calculate(
        elevation=45.0,
        earth_sun_distance=1.0
    )
    assert radiation > 0
    assert radiation < 1500  # Reasonable upper bound

def test_mynewmethod_zero_at_night():
    """Test that radiation is zero when sun is below horizon."""
    radiation = SolarRadiationMyNewMethod.calculate(
        elevation=-10.0,
        earth_sun_distance=1.0
    )
    assert radiation == 0.0
```

5. **Add property test:**
```python
# tests/property/test_properties_solar.py
@given(
    elevation=st.floats(min_value=-90, max_value=90),
    distance=st.floats(min_value=0.98, max_value=1.02)
)
def test_mynewmethod_non_negative(elevation, distance):
    """Property: Solar radiation should always be non-negative."""
    radiation = SolarRadiationMyNewMethod.calculate(
        elevation=elevation,
        earth_sun_distance=distance
    )
    assert radiation >= 0
```

6. **Update documentation:**
- Add to `docs/API_REFERENCE.md`
- Add to `docs/METHOD_SELECTION_GUIDE.md`
- Add to `docs/CONFIGURATION_GUIDE.md`

### Adding a New Configuration Parameter

1. **Update config.py:**
```python
@dataclass
class ModelConfiguration:
    # ... existing parameters
    
    my_new_parameter: float = 1.0  # Add with default value
```

2. **Update validation:**
```python
# In InputValidator.validate_site_parameters()
if params.get('my_new_parameter', 1.0) < 0:
    raise ValueError("my_new_parameter must be non-negative")
```

3. **Use in model:**
```python
# In RTempModel or relevant module
value = self.config.my_new_parameter
# ... use value
```

4. **Add tests:**
```python
def test_new_parameter_validation():
    """Test that invalid parameter is rejected."""
    with pytest.raises(ValueError):
        config = ModelConfiguration(
            # ... required parameters
            my_new_parameter=-1.0  # Invalid
        )
```

5. **Update documentation:**
- Add to `docs/CONFIGURATION_GUIDE.md`
- Add to `docs/API_REFERENCE.md`

---

## Performance Optimization

### Profiling

**Profile execution time:**
```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Run model
results = model.run(met_data)

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)  # Top 20 functions
```

**Profile memory usage:**
```python
from memory_profiler import profile

@profile
def run_model():
    model = RTempModel(config)
    results = model.run(met_data)
    return results

run_model()
```

### Optimization Strategies

1. **Vectorize operations:**
```python
# Bad: Loop over array
for i in range(len(temps)):
    result[i] = temps[i] + 273.15

# Good: Vectorized
result = temps + 273.15
```

2. **Avoid repeated calculations:**
```python
# Bad: Calculate in loop
for i in range(n):
    value = expensive_calculation()
    result[i] = value * data[i]

# Good: Calculate once
value = expensive_calculation()
for i in range(n):
    result[i] = value * data[i]
```

3. **Use appropriate data structures:**
```python
# Bad: List for lookups
methods = ['Bras', 'Bird', 'Ryan-Stolzenbach']
if method in methods:  # O(n)
    ...

# Good: Set for lookups
methods = {'Bras', 'Bird', 'Ryan-Stolzenbach'}
if method in methods:  # O(1)
    ...
```

4. **Cache expensive calculations:**
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_calculation(param):
    # ... expensive operation
    return result
```

---

## Documentation

### Code Documentation

**Module docstrings:**
```python
"""
Solar radiation calculation module.

This module provides multiple methods for calculating solar radiation
reaching the water surface, including Bras, Bird-Hulstrom, Ryan-Stolzenbach,
and Iqbal methods.

Example:
    >>> from rtemp.solar import SolarRadiationBras
    >>> radiation = SolarRadiationBras.calculate(elevation=45.0, ...)
"""
```

**Class docstrings:**
```python
class SolarRadiationBras:
    """
    Bras atmospheric attenuation solar radiation model.
    
    Implements the Bras (1990) method for calculating clear-sky solar
    radiation based on optical air mass and atmospheric turbidity.
    
    References:
        Bras, R.L. (1990). Hydrology: An Introduction to Hydrologic Science.
        Addison-Wesley.
    
    Attributes:
        None (all methods are static)
    """
```

**Function docstrings:**
```python
def calculate(elevation: float, earth_sun_distance: float, turbidity: float) -> float:
    """
    Calculate solar radiation using Bras method.
    
    Args:
        elevation: Solar elevation angle in degrees above horizon
        earth_sun_distance: Earth-Sun distance in astronomical units
        turbidity: Atmospheric turbidity factor (typically 2-5)
        
    Returns:
        Solar radiation in W/m²
        
    Raises:
        ValueError: If elevation is not in range [-90, 90]
        
    Example:
        >>> SolarRadiationBras.calculate(45.0, 1.0, 2.0)
        850.5
        
    Note:
        Returns 0 if elevation <= 0 (sun below horizon)
    """
```

### User Documentation

Update these files when adding features:
- `docs/API_REFERENCE.md`: API documentation
- `docs/USER_GUIDE.md`: User guide and examples
- `docs/CONFIGURATION_GUIDE.md`: Configuration parameters
- `docs/METHOD_SELECTION_GUIDE.md`: Method selection guidance
- `docs/TROUBLESHOOTING.md`: Common issues and solutions
- `README.md`: Overview and quick start

---

## Release Process

### Version Numbering

Follow Semantic Versioning (semver):
- MAJOR.MINOR.PATCH (e.g., 1.2.3)
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes (backward compatible)

### Release Checklist

1. **Update version:**
```python
# pyproject.toml
[project]
version = "1.2.3"
```

2. **Update CHANGELOG.md:**
```markdown
## [1.2.3] - 2024-06-15

### Added
- New Iqbal solar radiation method
- Time-varying water depth support

### Fixed
- Bug in wind height adjustment
- Validation error for negative values

### Changed
- Improved performance of solar calculations
```

3. **Run full test suite:**
```bash
pytest
pytest --cov=rtemp --cov-report=term-missing
mypy rtemp
flake8 rtemp tests
black --check rtemp tests
```

4. **Build documentation:**
```bash
# If using Sphinx or similar
cd docs
make html
```

5. **Create release branch:**
```bash
git checkout develop
git checkout -b release/1.2.3
```

6. **Commit version changes:**
```bash
git add pyproject.toml CHANGELOG.md
git commit -m "Bump version to 1.2.3"
```

7. **Merge to main:**
```bash
git checkout main
git merge release/1.2.3
git tag -a v1.2.3 -m "Release version 1.2.3"
git push origin main --tags
```

8. **Merge back to develop:**
```bash
git checkout develop
git merge release/1.2.3
git push origin develop
```

9. **Build and publish:**
```bash
python -m build
python -m twine upload dist/*
```

---

## Contributing Guidelines

### Pull Request Process

1. **Create feature branch** from `develop`
2. **Make changes** with tests and documentation
3. **Run all checks** (tests, linting, type checking)
4. **Update documentation** as needed
5. **Create pull request** with clear description
6. **Address review comments**
7. **Squash and merge** when approved

### Code Review Checklist

**Functionality:**
- [ ] Code works as intended
- [ ] Edge cases are handled
- [ ] Error handling is appropriate

**Tests:**
- [ ] Unit tests added/updated
- [ ] Property tests added if applicable
- [ ] All tests pass
- [ ] Coverage is maintained/improved

**Code Quality:**
- [ ] Follows style guide
- [ ] Type hints are present
- [ ] Docstrings are complete
- [ ] No unnecessary complexity

**Documentation:**
- [ ] API documentation updated
- [ ] User guide updated if needed
- [ ] Examples added if applicable
- [ ] CHANGELOG.md updated

### Getting Help

- **Questions**: Open a GitHub Discussion
- **Bugs**: Open a GitHub Issue
- **Features**: Open a GitHub Issue with proposal
- **Security**: Email maintainers directly

---

## Additional Resources

### References

**Solar Position:**
- Reda, I., & Andreas, A. (2004). Solar position algorithm for solar radiation applications. Solar Energy, 76(5), 577-589.

**Solar Radiation:**
- Bras, R.L. (1990). Hydrology: An Introduction to Hydrologic Science. Addison-Wesley.
- Bird, R.E., & Hulstrom, R.L. (1981). A Simplified Clear Sky Model for Direct and Diffuse Insolation on Horizontal Surfaces. SERI Technical Report.
- Iqbal, M. (1983). An Introduction to Solar Radiation. Academic Press.

**Longwave Radiation:**
- Brunt, D. (1932). Notes on radiation in the atmosphere. Quarterly Journal of the Royal Meteorological Society, 58(247), 389-420.
- Brutsaert, W. (1975). On a derivable formula for long-wave radiation from clear skies. Water Resources Research, 11(5), 742-744.

**Wind Functions:**
- Brady, D.K., Graves, W.L., & Geyer, J.C. (1969). Surface heat exchange at power plant cooling lakes. Report No. 5, Cooling Water Studies for Edison Electric Institute.

### Tools

- **pytest**: https://pytest.org
- **hypothesis**: https://hypothesis.readthedocs.io
- **black**: https://black.readthedocs.io
- **mypy**: https://mypy.readthedocs.io
- **flake8**: https://flake8.pycqa.org

### Community

- **GitHub**: <repository-url>
- **Issues**: <repository-url>/issues
- **Discussions**: <repository-url>/discussions

