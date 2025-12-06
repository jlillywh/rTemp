# Changelog

All notable changes to the rTemp project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-12-06

### 🎉 Initial Production Release

First production-ready release of the Python rTemp water temperature model, validated against the original VBA implementation.

### Added

#### Core Features
- Complete Python implementation of rTemp water temperature model
- Multiple solar radiation calculation methods:
  - Bras atmospheric attenuation model
  - Bird-Hulstrom clear sky model
  - Ryan-Stolzenbach simplified model
  - Iqbal spectral model
- Multiple longwave radiation methods:
  - Brunt emissivity model
  - Brutsaert vapor pressure model
  - Swinbank temperature-based model
  - Satterlund, Koberg, Anderson methods
- Multiple wind function models:
  - Brady-Graves-Geyer (default)
  - Ryan-Harleman with stability
  - Marciano-Harbeck linear
  - East Mesa, Helfrich methods
- Comprehensive heat budget calculations:
  - Solar radiation (with cloud, shade, albedo corrections)
  - Longwave atmospheric and back radiation
  - Evaporation and convection
  - Sediment conduction
  - Hyporheic exchange
  - Groundwater inflow

#### Validation & Testing
- Comprehensive validation against VBA rTemp model
- 346 automated tests with 98% code coverage
- Water temperature RMSE: 0.13°C (3-month validation)
- Solar radiation RMSE: 6.82 W/m² (2.4% error)
- Solar position accuracy: 0.02-0.09° elevation difference
- Unit tests for all components
- Property-based tests using Hypothesis
- Integration tests for full model scenarios

#### Documentation
- Complete user guide with validation results
- Comprehensive API reference
- Developer guide with validation methodology
- Configuration guide for all parameters
- Method selection guide
- Troubleshooting guide
- Validation documentation in docs/validation/
- Working examples in examples/ directory

#### Features
- Measured solar radiation support (uses measured data when available)
- Time-varying parameters (depth, shade)
- Diagnostic output mode for debugging
- Input validation with informative warnings
- Stability criteria checking
- Minimum temperature enforcement
- NOAA solar position algorithm
- Anderson albedo calculation
- Cloud cover corrections

### Fixed

#### Critical Bug Fixes
- **Bras Solar Radiation Formula** (3 bugs corrected):
  1. Extraterrestrial radiation: Changed from `I0 * cos(zenith)` to `I0 * sin(elevation)`
  2. Molecular scattering: Changed from constant `0.128` to `0.128 - 0.054 * log10(air_mass)`
  3. Air mass formula: Updated to match VBA implementation
- **Measured Solar Radiation**: Added support for using measured data from input
- **Cloud Corrections**: Now applied to both measured and calculated solar radiation
- **Temperature Update**: Fixed heat capacity unit conversion (1000x error)
- **Longwave Back Radiation**: Fixed sign in net flux calculation

### Validation Results

#### Water Temperature
- RMSE: 0.13°C (3-month validation, 8,828 timesteps)
- Mean Difference: 0.096°C (< 2% error)
- Maximum Difference: 0.39°C (1 day out of 92)
- Status: ✅ Production-ready

#### Heat Flux Components
- Solar Radiation: 6.82 W/m² RMSE (2.4% error)
- Longwave Atmospheric: 0.13 W/m² RMSE (0.07% error)
- Longwave Back: 0.60 W/m² RMSE (0.59% error)
- Convection: 0.64 W/m² RMSE
- Evaporation: 0.71 W/m² RMSE
- Sediment Conduction: 5.44 W/m² RMSE

### Technical Details

#### Dependencies
- Python ≥ 3.8
- numpy ≥ 1.20.0
- pandas ≥ 1.3.0
- python-dateutil ≥ 2.8.0

#### Development Dependencies
- pytest ≥ 7.0.0
- hypothesis ≥ 6.0.0
- pytest-cov ≥ 3.0.0
- black ≥ 22.0.0
- mypy ≥ 0.950
- flake8 ≥ 4.0.0
- isort ≥ 5.10.0

### Credits

Based on the original VBA rTemp model by:
- **Greg Pelletier**, Washington State Department of Ecology
- Concept by **J.E. Edinger Associates**

Primary reference:
- **Edinger, J.E., Brady, D.K. and Geyer, J.C.** (1974). *Heat exchange and transport in the environment*. EPRI publication no. 74-049-00-3, Electric Power Research Institute, Palo Alto, CA.

### Notes

This release represents a complete, production-ready implementation of the rTemp water temperature model in Python. The implementation has been rigorously validated against the original VBA model and is suitable for:
- Research applications
- Regulatory compliance modeling
- Long-term statistical analysis
- Educational purposes

---

## Future Releases

Future releases will include:
- Additional solar radiation models
- Enhanced diagnostic capabilities
- Performance optimizations
- Additional validation datasets
- Extended documentation

---

**For detailed validation results, see:**
- `docs/validation/SOLAR_RADIATION_FIX_SUMMARY.md`
- `docs/validation/COMPREHENSIVE_VALIDATION_RESULTS.md`
- `docs/USER_GUIDE.md#validation-results`

**For migration from VBA, see:**
- `docs/USER_GUIDE.md#comparison-with-original-vba-model`
