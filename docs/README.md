# rTemp Documentation

Welcome to the rTemp water temperature model documentation!

## Documentation Overview

This documentation is organized into several guides to help you get started, configure the model, and understand its capabilities.

### For Users

**[User Guide](USER_GUIDE.md)** - Start here!
- Installation instructions
- Quick start tutorial
- Input data preparation
- Running the model
- Understanding output
- Advanced usage examples
- Best practices

**[Configuration Guide](CONFIGURATION_GUIDE.md)** - Detailed parameter reference
- Site parameters (latitude, longitude, elevation, etc.)
- Initial conditions
- Water body parameters
- Sediment parameters
- Groundwater parameters
- Method selections
- Model parameters
- Configuration examples

**[Method Selection Guide](METHOD_SELECTION_GUIDE.md)** - Choosing calculation methods
- Solar radiation methods (Bras, Bird, Ryan-Stolzenbach, Iqbal)
- Longwave radiation methods (Brunt, Brutsaert, Satterlund, etc.)
- Wind function methods (Brady-Graves-Geyer, Marciano-Harbeck, etc.)
- Decision trees for method selection
- Method comparison tables
- Recommendations by application type

**[API Reference](API_REFERENCE.md)** - Complete API documentation
- RTempModel class
- Configuration dataclasses
- Solar module
- Atmospheric module
- Wind module
- Heat flux module
- Utilities
- Constants

**[Troubleshooting](TROUBLESHOOTING.md)** - Common issues and solutions
- Installation issues
- Configuration errors
- Data issues
- Runtime errors
- Output issues
- Performance issues
- Accuracy issues
- Common error messages

### For Developers

**[Developer Guide](DEVELOPER_GUIDE.md)** - Contributing to rTemp
- Development setup
- Project architecture
- Code organization
- Development workflow
- Testing (unit, property-based, integration)
- Code style guidelines
- Adding new features
- Performance optimization
- Documentation standards
- Release process

**[Contributing Guidelines](../CONTRIBUTING.md)** - How to contribute
- Development setup
- Code quality standards
- Testing requirements
- Pull request process

## Quick Navigation

### Getting Started

1. **Install rTemp**: See [Installation](USER_GUIDE.md#installation)
2. **Run your first model**: See [Quick Start](USER_GUIDE.md#quick-start)
3. **Prepare your data**: See [Input Data Preparation](USER_GUIDE.md#input-data-preparation)

### Common Tasks

- **Configure the model**: [Configuration Guide](CONFIGURATION_GUIDE.md)
- **Choose calculation methods**: [Method Selection Guide](METHOD_SELECTION_GUIDE.md)
- **Understand output**: [Understanding Output](USER_GUIDE.md#understanding-output)
- **Troubleshoot issues**: [Troubleshooting](TROUBLESHOOTING.md)
- **View examples**: See `examples/` directory in repository

### Reference

- **API documentation**: [API Reference](API_REFERENCE.md)
- **All parameters**: [Configuration Guide](CONFIGURATION_GUIDE.md)
- **All methods**: [Method Selection Guide](METHOD_SELECTION_GUIDE.md)
- **Error messages**: [Common Error Messages](TROUBLESHOOTING.md#common-error-messages)

## Documentation by Topic

### Solar Radiation

- [Solar Radiation Methods](METHOD_SELECTION_GUIDE.md#solar-radiation-methods)
- [Solar Module API](API_REFERENCE.md#solar-module)
- [Solar Parameters](CONFIGURATION_GUIDE.md#model-parameters)
- [Solar Troubleshooting](TROUBLESHOOTING.md#accuracy-issues)

### Longwave Radiation

- [Longwave Radiation Methods](METHOD_SELECTION_GUIDE.md#longwave-radiation-methods)
- [Atmospheric Module API](API_REFERENCE.md#atmospheric-module)
- [Longwave Parameters](CONFIGURATION_GUIDE.md#model-parameters)

### Wind Functions

- [Wind Function Methods](METHOD_SELECTION_GUIDE.md#wind-function-methods)
- [Wind Module API](API_REFERENCE.md#wind-module)
- [Wind Parameters](CONFIGURATION_GUIDE.md#water-body-parameters)

### Heat Fluxes

- [Heat Flux Calculations](API_REFERENCE.md#heat-flux-module)
- [Understanding Heat Fluxes](USER_GUIDE.md#understanding-output)
- [Heat Flux Parameters](CONFIGURATION_GUIDE.md#sediment-parameters)

### Data Preparation

- [Input Data Format](USER_GUIDE.md#input-data-preparation)
- [Data Quality](USER_GUIDE.md#data-quality-considerations)
- [Data Issues](TROUBLESHOOTING.md#data-issues)

### Configuration

- [All Parameters](CONFIGURATION_GUIDE.md)
- [Configuration Examples](CONFIGURATION_GUIDE.md#configuration-examples)
- [Configuration Errors](TROUBLESHOOTING.md#configuration-errors)

### Testing

- [Running Tests](DEVELOPER_GUIDE.md#testing)
- [Writing Tests](DEVELOPER_GUIDE.md#writing-unit-tests)
- [Property-Based Testing](DEVELOPER_GUIDE.md#writing-property-based-tests)

## Examples

The `examples/` directory contains working code examples:

- `basic_usage.py`: Simple model run with default parameters
- `all_methods_demo.py`: Demonstration of all calculation methods
- `diagnostic_output_demo.py`: Using diagnostic output for debugging
- `time_varying_parameters_demo.py`: Time-varying depth and shade
- `solar_corrections_demo.py`: Solar radiation corrections

## Additional Resources

### Validation

The Python implementation has been rigorously validated against the original VBA rTemp model:

- **Water Temperature RMSE**: 0.13°C (excellent agreement)
- **Solar Radiation RMSE**: 6.82 W/m² (2.4% error)
- **Test Coverage**: 346 automated tests passing
- **Status**: Production-ready for water temperature modeling

See [User Guide - Validation Results](USER_GUIDE.md#validation-results) for detailed validation methodology and results.

### Scientific Background

The rTemp model is based on established scientific methods:

- **Solar Position**: NOAA algorithm (Reda & Andreas, 2004)
- **Solar Radiation**: Multiple models (Bras, Bird & Hulstrom, Ryan-Stolzenbach, Iqbal)
- **Longwave Radiation**: Various emissivity models (Brunt, Brutsaert, Satterlund, etc.)
- **Wind Functions**: Established relationships (Brady-Graves-Geyer, Marciano-Harbeck, etc.)

**Original Work**: Greg Pelletier, Washington State Department of Ecology  
**Concept**: J.E. Edinger Associates

### Related Projects

- Original VBA implementation by Greg Pelletier, Washington State Department of Ecology
- NOAA Solar Position Calculator: https://www.esrl.noaa.gov/gmd/grad/solcalc/

### Support

- **Questions**: Open a GitHub Discussion
- **Bug Reports**: Open a GitHub Issue
- **Feature Requests**: Open a GitHub Issue with proposal
- **Contributing**: See [Developer Guide](DEVELOPER_GUIDE.md)

## Documentation Feedback

Found an error in the documentation? Have a suggestion for improvement?

- Open an issue on GitHub
- Submit a pull request with corrections
- Start a discussion for major changes

## Version Information

This documentation is for rTemp version 1.0.0.

For older versions, see the documentation in the corresponding release tag.

---

## Document Index

### User Documentation

1. [User Guide](USER_GUIDE.md) - Complete user guide
2. [Configuration Guide](CONFIGURATION_GUIDE.md) - Parameter reference
3. [Method Selection Guide](METHOD_SELECTION_GUIDE.md) - Choosing methods
4. [API Reference](API_REFERENCE.md) - API documentation
5. [Troubleshooting](TROUBLESHOOTING.md) - Common issues

### Developer Documentation

1. [Developer Guide](DEVELOPER_GUIDE.md) - Development guide
2. [Contributing Guidelines](../CONTRIBUTING.md) - How to contribute

### Other Documentation

1. [README](../README.md) - Project overview
2. [License](../LICENSE) - MIT License
3. [Changelog](../CHANGELOG.md) - Version history (if exists)

---

**Last Updated**: December 2024  
**Version**: 1.0.0

