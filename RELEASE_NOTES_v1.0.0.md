# rTemp v1.0.0 Release Notes 🎉

**Release Date:** December 6, 2024  
**Status:** Production/Stable  
**Python Version:** ≥ 3.8

## Overview

We're excited to announce the first production release of **rTemp** - a comprehensive Python implementation of the Response Temperature water temperature model!

## Highlights

### Validation and verification
- **346 tests passing** with 98% code coverage
- **0.13°C RMSE** against VBA over 3 months

### Physics
- Multiple solar radiation models (Bras, Bird, Ryan-Stolzenbach, Iqbal)
- Multiple longwave radiation models (Brunt, Brutsaert, Swinbank, etc.)
- Multiple wind function models (Brady-Graves-Geyer, Ryan-Harleman, etc.)
- Complete heat budget calculations

### Documentation
- Complete user guide with validation results
- Comprehensive API reference
- Developer guide with testing methodology
- Method selection guide
- Working examples

### Bug Fixes
- Fixed 3 bugs in Bras solar radiation formula
- Added measured solar radiation support
- Corrected temperature update calculations
- All validation issues resolved

## What's New

### Core Features

**Solar Radiation Methods:**
- Bras atmospheric attenuation model
- Bird-Hulstrom clear sky model
- Ryan-Stolzenbach simplified model
- Iqbal spectral model

**Longwave Radiation Methods:**
- Brunt, Brutsaert, Swinbank
- Satterlund, Koberg, Anderson
- Multiple cloud correction methods

**Wind Functions:**
- Brady-Graves-Geyer (default)
- Ryan-Harleman with stability effects
- Marciano-Harbeck, East Mesa, Helfrich

**Additional Features:**
- Measured solar radiation support
- Time-varying parameters
- Diagnostic output mode
- Comprehensive input validation
- Stability criteria checking

### Validation Results

**Water Temperature:**
```
RMSE: 0.13°C
Mean Difference: 0.096°C
Maximum Difference: 0.39°C
```

**Heat Flux Components:**
```
Solar Radiation:      6.82 W/m² RMSE (2.4% error)
Longwave Atmospheric: 0.13 W/m² RMSE (0.07% error)
Longwave Back:        0.60 W/m² RMSE (0.59% error)
Convection:           0.64 W/m² RMSE
Evaporation:          0.71 W/m² RMSE
```

**Solar Position:**
```
Elevation Accuracy: 0.02-0.09° (excellent)
NOAA Algorithm: Verified correct
```

## Installation

```bash
pip install rtemp
```

Or from source:
```bash
git clone https://github.com/yourusername/rtemp.git
cd rtemp
pip install -e .
```

## Quick Start

```python
from rtemp import RTempModel, ModelConfiguration
import pandas as pd

# Configure model
config = ModelConfiguration(
    latitude=47.5,
    longitude=-122.0,
    elevation=100.0,
    timezone=-8.0,
    initial_water_temp=15.0,
    water_depth=2.0
)

# Load meteorological data
met_data = pd.read_csv("met_data.csv")

# Run model
model = RTempModel(config)
results = model.run(met_data)

# Export results
results.to_csv("water_temperature.csv")
```

## Documentation

- **User Guide**: `docs/USER_GUIDE.md`
- **API Reference**: `docs/API_REFERENCE.md`
- **Developer Guide**: `docs/DEVELOPER_GUIDE.md`
- **Validation Results**: `docs/validation/`
- **Examples**: `examples/`

## Migration from VBA

If you're migrating from the VBA rTemp model:

1. **Compatible Parameters**: Most parameters have identical names
2. **Input Format**: CSV format similar to VBA
3. **Output Format**: Can export to CSV matching VBA structure
4. **Validation**: Excellent agreement (0.13°C RMSE)

See `docs/USER_GUIDE.md#comparison-with-original-vba-model` for details.

## Testing

Run the test suite:
```bash
pytest                          # All tests
pytest --cov=rtemp             # With coverage
pytest tests/unit              # Unit tests only
pytest tests/validation        # Validation tests
```

## Known Limitations

1. **Maximum Temperature Difference**: 0.39°C on 1 day (December 3, 2003)
   - Acceptable for most applications
   - Caused by accumulated small differences

2. **Edge Cases**: Small differences near sunrise/sunset
   - When sun elevation < 2°
   - Affects < 0.1% of timesteps

3. **Long-Term Accumulation**: Small errors can accumulate over > 3 months
   - Recommend periodic reinitialization for very long simulations

## Credits

Based on the original VBA rTemp model by:
- **Greg Pelletier**, Washington State Department of Ecology
- Concept by **J.E. Edinger Associates**

Primary reference:
- **Edinger, J.E., Brady, D.K. and Geyer, J.C.** (1974). *Heat exchange and transport in the environment*. EPRI publication no. 74-049-00-3.

## Support

- **Documentation**: See `docs/` directory
- **Issues**: Report on GitHub
- **Discussions**: Ask questions on GitHub Discussions
- **Contributing**: See `CONTRIBUTING.md`

## License

MIT License - See `LICENSE` file

## What's Next

Future releases will include:
- Additional solar radiation models
- Enhanced diagnostic capabilities
- Performance optimizations
- Additional validation datasets
- Extended documentation

---

**Thank you for using rTemp!** 🌊🌡️

We hope this tool helps advance water temperature modeling and environmental research.

For questions, issues, or contributions, please visit our GitHub repository.
