# GoldSim-rTemp Integration Quick Start Guide

Get up and running with the GoldSim-rTemp integration in 15 minutes.

## Prerequisites

- Windows computer
- GoldSim 15+ (64-bit)
- Administrator access (for Python installation)

## Step 1: Install Python (5 minutes)

1. Download Python 3.11 (64-bit): https://www.python.org/downloads/
2. Run installer:
   - ✅ Check "Add Python to PATH"
   - ✅ Check "Install for all users"
   - Click "Install Now"
3. Verify installation:
   ```cmd
   py -3.11 --version
   ```
   Should show: `Python 3.11.x`

## Step 2: Install Packages (3 minutes)

Open Command Prompt and run:

```cmd
py -3.11 -m pip install numpy pandas scipy rtemp
```

Wait for installation to complete.

## Step 3: Download GSPy (2 minutes)

1. Go to: https://github.com/GoldSim/GSPy/releases
2. Download `GSPy_v1.8.8.zip`
3. Extract ZIP file
4. Copy `GSPy_Release_py311.dll` to your project folder
5. Rename it to `rtemp_adapter.dll`

## Step 4: Set Up Project Files (3 minutes)

1. Copy these files to your project folder:
   - `rtemp_goldsim_adapter.py` (Python adapter script)
   - `rtemp_adapter.json` (GSPy configuration)

2. Edit `rtemp_adapter.json`:
   - Find `"python_path"` line
   - Replace with your Python path:
     ```cmd
     py -3.11 -c "import sys; print(sys.prefix)"
     ```
   - Use double backslashes: `C:\\Users\\...\\Python311`

3. Edit `rtemp_goldsim_adapter.py`:
   - Find `REFERENCE_DATE = datetime(2024, 1, 1)`
   - Change to match your GoldSim simulation start date

## Step 5: Validate Environment (1 minute)

Run validation script:

```cmd
py -3.11 validate_environment.py
```

All checks should pass ✓

## Step 6: Configure GoldSim (5 minutes)

### Create External Element

1. In GoldSim, right-click → Insert Element → External
2. Name: "rTemp_Physics"
3. DLL Path: `rtemp_adapter.dll`
4. Function Name: `GSPy`

### Configure Interface

**Inputs** (14 total):
1. Current_Water_Temp (scalar)
2. Current_Sediment_Temp (scalar)
3. Water_Depth (scalar)
4. Latitude (scalar)
5. Longitude (scalar)
6. Elevation (scalar)
7. Timezone (scalar)
8. Air_Temp_Min (scalar)
9. Air_Temp_Max (scalar)
10. Dewpoint_Min (scalar)
11. Dewpoint_Max (scalar)
12. Wind_Speed_Avg (scalar)
13. Cloud_Cover_Avg (scalar)
14. Simulation_Date (scalar)

**Outputs** (3 total):
1. New_Water_Temp (scalar)
2. New_Sediment_Temp (scalar)
3. Daily_Avg_Net_Flux (scalar)

### Create State Variables

1. Create Previous Value element: "Water_Temperature"
   - Initial Value: 15.0
   - Expression: `rTemp_Physics.New_Water_Temp`

2. Create Previous Value element: "Sediment_Temperature"
   - Initial Value: 15.0
   - Expression: `rTemp_Physics.New_Sediment_Temp`

3. Connect to External element:
   - Input[0]: `Water_Temperature`
   - Input[1]: `Sediment_Temperature`

### Connect Other Inputs

- Input[2]: Water depth from your water balance model
- Input[3-6]: Site parameters (constants)
- Input[7-13]: Meteorological data (time series or constants)
- Input[14]: `ElapsedTime` (GoldSim built-in)

## Step 7: Test Run (1 minute)

1. Set simulation duration: 10 days
2. Set timestep: 1 day
3. Click Run
4. Check results:
   - Water temperature should be reasonable (0-30°C)
   - Should see log file: `rtemp_adapter.log`

## Minimal Example

Here's a minimal GoldSim model structure:

```
Site Parameters (Constants):
├─ Latitude = 45.0
├─ Longitude = -120.0
├─ Elevation = 100.0
└─ Timezone = 8.0

Meteorological Data (Constants for testing):
├─ Air_Temp_Min = 10.0
├─ Air_Temp_Max = 25.0
├─ Dewpoint_Min = 5.0
├─ Dewpoint_Max = 15.0
├─ Wind_Speed_Avg = 3.0
└─ Cloud_Cover_Avg = 0.3

Hydraulic (Constant for testing):
└─ Water_Depth = 1.0

State Variables (Previous Values):
├─ Water_Temperature (init: 15.0) = rTemp_Physics.New_Water_Temp
└─ Sediment_Temperature (init: 15.0) = rTemp_Physics.New_Sediment_Temp

External Element: rTemp_Physics
├─ Inputs: All parameters above + ElapsedTime
└─ Outputs: New_Water_Temp, New_Sediment_Temp, Daily_Avg_Net_Flux
```

## Troubleshooting

### "Cannot load DLL"
- Add Python to PATH (see Step 1)
- Restart computer
- Verify DLL name is exactly `rtemp_adapter.dll`

### "Error in external function"
- Check log file: `rtemp_adapter.log`
- Look for `[ERROR]` entries
- Common issues:
  - Negative water depth
  - Invalid lat/lon ranges
  - Wrong REFERENCE_DATE

### Incorrect results
- Verify REFERENCE_DATE matches simulation start
- Check timezone is correct (hours from UTC)
- Verify input units (°C, m/s, meters)

## Next Steps

- Read full documentation: `GOLDSIM_INTEGRATION_README.md`
- Review troubleshooting guide: `TROUBLESHOOTING_GUIDE.md`
- Add real meteorological data
- Connect to water balance model
- Run multi-year simulations

## Example Input Values

For testing, use these typical values:

| Parameter | Example Value | Notes |
|-----------|---------------|-------|
| Latitude | 45.0 | Mid-latitude location |
| Longitude | -120.0 | Western US |
| Elevation | 100.0 | Low elevation |
| Timezone | 8.0 | Pacific Time |
| Air_Temp_Min | 10.0 | Cool morning |
| Air_Temp_Max | 25.0 | Warm afternoon |
| Dewpoint_Min | 5.0 | Dry morning |
| Dewpoint_Max | 15.0 | Humid afternoon |
| Wind_Speed_Avg | 3.0 | Light breeze |
| Cloud_Cover_Avg | 0.3 | Partly cloudy |
| Water_Depth | 1.0 | Moderate depth |

## Support

- Full documentation: `GOLDSIM_INTEGRATION_README.md`
- Troubleshooting: `TROUBLESHOOTING_GUIDE.md`
- Validation script: `validate_environment.py`
- rTemp docs: `docs/` directory in rTemp package

---

**Time to complete**: ~15 minutes  
**Difficulty**: Beginner  
**Last updated**: 2024-12-06
