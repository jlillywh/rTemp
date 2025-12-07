# GoldSim-rTemp Integration Example

This directory contains a complete example of integrating the rTemp water temperature model into GoldSim using the GSPy Python bridge.

## Overview

This integration implements a stateless physics engine pattern where:
- GoldSim operates at a daily timestep and manages state variables
- Python adapter disaggregates daily meteorological data to hourly resolution
- rTemp executes thermal physics calculations at hourly resolution
- Final state is returned to GoldSim for the next timestep

## Files in This Directory

### Core Integration Files

- `rtemp_goldsim_adapter.py` - Python adapter script (12 inputs, 3 outputs, with automatic dewpoint estimation)
- `GSPy_314.json` - GSPy configuration file for Python 3.14
- `validate_environment.py` - Environment validation script
- `verify_json_config.py` - JSON configuration validator

### Documentation

- `INTEGRATION_GUIDE.md` - Complete setup and usage guide
- `QUICK_REFERENCE.md` - Quick reference for inputs/outputs
- `TROUBLESHOOTING.md` - Common issues and solutions
- `DEWPOINT_ESTIMATION.md` - Guide for dewpoint estimation feature

### Setup Utilities

- `setup_goldsim_integration.py` - Automated setup script
- `cloud_cover_estimation.md` - Guide for estimating cloud cover from precipitation

## Quick Start

### 1. Prerequisites

- GoldSim version 15 or later (64-bit)
- Python 3.14 (64-bit)
- GSPy v1.8.8 DLL for Python 3.14
- Python packages: numpy, pandas, scipy, rtemp

### 2. Installation

Install Python packages:
```bash
pip install numpy pandas scipy
pip install git+https://github.com/jlillywh/rTemp.git
```

Download GSPy DLL:
- Get `GSPy_Release_py314.dll` from https://github.com/GoldSim/GSPy/releases
- Rename to match your project (e.g., `GSPy_314.dll`)

### 3. Configuration

1. Copy files to your GoldSim project directory:
   - `rtemp_goldsim_adapter.py`
   - `GSPy_314.json`
   - `GSPy_314.dll` (renamed from downloaded DLL)

2. Update `GSPy_314.json` with your Python path:
   ```json
   "python_path": "C:\\Users\\YourName\\AppData\\Local\\Programs\\Python\\Python314"
   ```

3. Set `REFERENCE_DATE` in `rtemp_goldsim_adapter.py` to match your simulation start date

### 4. GoldSim Model Setup

Create an External Element with:
- DLL: `GSPy_314.dll`
- Function: `GSPy`
- 12 inputs (in order):
  1. Current_Water_Temp
  2. Current_Sediment_Temp
  3. Water_Depth
  4. Latitude
  5. Longitude
  6. Elevation
  7. Timezone
  8. Air_Temp_Min
  9. Air_Temp_Max
  10. Wind_Speed_Avg
  11. Cloud_Cover_Avg
  12. Simulation_Date

- 3 outputs (in order):
  1. New_Water_Temp
  2. New_Sediment_Temp
  3. Daily_Avg_Net_Flux

Create Previous Value elements for state variables:
- Water_Temperature (feeds back to Current_Water_Temp)
- Sediment_Temperature (feeds back to Current_Sediment_Temp)

## Key Features

### Automatic Dewpoint Estimation

The adapter automatically estimates dewpoint from air temperature using typical dewpoint depression values:
- Dewpoint_Min = Air_Temp_Min - 2°C (humid nighttime)
- Dewpoint_Max = Air_Temp_Max - 8°C (drier daytime)

Adjust these values in the script for your climate (see `DEWPOINT_ESTIMATION.md`).

### Dry-Bed Handling

When water depth ≤ 0.01 m, the adapter bypasses rTemp calculation and returns safe fallback values to prevent numerical instability.

### Temporal Disaggregation

Daily min/max meteorological data is disaggregated to hourly values using:
- Sinusoidal pattern for temperature
- Solar position for timing of temperature extremes
- Constant values for wind speed and cloud cover

### Configurable Physics

The adapter allows customization of:
- Solar radiation method (Bras, Bird, Iqbal, Ryan)
- Longwave radiation method (Brunt, Brutsaert, Swinbank)
- Wind function method (Brady-Graves-Geyer, etc.)
- Dewpoint depression values for different climates

## Model Assumptions

The rTemp model assumes:
- Well-mixed water body (no vertical stratification)
- Uniform temperature throughout water column
- Surface temperature equals bulk average temperature

These assumptions are appropriate for:
- Shallow water bodies (< 2-3 meters)
- Daily timestep modeling
- Well-mixed conditions (wind, flow, convection)

## Performance

Expected execution time:
- ~0.1 seconds per day
- ~36 seconds for annual simulation (365 days)
- ~6 minutes for 10-year simulation

## Validation

The integration has been validated against standalone rTemp simulations showing:
- Proper thermal damping (water temp smoother than air temp)
- Appropriate lag in water temperature response
- Physically realistic temperature ranges
- Correct energy balance (via Daily_Avg_Net_Flux output)

## Support

For issues or questions:
1. Check `TROUBLESHOOTING.md` for common problems
2. Review log file (`GSPy_314.log`) for error messages
3. Run `validate_environment.py` to check setup
4. Open an issue on the rTemp GitHub repository

## References

- Original rTemp: [Washington State Department of Ecology](https://ecology.wa.gov/research-data/data-resources/models-spreadsheets/modeling-the-environment/models-tools-for-tmdls)
- GSPy: [GitHub Repository](https://github.com/GoldSim/GSPy)
- rTemp Python Implementation: [GitHub Repository](https://github.com/jlillywh/rTemp)

## License

This integration example follows the same MIT license as the rTemp package.
