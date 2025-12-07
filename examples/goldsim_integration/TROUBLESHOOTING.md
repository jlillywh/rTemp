# GoldSim-rTemp Integration Troubleshooting Guide

This guide provides detailed troubleshooting steps for common issues encountered when integrating rTemp with GoldSim.

## Quick Diagnostic Checklist

Before diving into specific errors, run through this checklist:

- [ ] Python 3.11 or 3.14 (64-bit) installed
- [ ] All required packages installed (numpy, pandas, scipy, rtemp)
- [ ] GSPy DLL matches Python version (py311 vs py314)
- [ ] `python_path` in JSON points to correct Python installation
- [ ] `REFERENCE_DATE` in adapter matches GoldSim simulation start date
- [ ] All 14 inputs connected in GoldSim External element
- [ ] State variables have feedback loops (Previous Value elements)
- [ ] Simulation timestep is 1 day
- [ ] Log file exists and is readable

## Error Categories

### 1. Installation and Configuration Errors

#### Error: "Cannot load DLL"

**Full Error Message**:
```
Error loading external DLL: Cannot load DLL 'rtemp_adapter.dll'
```

**Symptoms**:
- GoldSim shows error when trying to run simulation
- External element shows red X icon
- No log file created

**Root Causes**:
1. Python DLL not in system PATH
2. Wrong Python architecture (32-bit vs 64-bit)
3. GSPy DLL doesn't match Python version
4. Missing Visual C++ Redistributables

**Diagnostic Steps**:

1. **Check Python architecture**:
   ```cmd
   py -3.11 -c "import struct; print(f'{struct.calcsize(\"P\") * 8}-bit')"
   ```
   Should print `64-bit`

2. **Check Python in PATH**:
   ```cmd
   where python
   ```
   Should show Python installation directory

3. **Check GSPy DLL version**:
   - File name should be `GSPy_Release_py311.dll` for Python 3.11
   - File name should be `GSPy_Release_py314.dll` for Python 3.14

4. **Check Visual C++ Redistributables**:
   - Download from Microsoft: https://aka.ms/vs/17/release/vc_redist.x64.exe
   - Install and restart computer

**Solutions**:

**Solution A: Add Python to PATH**
1. Find Python installation directory:
   ```cmd
   py -3.11 -c "import sys; print(sys.prefix)"
   ```
2. Add to system PATH:
   - Control Panel → System → Advanced System Settings
   - Environment Variables → System Variables → Path
   - Add Python directory (e.g., `C:\Users\YourName\AppData\Local\Programs\Python\Python311`)
   - Add Scripts directory (e.g., `C:\Users\YourName\AppData\Local\Programs\Python\Python311\Scripts`)
3. Restart GoldSim

**Solution B: Use correct GSPy DLL**
1. Check Python version: `py --version`
2. Download correct GSPy DLL from GitHub
3. Rename to `rtemp_adapter.dll`
4. Place in same directory as GoldSim model

**Solution C: Reinstall Python**
1. Uninstall current Python
2. Download Python 3.11 or 3.14 (64-bit) from python.org
3. During installation:
   - ✅ Check "Add Python to PATH"
   - ✅ Check "Install for all users"
4. Reinstall packages:
   ```cmd
   py -3.11 -m pip install numpy pandas scipy rtemp
   ```

---

#### Error: "Could not initialize NumPy C-API"

**Full Error Message**:
```
RuntimeError: Could not initialize NumPy C-API: _ARRAY_API not found
```

**Symptoms**:
- Error appears in log file
- GoldSim simulation stops immediately
- Python imports work outside GoldSim

**Root Causes**:
1. Python version mismatch between GSPy DLL and installed Python
2. Corrupted NumPy installation
3. Multiple Python versions causing conflicts

**Diagnostic Steps**:

1. **Check Python version**:
   ```cmd
   py -3.11 --version
   ```

2. **Check NumPy installation**:
   ```cmd
   py -3.11 -c "import numpy; print(numpy.__version__)"
   ```

3. **Check for multiple Python installations**:
   ```cmd
   where python
   py -0
   ```

**Solutions**:

**Solution A: Reinstall NumPy**
```cmd
py -3.11 -m pip uninstall numpy
py -3.11 -m pip install numpy
```

**Solution B: Force reinstall all packages**
```cmd
py -3.11 -m pip install --force-reinstall numpy pandas scipy
```

**Solution C: Use virtual environment**
```cmd
py -3.11 -m venv venv_goldsim
venv_goldsim\Scripts\activate
pip install numpy pandas scipy rtemp
```
Then update `python_path` in JSON to point to virtual environment.

---

### 2. Configuration Errors

#### Error: "Error in external function. Return code 1."

**Full Error Message**:
```
Error in external function. Return code 1.
Check log file for details.
```

**Symptoms**:
- GoldSim simulation stops
- Log file contains ERROR entries
- Specific error message in log

**Root Causes**:
- Python adapter called `gspy.error()` due to invalid inputs
- Check log file for specific cause

**Diagnostic Steps**:

1. **Open log file**: `rtemp_adapter.log` in results directory
2. **Search for `[ERROR]` entries**
3. **Read error message and traceback**

**Common Sub-Errors**:

##### Sub-Error: "Invalid Water_Depth"

**Log Message**:
```
[ERROR] Invalid Water_Depth: -0.5 meters (must be >= 0)
```

**Cause**: Water depth is negative

**Solution**:
1. Check water balance calculations in GoldSim
2. Add constraint: `Water_Depth = Max(0, calculated_depth)`
3. Verify initial conditions are non-negative

##### Sub-Error: "Invalid Latitude"

**Log Message**:
```
[ERROR] Invalid Latitude: 95.0 degrees (must be -90 to 90)
```

**Cause**: Latitude outside valid range

**Solution**:
1. Check site parameter values in GoldSim
2. Verify latitude is in degrees (not radians)
3. Ensure positive values for northern hemisphere, negative for southern

##### Sub-Error: "Invalid Longitude"

**Log Message**:
```
[ERROR] Invalid Longitude: 200.0 degrees (must be -180 to 180)
```

**Cause**: Longitude outside valid range

**Solution**:
1. Check site parameter values in GoldSim
2. Verify longitude is in degrees (not radians)
3. Ensure positive values for eastern hemisphere, negative for western

##### Sub-Error: "DataFrame has X rows, expected 24"

**Log Message**:
```
[ERROR] DataFrame has 20 rows, expected 24
```

**Cause**: Bug in datetime stamp generation (should not occur in production)

**Solution**:
1. This indicates a bug in the adapter script
2. Check `REFERENCE_DATE` is set correctly
3. Verify `simulation_date` is a valid number
4. Contact support if issue persists

---

#### Error: Incorrect solar radiation values

**Symptoms**:
- Solar radiation seems too high or too low for season
- Water temperature doesn't match expected diurnal pattern
- Energy balance doesn't close

**Root Causes**:
1. `REFERENCE_DATE` doesn't match GoldSim simulation start date
2. Wrong timezone setting
3. Incorrect latitude/longitude

**Diagnostic Steps**:

1. **Check REFERENCE_DATE**:
   - Open `rtemp_goldsim_adapter.py`
   - Find `REFERENCE_DATE = datetime(YYYY, M, D)`
   - Compare to GoldSim simulation start date

2. **Check timezone**:
   - Verify timezone is hours from UTC
   - Positive values for west of UTC (e.g., Pacific = 8)
   - Negative values for east of UTC (e.g., Tokyo = -9)

3. **Check site parameters**:
   - Latitude: -90 to 90 (positive north)
   - Longitude: -180 to 180 (positive east)

**Solutions**:

**Solution A: Fix REFERENCE_DATE**
1. Determine GoldSim simulation start date
2. Edit `rtemp_goldsim_adapter.py`:
   ```python
   REFERENCE_DATE = datetime(2024, 7, 1)  # Example: July 1, 2024
   ```
3. Save and restart GoldSim

**Solution B: Fix timezone**
1. Determine correct timezone offset
   - Pacific Time: 8 hours
   - Mountain Time: 7 hours
   - Central Time: 6 hours
   - Eastern Time: 5 hours
2. Update timezone input in GoldSim

**Solution C: Verify site parameters**
1. Use online tool to verify lat/lon (e.g., Google Maps)
2. Ensure correct sign conventions
3. Update GoldSim site parameter elements

---

### 3. Runtime Errors

#### Error: Temperature discontinuities

**Symptoms**:
- Sudden jumps in water temperature between days
- Temperature changes by >5°C in one day
- Unrealistic temperature values

**Root Causes**:
1. Meteorological data has gaps or discontinuities
2. State variable feedback loop not connected
3. Dry-bed bypass triggered
4. Initial conditions not set

**Diagnostic Steps**:

1. **Check log file for dry-bed warnings**:
   ```
   [WARNING] Dry-bed condition detected
   ```

2. **Check state variable connections**:
   - Previous Value element should reference External element output
   - Verify feedback loop is closed

3. **Check meteorological data**:
   - Plot air temperature time series
   - Look for gaps, spikes, or unrealistic values

4. **Check initial conditions**:
   - Previous Value elements should have defined initial values
   - Typical: 15°C for both water and sediment

**Solutions**:

**Solution A: Fix state variable feedback**
1. Open GoldSim model
2. For water temperature:
   - Create Previous Value element: `Water_Temperature`
   - Set initial value: 15.0 °C
   - Set expression: `External.New_Water_Temp`
   - Connect to External element input
3. Repeat for sediment temperature

**Solution B: Fix meteorological data**
1. Check data source for gaps
2. Interpolate missing values
3. Smooth unrealistic spikes
4. Verify units (°C, not °F)

**Solution C: Handle dry-bed conditions**
1. If dry-bed is expected, no action needed
2. If unexpected, check water balance calculations
3. Consider adjusting `DRY_BED_THRESHOLD` in adapter

---

#### Error: Slow performance

**Symptoms**:
- Simulation takes much longer than expected
- >1 second per day execution time
- Log file is very large

**Root Causes**:
1. High log level creates excessive logging
2. Diagnostics enabled in rTemp
3. Inefficient meteorological data sources

**Diagnostic Steps**:

1. **Check log level**:
   - Open `rtemp_adapter.json`
   - Check `"log_level"` value

2. **Check log file size**:
   ```cmd
   dir rtemp_adapter.log
   ```

3. **Time a single day**:
   - Run simulation for 1 day
   - Note execution time

**Solutions**:

**Solution A: Reduce log level**
1. Edit `rtemp_adapter.json`:
   ```json
   {
     "log_level": 0,  // Change from 2 or 3 to 0
     ...
   }
   ```
2. Save and restart GoldSim

**Solution B: Disable diagnostics**
1. Edit `rtemp_goldsim_adapter.py`:
   ```python
   config = ModelConfiguration(
       ...
       enable_diagnostics=False,  // Ensure this is False
       ...
   )
   ```
2. Save and restart GoldSim

**Solution C: Optimize data sources**
1. Use GoldSim Element Vectors instead of Time Series files
2. Pre-process data to reduce file I/O
3. Use binary data formats instead of CSV

**Expected Performance**:
- ~0.1 seconds per day on modern hardware
- ~36 seconds for 1 year (365 days)
- ~6 minutes for 10 years

---

### 4. Data Errors

#### Error: Energy balance doesn't close

**Symptoms**:
- `Daily_Avg_Net_Flux` doesn't match expected energy balance
- Water temperature change doesn't match net flux
- Unrealistic heat flux values

**Root Causes**:
1. Missing heat flux components
2. Incorrect site parameters
3. Solar radiation calculation issues
4. Incorrect water depth

**Diagnostic Steps**:

1. **Calculate expected temperature change**:
   ```
   ΔT = (Q_net × Δt) / (ρ × c_p × depth)
   
   Where:
   - Q_net = Daily_Avg_Net_Flux (W/m²)
   - Δt = 86400 seconds (1 day)
   - ρ = 1000 kg/m³ (water density)
   - c_p = 4186 J/(kg·°C) (specific heat)
   - depth = water depth (m)
   ```

2. **Compare to actual temperature change**:
   ```
   ΔT_actual = New_Water_Temp - Current_Water_Temp
   ```

3. **Check site parameters**:
   - Latitude, longitude, elevation, timezone
   - Verify against known values

**Solutions**:

**Solution A: Verify site parameters**
1. Use online tool to get accurate lat/lon
2. Verify elevation from topographic map
3. Confirm timezone offset

**Solution B: Check REFERENCE_DATE**
1. Ensure it matches GoldSim simulation start
2. Verify calendar year is correct

**Solution C: Compare with standalone rTemp**
1. Extract one day of data from GoldSim
2. Run standalone rTemp with same inputs
3. Compare results
4. If different, check adapter implementation

---

### 5. Validation Errors

#### Error: Results don't match expected values

**Symptoms**:
- Water temperature seems too high or too low
- Sediment temperature doesn't follow air temperature
- Net flux has wrong sign

**Root Causes**:
1. Incorrect input units
2. Wrong sign conventions
3. Mismatched coordinate systems

**Diagnostic Steps**:

1. **Check input units**:
   - Temperature: °C (not °F or K)
   - Wind speed: m/s (not mph or km/h)
   - Cloud cover: fraction 0-1 (not percent)
   - Depth: meters (not feet or cm)

2. **Check sign conventions**:
   - Latitude: positive north, negative south
   - Longitude: positive east, negative west
   - Timezone: positive west of UTC, negative east

3. **Check coordinate systems**:
   - Ensure lat/lon are in decimal degrees (not DMS)

**Solutions**:

**Solution A: Convert units**
1. Add conversion factors in GoldSim:
   ```
   Air_Temp_C = (Air_Temp_F - 32) * 5/9
   Wind_Speed_ms = Wind_Speed_mph * 0.44704
   Cloud_Cover_frac = Cloud_Cover_percent / 100
   Depth_m = Depth_ft * 0.3048
   ```

**Solution B: Fix sign conventions**
1. Check hemisphere and adjust latitude sign
2. Check longitude relative to Prime Meridian
3. Verify timezone offset direction

**Solution C: Validate with known data**
1. Use published data for a known location
2. Compare rTemp results to measurements
3. Adjust parameters if needed

---

## Diagnostic Tools

### Log File Analysis

The log file (`rtemp_adapter.log`) contains detailed information about each execution:

**Log Levels**:
- `[ERROR]` (0): Fatal errors that stop simulation
- `[WARNING]` (1): Non-fatal issues (e.g., dry-bed bypass)
- `[INFO]` (2): Normal execution summaries
- `[DEBUG]` (3): Detailed intermediate values

**Useful Log Patterns**:

1. **Find all errors**:
   ```cmd
   findstr /C:"[ERROR]" rtemp_adapter.log
   ```

2. **Find dry-bed warnings**:
   ```cmd
   findstr /C:"Dry-bed" rtemp_adapter.log
   ```

3. **Find execution summaries**:
   ```cmd
   findstr /C:"Processing day" rtemp_adapter.log
   findstr /C:"rTemp complete" rtemp_adapter.log
   ```

### Environment Validation Script

Run the validation script to check your environment:

```cmd
py -3.11 validate_environment.py
```

This checks:
- Python version and architecture
- Required packages
- File presence
- JSON configuration
- Adapter syntax
- Test execution

### Manual Testing

Test the adapter outside GoldSim:

```python
# test_adapter.py
from rtemp_goldsim_adapter import process_data

# Sample inputs
args = (
    15.0,   # Current_Water_Temp
    15.0,   # Current_Sediment_Temp
    1.0,    # Water_Depth
    45.0,   # Latitude
    -120.0, # Longitude
    100.0,  # Elevation
    8.0,    # Timezone
    10.0,   # Air_Temp_Min
    25.0,   # Air_Temp_Max
    5.0,    # Dewpoint_Min
    15.0,   # Dewpoint_Max
    3.0,    # Wind_Speed_Avg
    0.3,    # Cloud_Cover_Avg
    0.0     # Simulation_Date
)

result = process_data(*args)
print(f"Result: {result}")
```

Run:
```cmd
py -3.11 test_adapter.py
```

---

## Getting Help

If you've tried all troubleshooting steps and still have issues:

1. **Collect diagnostic information**:
   - Python version: `py --version`
   - Package versions: `py -m pip list`
   - Log file: `rtemp_adapter.log`
   - JSON configuration: `rtemp_adapter.json`
   - Error messages and screenshots

2. **Check documentation**:
   - rTemp documentation: `docs/` directory
   - GSPy documentation: GitHub repository
   - GoldSim help files

3. **Contact support**:
   - Include all diagnostic information
   - Describe steps to reproduce issue
   - Provide minimal example if possible

---

## Appendix: Common Parameter Values

### Typical Site Parameters

| Location | Latitude | Longitude | Elevation | Timezone |
|----------|----------|-----------|-----------|----------|
| Seattle, WA | 47.6 | -122.3 | 50 m | 8 |
| Denver, CO | 39.7 | -105.0 | 1600 m | 7 |
| Chicago, IL | 41.9 | -87.6 | 180 m | 6 |
| New York, NY | 40.7 | -74.0 | 10 m | 5 |
| Miami, FL | 25.8 | -80.2 | 2 m | 5 |

### Typical Meteorological Ranges

| Parameter | Typical Range | Units |
|-----------|---------------|-------|
| Air Temperature | -20 to 40 | °C |
| Dewpoint | -25 to 30 | °C |
| Wind Speed | 0 to 15 | m/s |
| Cloud Cover | 0 to 1 | fraction |

### Typical Water Parameters

| Parameter | Typical Range | Units |
|-----------|---------------|-------|
| Water Depth | 0.1 to 10 | meters |
| Water Temperature | 0 to 30 | °C |
| Sediment Temperature | 5 to 25 | °C |

---

## Version History

- **v1.0** (2024-12-06): Initial troubleshooting guide
