# GoldSim-rTemp Integration Guide

## Overview

This guide provides complete instructions for integrating the rTemp water temperature model into GoldSim using the GSPy (v1.8.8) interface. The integration implements a **Stateless Physics Engine** architecture where GoldSim manages simulation time and state persistence, while Python executes high-resolution thermal physics calculations.

### Key Features

- **Daily timestep integration**: GoldSim calls Python once per day
- **Automatic disaggregation**: Converts daily min/max meteorological data to hourly values
- **Sub-daily physics**: rTemp executes at hourly resolution internally
- **Dry-bed handling**: Gracefully handles zero or near-zero water depth
- **Comprehensive error handling**: Validates inputs and reports errors to GoldSim
- **Diagnostic outputs**: Returns daily average net heat flux for energy balance validation

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      GoldSim Model                          │
│  (Daily Timestep, State Management, Water Balance)         │
│                                                             │
│  ┌──────────────┐      ┌──────────────┐                   │
│  │ Previous     │      │  External    │                   │
│  │ Value        │─────▶│  Element     │                   │
│  │ Elements     │      │  (GSPy)      │                   │
│  └──────────────┘      └──────┬───────┘                   │
│         ▲                     │                            │
│         │                     ▼                            │
│         │              ┌──────────────┐                   │
│         └──────────────│  Outputs     │                   │
│                        └──────────────┘                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    GSPy Bridge (DLL)                        │
│              (Data Marshalling, Error Handling)             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Python Adapter (process_data)                  │
│                                                             │
│  1. Unpack inputs from GoldSim                             │
│  2. Validate inputs (depth, lat/lon ranges)                │
│  3. Check dry-bed condition → bypass if needed             │
│  4. Disaggregate daily min/max to hourly values            │
│  5. Construct pandas DataFrame with datetime stamps        │
│  6. Initialize rTemp model configuration                   │
│  7. Execute rTemp for 24 hours                             │
│  8. Extract final state and diagnostics                    │
│  9. Return results to GoldSim                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    rTemp Model                              │
│         (Hourly Thermal Physics Calculations)               │
└─────────────────────────────────────────────────────────────┘
```

## Installation

### Prerequisites

- **GoldSim**: Version 15 or later (64-bit)
- **Python**: Version 3.11 or 3.14 (64-bit) - required by GSPy v1.8.8
- **Operating System**: Windows (GSPy is Windows-only)

### Step 1: Install Python

1. Download Python 3.11 or 3.14 (64-bit) from [python.org](https://www.python.org/downloads/)
2. During installation:
   - ✅ Check "Add Python to PATH"
   - ✅ Check "Install for all users" (optional but recommended)
3. Verify installation:
   ```cmd
   py -3.11 --version
   ```
   or
   ```cmd
   py -3.14 --version
   ```

### Step 2: Install Python Dependencies

Open Command Prompt and run:

```cmd
py -3.11 -m pip install --upgrade pip
py -3.11 -m pip install numpy pandas scipy
py -3.11 -m pip install rtemp
```

**Note**: Replace `3.11` with `3.14` if using Python 3.14.

### Step 3: Download and Configure GSPy

1. Download GSPy v1.8.8 from [GitHub releases](https://github.com/GoldSim/GSPy/releases)
2. Extract the ZIP file
3. Copy the appropriate DLL:
   - For Python 3.11: `GSPy_Release_py311.dll`
   - For Python 3.14: `GSPy_Release_py314.dll`
4. Rename the DLL to `rtemp_adapter.dll`
5. Place it in your GoldSim project directory

### Step 4: Set Up Project Files

Create a project directory with the following structure:

```
my_project/
├── model.gsm                      # Your GoldSim model
├── rtemp_adapter.dll              # Renamed GSPy DLL
├── rtemp_adapter.json             # GSPy configuration (see below)
├── rtemp_goldsim_adapter.py       # Python adapter script (see below)
└── results/                       # Output directory (optional)
    └── rtemp_adapter.log          # GSPy log file (created automatically)
```

### Step 5: Configure rtemp_adapter.json

Create `rtemp_adapter.json` with the following content:

```json
{
  "python_path": "C:\\Users\\YourUsername\\AppData\\Local\\Programs\\Python\\Python311",
  "script_path": "rtemp_goldsim_adapter.py",
  "function_name": "process_data",
  "log_level": 2,
  "inputs": [
    {"name": "Current_Water_Temp", "type": "scalar", "dimensions": []},
    {"name": "Current_Sediment_Temp", "type": "scalar", "dimensions": []},
    {"name": "Water_Depth", "type": "scalar", "dimensions": []},
    {"name": "Latitude", "type": "scalar", "dimensions": []},
    {"name": "Longitude", "type": "scalar", "dimensions": []},
    {"name": "Elevation", "type": "scalar", "dimensions": []},
    {"name": "Timezone", "type": "scalar", "dimensions": []},
    {"name": "Air_Temp_Min", "type": "scalar", "dimensions": []},
    {"name": "Air_Temp_Max", "type": "scalar", "dimensions": []},
    {"name": "Dewpoint_Min", "type": "scalar", "dimensions": []},
    {"name": "Dewpoint_Max", "type": "scalar", "dimensions": []},
    {"name": "Wind_Speed_Avg", "type": "scalar", "dimensions": []},
    {"name": "Cloud_Cover_Avg", "type": "scalar", "dimensions": []},
    {"name": "Simulation_Date", "type": "scalar", "dimensions": []}
  ],
  "outputs": [
    {"name": "New_Water_Temp", "type": "scalar", "dimensions": []},
    {"name": "New_Sediment_Temp", "type": "scalar", "dimensions": []},
    {"name": "Daily_Avg_Net_Flux", "type": "scalar", "dimensions": []}
  ]
}
```

**Important**: Update `python_path` to match your Python installation:
- Find your Python path: `py -3.11 -c "import sys; print(sys.prefix)"`
- Use double backslashes (`\\`) in the path

### Step 6: Configure REFERENCE_DATE

Open `rtemp_goldsim_adapter.py` and locate this line near the top:

```python
REFERENCE_DATE = datetime(2024, 1, 1)
```

**⚠️ CRITICAL**: Set `REFERENCE_DATE` to match your GoldSim simulation start date!

This ensures accurate solar geometry calculations. For example:
- If GoldSim starts on January 1, 2024: `datetime(2024, 1, 1)`
- If GoldSim starts on July 15, 2023: `datetime(2023, 7, 15)`
- If GoldSim starts on October 1, 2025: `datetime(2025, 10, 1)`

**Why this matters**: Solar radiation calculations depend on the calendar date to determine sun position, day length, and atmospheric path length. Incorrect dates will produce inaccurate solar radiation estimates.

### Step 7: Verify Installation

Run the environment validation script (see "Environment Validation" section below):

```cmd
py -3.11 validate_environment.py
```

This will check:
- ✅ Python version compatibility
- ✅ Required packages installed
- ✅ GSPy DLL present
- ✅ JSON configuration valid
- ✅ Adapter script syntax correct

## GoldSim Model Configuration

### External Element Setup

1. **Create External Element**:
   - Right-click in GoldSim → Insert Element → External
   - Name it "rTemp_Physics"

2. **Configure DLL**:
   - DLL Path: `rtemp_adapter.dll` (relative path)
   - Function Name: `GSPy` (this is the GSPy bridge function, NOT "process_data")

3. **Configure Interface** (14 inputs, 3 outputs):

   **Inputs** (in exact order):
   1. Current_Water_Temp (scalar, °C)
   2. Current_Sediment_Temp (scalar, °C)
   3. Water_Depth (scalar, meters)
   4. Latitude (scalar, degrees)
   5. Longitude (scalar, degrees)
   6. Elevation (scalar, meters)
   7. Timezone (scalar, hours from UTC)
   8. Air_Temp_Min (scalar, °C)
   9. Air_Temp_Max (scalar, °C)
   10. Dewpoint_Min (scalar, °C)
   11. Dewpoint_Max (scalar, °C)
   12. Wind_Speed_Avg (scalar, m/s)
   13. Cloud_Cover_Avg (scalar, fraction 0-1)
   14. Simulation_Date (scalar, elapsed days)

   **Outputs** (in exact order):
   1. New_Water_Temp (scalar, °C)
   2. New_Sediment_Temp (scalar, °C)
   3. Daily_Avg_Net_Flux (scalar, W/m²)

### State Variable Management

Create feedback loops for state variables:

```
┌─────────────────────────────────────────────────────────┐
│  Previous Value Element: "Water_Temperature"            │
│  Initial Value: 15.0 °C                                 │
│  ┌──────────────────────────────────────────────┐      │
│  │ Previous Value = External.New_Water_Temp     │      │
│  └──────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│  External Element: "rTemp_Physics"                      │
│  Input[0]: Water_Temperature (from Previous Value)      │
│  Output[0]: New_Water_Temp                              │
└─────────────────────────────────────────────────────────┘
```

Repeat for sediment temperature:

```
┌─────────────────────────────────────────────────────────┐
│  Previous Value Element: "Sediment_Temperature"         │
│  Initial Value: 15.0 °C                                 │
│  ┌──────────────────────────────────────────────┐      │
│  │ Previous Value = External.New_Sediment_Temp  │      │
│  └──────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│  External Element: "rTemp_Physics"                      │
│  Input[1]: Sediment_Temperature (from Previous Value)   │
│  Output[1]: New_Sediment_Temp                           │
└─────────────────────────────────────────────────────────┘
```

### Simulation Date

Connect `Simulation_Date` input to GoldSim's elapsed time:

```
External.Simulation_Date = ElapsedTime
```

Where `ElapsedTime` is in days from simulation start.

### Example GoldSim Model Structure

```
┌────────────────────────────────────────────────────────────────┐
│                     GoldSim Model Layout                       │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌─────────────────┐                                          │
│  │ Site Parameters │                                          │
│  │  - Latitude     │                                          │
│  │  - Longitude    │                                          │
│  │  - Elevation    │                                          │
│  │  - Timezone     │                                          │
│  └─────────────────┘                                          │
│           │                                                    │
│           ▼                                                    │
│  ┌─────────────────────────────────────┐                     │
│  │ Meteorological Data (Time Series)   │                     │
│  │  - Air_Temp_Min                     │                     │
│  │  - Air_Temp_Max                     │                     │
│  │  - Dewpoint_Min                     │                     │
│  │  - Dewpoint_Max                     │                     │
│  │  - Wind_Speed_Avg                   │                     │
│  │  - Cloud_Cover_Avg                  │                     │
│  └─────────────────────────────────────┘                     │
│           │                                                    │
│           ▼                                                    │
│  ┌─────────────────────────────────────┐                     │
│  │ Hydraulic Calculations              │                     │
│  │  - Water_Depth                      │                     │
│  │  (from water balance model)         │                     │
│  └─────────────────────────────────────┘                     │
│           │                                                    │
│           ▼                                                    │
│  ┌─────────────────────────────────────┐                     │
│  │ State Variables (Previous Values)   │                     │
│  │  - Water_Temperature (init: 15°C)   │                     │
│  │  - Sediment_Temperature (init: 15°C)│                     │
│  └─────────────────────────────────────┘                     │
│           │                                                    │
│           ▼                                                    │
│  ┌─────────────────────────────────────┐                     │
│  │ External Element: rTemp_Physics     │                     │
│  │  Inputs: 14 parameters              │                     │
│  │  Outputs: 3 results                 │                     │
│  └─────────────────────────────────────┘                     │
│           │                                                    │
│           ▼                                                    │
│  ┌─────────────────────────────────────┐                     │
│  │ Results Collection                  │                     │
│  │  - New_Water_Temp → Time History    │                     │
│  │  - New_Sediment_Temp → Time History │                     │
│  │  - Daily_Avg_Net_Flux → Time History│                     │
│  └─────────────────────────────────────┘                     │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

## Input Parameter Specifications

| Parameter | Type | Units | Valid Range | Description |
|-----------|------|-------|-------------|-------------|
| Current_Water_Temp | scalar | °C | -5 to 50 | Water temperature at start of day |
| Current_Sediment_Temp | scalar | °C | -5 to 50 | Sediment temperature at start of day |
| Water_Depth | scalar | meters | ≥0 | Water depth (≤0.01 triggers dry-bed) |
| Latitude | scalar | degrees | -90 to 90 | Site latitude (positive north) |
| Longitude | scalar | degrees | -180 to 180 | Site longitude (positive east) |
| Elevation | scalar | meters | -500 to 5000 | Site elevation above sea level |
| Timezone | scalar | hours | -12 to 14 | Hours from UTC (positive west) |
| Air_Temp_Min | scalar | °C | -50 to 50 | Daily minimum air temperature |
| Air_Temp_Max | scalar | °C | -50 to 50 | Daily maximum air temperature |
| Dewpoint_Min | scalar | °C | -50 to 50 | Daily minimum dewpoint temperature |
| Dewpoint_Max | scalar | °C | -50 to 50 | Daily maximum dewpoint temperature |
| Wind_Speed_Avg | scalar | m/s | 0 to 50 | Daily average wind speed |
| Cloud_Cover_Avg | scalar | fraction | 0 to 1 | Daily average cloud cover |
| Simulation_Date | scalar | days | ≥0 | Elapsed days from simulation start |

## Output Parameter Specifications

| Parameter | Type | Units | Description |
|-----------|------|-------|-------------|
| New_Water_Temp | scalar | °C | Water temperature at end of day |
| New_Sediment_Temp | scalar | °C | Sediment temperature at end of day |
| Daily_Avg_Net_Flux | scalar | W/m² | Mean net heat flux over 24 hours |

## Troubleshooting

### Error: "Cannot load DLL"

**Symptoms**: GoldSim shows "Cannot load DLL" or "DLL not found" error

**Causes**:
- Python DLL not in system PATH
- Wrong Python version (32-bit vs 64-bit)
- GSPy DLL doesn't match Python version

**Solutions**:
1. Verify Python is 64-bit: `py -3.11 -c "import struct; print(struct.calcsize('P') * 8)"`
   - Should print `64`
2. Add Python directory to system PATH:
   - Control Panel → System → Advanced → Environment Variables
   - Add Python installation directory to PATH
   - Restart GoldSim
3. Verify GSPy DLL matches Python version:
   - Python 3.11 → `GSPy_Release_py311.dll`
   - Python 3.14 → `GSPy_Release_py314.dll`

### Error: "Could not initialize NumPy C-API"

**Symptoms**: Error message about NumPy initialization

**Causes**:
- Python version mismatch between GSPy DLL and installed Python
- Corrupted NumPy installation

**Solutions**:
1. Verify Python version matches GSPy DLL
2. Reinstall NumPy: `py -3.11 -m pip install --force-reinstall numpy`
3. Restart GoldSim

### Error: "Error in external function. Return code 1."

**Symptoms**: GoldSim simulation stops with this error

**Causes**:
- Python adapter called `gspy.error()` due to invalid inputs or numerical error
- Check log file for details

**Solutions**:
1. Open `rtemp_adapter.log` in the results directory
2. Search for `[ERROR]` entries
3. Read the error message and traceback
4. Common issues:
   - **Invalid Water_Depth**: Check for negative values
   - **Invalid Latitude/Longitude**: Check site parameters are in valid ranges
   - **Array length errors**: Ensure meteorological data has correct dimensions
   - **Numerical errors**: Check for extreme input values (very high temps, etc.)

### Error: Incorrect solar radiation values

**Symptoms**: Solar radiation seems wrong for the season or location

**Causes**:
- `REFERENCE_DATE` in adapter doesn't match GoldSim simulation start date
- Wrong timezone setting

**Solutions**:
1. Open `rtemp_goldsim_adapter.py`
2. Find `REFERENCE_DATE = datetime(YYYY, M, D)`
3. Set to match GoldSim simulation start date exactly
4. Verify timezone is correct (hours from UTC, positive for west)

### Error: Slow performance

**Symptoms**: Simulation takes too long

**Causes**:
- High log level creates excessive logging overhead
- Diagnostics enabled in rTemp configuration

**Solutions**:
1. Set `"log_level": 0` in `rtemp_adapter.json` (errors only)
2. Verify `enable_diagnostics=False` in adapter script
3. Expected performance: ~0.1 seconds per day

### Error: Dry-bed warnings

**Symptoms**: Log shows "Dry-bed condition detected" warnings

**Causes**:
- Water depth at or below 0.01 meters
- This is expected behavior, not an error

**Solutions**:
- No action needed - adapter handles this gracefully
- If warnings are excessive, check water balance calculations
- Adjust `DRY_BED_THRESHOLD` in adapter if needed (default: 0.01 m)

### Error: Temperature discontinuities

**Symptoms**: Sudden jumps in water temperature between days

**Causes**:
- Meteorological data has discontinuities
- Initial conditions not properly set
- Dry-bed bypass triggered

**Solutions**:
1. Check meteorological data for gaps or unrealistic values
2. Verify state variable feedback loops are connected
3. Check log for dry-bed warnings
4. Verify `REFERENCE_DATE` is correct

### Error: Energy balance doesn't close

**Symptoms**: `Daily_Avg_Net_Flux` doesn't match expected energy balance

**Causes**:
- Missing heat flux components
- Incorrect site parameters
- Solar radiation calculation issues

**Solutions**:
1. Verify site parameters (lat, lon, elevation, timezone)
2. Check `REFERENCE_DATE` matches simulation start
3. Review rTemp configuration parameters in adapter
4. Compare with standalone rTemp simulation

## Environment Validation

Use the validation script to check your installation before running GoldSim:

```cmd
py -3.11 validate_environment.py
```

The script checks:
- ✅ Python version (3.11 or 3.14, 64-bit)
- ✅ Required packages (numpy, pandas, scipy, rtemp)
- ✅ GSPy DLL present
- ✅ JSON configuration valid
- ✅ Adapter script syntax
- ✅ Test execution of adapter function

See "Environment Validation Script" section below for the complete script.

## Advanced Configuration

### Changing rTemp Calculation Methods

Edit `rtemp_goldsim_adapter.py` to change calculation methods:

```python
config = ModelConfiguration(
    # ...
    solar_method="Bird",  # Options: "Bras", "Bird", "Iqbal", "Ryan"
    longwave_method="Brutsaert",  # Options: "Brunt", "Brutsaert", "Swinbank"
    wind_function_method="Brady-Graves-Geyer",  # Options: see rTemp docs
    # ...
)
```

### Making Parameters Dynamic

To pass additional parameters from GoldSim:

1. Add to `rtemp_adapter.json` inputs array
2. Update `process_data()` to unpack new parameter
3. Pass to `ModelConfiguration`
4. Add input to GoldSim External element interface

Example: Making `effective_shade` dynamic:

```json
// In rtemp_adapter.json, add to inputs:
{"name": "Effective_Shade", "type": "scalar", "dimensions": []}
```

```python
# In rtemp_goldsim_adapter.py:
effective_shade = float(args[14])  # New position after Simulation_Date

config = ModelConfiguration(
    # ...
    effective_shade=effective_shade,  # Use dynamic value
    # ...
)
```

### Adjusting Dry-Bed Threshold

Edit `rtemp_goldsim_adapter.py`:

```python
DRY_BED_THRESHOLD = 0.01  # Change to desired value (meters)
```

Lower values (e.g., 0.001) will allow rTemp to run at shallower depths but may cause numerical instability.

### Changing Log Level

Edit `rtemp_adapter.json`:

```json
{
  "log_level": 0,  // 0=ERROR, 1=WARNING, 2=INFO, 3=DEBUG
  // ...
}
```

- **Production**: Use `0` (errors only) for maximum performance
- **Development**: Use `3` (debug) for detailed diagnostics
- **Normal**: Use `2` (info) for execution summaries

## Performance Expectations

- **Per-day execution**: ~0.1 seconds on modern hardware
- **Annual simulation**: ~36 seconds (365 days)
- **10-year simulation**: ~6 minutes
- **100-year simulation**: ~60 minutes

Performance tips:
- Set `log_level: 0` in production
- Use `enable_diagnostics: False` in adapter
- Ensure Python packages are up to date
- Use SSD for faster file I/O

## Support and Resources

- **rTemp Documentation**: See `docs/` directory in rTemp package
- **GSPy Documentation**: [GitHub repository](https://github.com/GoldSim/GSPy)
- **GoldSim Support**: [GoldSim website](https://www.goldsim.com)

## Version Compatibility

- **rTemp**: v1.0.0 or later
- **GSPy**: v1.8.8
- **Python**: 3.11 or 3.14 (64-bit)
- **GoldSim**: 15 or later (64-bit)
- **NumPy**: 1.20 or later
- **Pandas**: 1.3 or later
- **SciPy**: 1.7 or later

## License

This integration adapter follows the same license as the rTemp package. See LICENSE file for details.
