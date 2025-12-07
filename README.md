# rTemp: Response Temperature Model for Water Bodies

A Python implementation of the rTemp water temperature model, which calculates response temperature of water bodies based on meteorological inputs and site characteristics using a heat budget approach.

## About Response Temperature

**Original Concept by:** Greg Pelletier, Washington State Department of Ecology, Olympia, WA  
**Based on work by:** J.E. Edinger Associates (www.jeeai.com)  
**Original rTemp Model:** [Models & Tools for TMDLs - Washington State Department of Ecology](https://ecology.wa.gov/research-data/data-resources/models-spreadsheets/modeling-the-environment/models-tools-for-tmdls)

Response temperature is defined as the temperature that a column of fully mixed water would have if heat fluxes across the surface were the only heat transfer processes. In other words, the water temperature is assumed to be responding only to those heat fluxes.

The rate of surface heat exchange can be calculated from meteorological data (e.g., air and dew point temperature, wind speed, cloud cover, solar radiation). Because meteorological data are available for very long periods, this simple model provides the basis to estimate long-term, frequency of occurrence statistics for natural water temperatures.

The Washington State Department of Ecology has extended this concept to also include the response to heat flux between the water and the stream bed, groundwater inflow, and hyporheic exchange.

### Governing Equation

The rate of change of response temperature is calculated from the net rate of surface heat exchange:

```
dT/dt = Jnet / (D × ρw × Cpw)
```

Where:
- `dT/dt` = rate of change of water temperature with time (°C/sec)
- `D` = mean depth of the water column (cm)
- `Jnet` = net rate of heat exchange (cal/cm²/sec)
- `ρw` = density of water (g/cm³)
- `Cpw` = specific heat of water at constant pressure (cal/g/°C)

The net heat flux includes:
- Solar shortwave radiation
- Longwave atmospheric radiation
- Longwave back radiation
- Convection
- Evaporation
- Streambed conduction
- Hyporheic exchange
- Groundwater inflow

A similar expression is used for the change in temperature of the surface layer of the bottom sediment underlying the stream bed in response to heat flux from hyporheic exchange and conduction between the water and sediment.

## Overview

## Features

- **Multiple Calculation Methods**: Choose from various solar radiation, longwave radiation, and wind function models
- **Heat Budget**: Accounts for major energy exchange processes
- **Configuration**: Parameter customization for different water bodies
- **Input Validation**: Input validation with warnings and error messages
- **Diagnostic Output**: Optional detailed output for debugging and analysis
- **Test Coverage**: Unit tests and property-based tests (346 tests passing)
- **VBA Comparison**: Validated against original VBA implementation (0.13°C water temperature RMSE)

## Installation

### From Source

Clone the repository and install in development mode with dev dependencies:

```bash
git clone <repository-url>
cd rtemp
pip install -e ".[dev]"
```

### Dependencies

**Core Dependencies:**
- numpy >= 1.20.0
- pandas >= 1.3.0
- python-dateutil >= 2.8.0

**Development Dependencies:**
- pytest >= 7.0.0
- hypothesis >= 6.0.0
- pytest-cov >= 3.0.0
- black >= 22.0.0
- mypy >= 0.950
- flake8 >= 4.0.0

## Quick Start

```python
from rtemp import RTempModel, ModelConfiguration
import pandas as pd

# Create model configuration
config = ModelConfiguration(
    latitude=47.5,
    longitude=-122.0,
    elevation=100.0,
    timezone=8.0,
    initial_water_temp=15.0,
    water_depth=2.0,
    solar_method="Bras",
    longwave_method="Brunt",
    wind_function_method="Brady-Graves-Geyer"
)

# Load meteorological data
met_data = pd.read_csv("meteorological_data.csv")

# Run model
model = RTempModel(config)
results = model.run(met_data)

# Export results
results.to_csv("water_temperature_results.csv")
```

## Examples

### GoldSim Integration

A complete example of integrating rTemp into GoldSim using the GSPy Python bridge is available in `examples/goldsim_integration/`. This example demonstrates:

- Stateless physics engine pattern
- Daily to hourly temporal disaggregation
- State management via GoldSim Previous Value elements
- Automatic dewpoint estimation from air temperature
- Complete setup and configuration instructions

See [examples/goldsim_integration/README.md](examples/goldsim_integration/README.md) for details.

## Development

### Running Tests

Run all tests:

```bash
pytest
```

Run unit tests only:

```bash
pytest tests/unit
```

Run property-based tests only:

```bash
pytest tests/property -m property
```

Run with coverage:

```bash
pytest --cov=rtemp --cov-report=html
```

### Code Quality

Format code with black:

```bash
black rtemp tests
```

Sort imports:

```bash
isort rtemp tests
```

Type checking with mypy:

```bash
mypy rtemp
```

Linting with flake8:

```bash
flake8 rtemp tests
```

## Project Structure

```
rtemp/
├── rtemp/                      # Main package
│   ├── __init__.py
│   ├── model.py               # Main RTempModel class
│   ├── config.py              # Configuration and data models
│   ├── constants.py           # Physical constants
│   ├── solar/                 # Solar position and radiation
│   ├── atmospheric/           # Longwave radiation
│   ├── wind/                  # Wind functions
│   ├── heat_flux/            # Heat flux calculations
│   └── utils/                # Utilities and validation
├── tests/                     # Test suite
│   ├── unit/                 # Unit tests
│   ├── property/             # Property-based tests
│   ├── integration/          # Integration tests
│   └── fixtures/             # Test data and fixtures
├── pyproject.toml            # Project configuration
└── README.md                 # This file
```

## Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[User Guide](docs/USER_GUIDE.md)**: Installation, quick start, and usage examples
- **[API Reference](docs/API_REFERENCE.md)**: Complete API documentation
- **[Configuration Guide](docs/CONFIGURATION_GUIDE.md)**: Detailed parameter descriptions
- **[Method Selection Guide](docs/METHOD_SELECTION_GUIDE.md)**: Choosing calculation methods
- **[Troubleshooting](docs/TROUBLESHOOTING.md)**: Common issues and solutions
- **[Developer Guide](docs/DEVELOPER_GUIDE.md)**: Contributing and development setup

### Quick Links

**Getting Started:**
1. [Installation](docs/USER_GUIDE.md#installation)
2. [Quick Start](docs/USER_GUIDE.md#quick-start)
3. [Input Data Preparation](docs/USER_GUIDE.md#input-data-preparation)

**Configuration:**
1. [Site Parameters](docs/CONFIGURATION_GUIDE.md#site-parameters)
2. [Method Selection](docs/METHOD_SELECTION_GUIDE.md)
3. [Advanced Usage](docs/USER_GUIDE.md#advanced-usage)

**Development:**
1. [Development Setup](docs/DEVELOPER_GUIDE.md#development-setup)
2. [Testing](docs/DEVELOPER_GUIDE.md#testing)
3. [Contributing](CONTRIBUTING.md)

**Validation:**
1. [Validation Results](docs/validation/COMPREHENSIVE_VALIDATION_RESULTS.md)
2. [Bug Fixes](docs/validation/BUG_FIXES_SUMMARY.md)
3. [Validation Summary](docs/validation/VBA_VALIDATION_RESULTS.md)

## Validation Results

The Python implementation has been validated against the original VBA rTemp model over a 3-month period (October-December 2003, 8,828 timesteps):

### Water Temperature Accuracy
- **RMSE**: 0.13°C
- **Mean Difference**: 0.096°C (< 2% error)
- **Maximum Difference**: 0.39°C (occurs on 1 day, 1% of period)

### Heat Flux Components
| Component | RMSE | Mean % Error |
|-----------|------|--------------|
| Solar Radiation | 6.82 W/m² | 2.4% |
| Longwave Atmospheric | 0.13 W/m² | 0.07% |
| Longwave Back | 0.60 W/m² | 0.59% |
| Convection | 0.64 W/m² | - |
| Evaporation | 0.71 W/m² | - |
| Sediment Conduction | 5.44 W/m² | - |

### Solar Position Accuracy
- **Elevation Difference**: 0.02-0.09°
- **NOAA Algorithm**: Verified correct implementation

### Test Coverage
- **Total Tests**: 346 passing
- **Unit Tests**: Coverage of all components
- **Property Tests**: Hypothesis-based testing for edge cases
- **Integration Tests**: Full model validation scenarios
- **Validation Tests**: Comparison with VBA reference implementation

### Key Improvements from Original VBA
1. **Measured Solar Radiation Support**: Uses measured data when available
2. **Numerical Stability**: Better handling of edge cases
3. **Input Checking**: Input validation with warnings

See [docs/validation/](docs/validation/) for detailed validation methodology and results.

## License

MIT License

## Contributing

Contributions are welcome! Please see CONTRIBUTING.md for guidelines.

## References

This implementation is based on the original VBA rTemp model by Greg Pelletier, Washington State Department of Ecology, and incorporates algorithms from:

### Primary Reference
- **Edinger, J.E., Brady, D.K. and Geyer, J.C.** (1974). *Heat exchange and transport in the environment*. EPRI publication no. 74-049-00-3, Electric Power Research Institute, Palo Alto, CA.

### Solar Position and Radiation
- **NOAA Solar Position Algorithm** (Reda & Andreas, 2004)
- **Bras, R.L.** (1990). *Hydrology: An Introduction to Hydrologic Science*. Addison-Wesley.
- **Bird, R.E. and Hulstrom, R.L.** (1981). *A Simplified Clear Sky Model for Direct and Diffuse Insolation on Horizontal Surfaces*. SERI/TR-642-761.
- **Ryan, P.J. and Stolzenbach, K.D.** (1972). *Engineering Aspects of Heat Disposal from Power Generation*. MIT.
- **Iqbal, M.** (1983). *An Introduction to Solar Radiation*. Academic Press.

### Longwave Radiation
- **Brunt, D.** (1932). Notes on radiation in the atmosphere. *Quarterly Journal of the Royal Meteorological Society*, 58(247), 389-420.
- **Brutsaert, W.** (1975). On a derivable formula for long-wave radiation from clear skies. *Water Resources Research*, 11(5), 742-744.
- **Swinbank, W.C.** (1963). Long-wave radiation from clear skies. *Quarterly Journal of the Royal Meteorological Society*, 89(381), 339-348.

### Wind Functions
- **Brady, D.K., Graves, W.L., and Geyer, J.C.** (1969). Surface heat exchange at power plant cooling lakes. Report No. 5, Cooling Water Studies for Edison Electric Institute.
- **Ryan, P.J. and Harleman, D.R.F.** (1973). An analytical and experimental study of transient cooling pond behavior. Report No. 161, Ralph M. Parsons Laboratory, MIT.

## Contact

For questions and support, please open an issue on the GitHub repository.
