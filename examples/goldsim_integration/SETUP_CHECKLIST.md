# GoldSim-rTemp Setup Checklist

**Your Configuration:**
- Python: 3.14.1 (64-bit) ✓
- Python Path: `C:\Users\JasonLillywhite\OneDrive - GoldSim\Python\rTemp\.venv`
- GoldSim Directory: `C:\Users\JasonLillywhite\GoldSim\GTGData - Documents\Library\Applications\Water Management\Water Quality\rTemp`

## ✅ Completed
- [x] Python 3.14 installed (64-bit)
- [x] Files copied to GoldSim directory
- [x] JSON configured with correct Python path

## 📋 To Do

### 1. Install scipy (Required!)
```cmd
python -m pip install scipy
```

### 2. Download GSPy DLL
- Go to: https://github.com/GoldSim/GSPy/releases
- Download: **GSPy_Release_py314.dll** (for Python 3.14)
- Save to: `C:\Users\JasonLillywhite\GoldSim\GTGData - Documents\Library\Applications\Water Management\Water Quality\rTemp`
- Rename to: **rtemp_adapter.dll**

### 3. Set Simulation Start Date
Edit `rtemp_goldsim_adapter.py` line 60:
```python
REFERENCE_DATE = datetime(2024, 1, 1)  # Change to YOUR simulation start date!
```

### 4. Validate Setup
```cmd
cd "C:\Users\JasonLillywhite\GoldSim\GTGData - Documents\Library\Applications\Water Management\Water Quality\rTemp"
python validate_environment.py
```

### 5. Configure GoldSim External Element

**Create External Element:**
- Right-click → Insert Element → External
- Name: `rTemp_Physics`

**DLL Configuration:**
- DLL Path: `rtemp_adapter.dll`
- Function Name: `GSPy` (NOT "process_data"!)

**Inputs (14 total, in exact order):**
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

**Outputs (3 total, in exact order):**
1. New_Water_Temp (scalar, °C)
2. New_Sediment_Temp (scalar, °C)
3. Daily_Avg_Net_Flux (scalar, W/m²)

### 6. Create State Variable Feedback Loops

**Water Temperature:**
```
Previous Value Element: "Water_Temperature"
  Initial Value: 15.0 °C
  Previous Value = rTemp_Physics.New_Water_Temp
  
Connect to External Element:
  rTemp_Physics.Current_Water_Temp = Water_Temperature
```

**Sediment Temperature:**
```
Previous Value Element: "Sediment_Temperature"
  Initial Value: 15.0 °C
  Previous Value = rTemp_Physics.New_Sediment_Temp
  
Connect to External Element:
  rTemp_Physics.Current_Sediment_Temp = Sediment_Temperature
```

**Simulation Date:**
```
Connect to External Element:
  rTemp_Physics.Simulation_Date = ElapsedTime
```

## 🔍 Troubleshooting

**"Cannot load DLL"**
- Make sure DLL is named exactly `rtemp_adapter.dll`
- Verify it's the py314 version for Python 3.14
- Check that Python path in JSON is correct

**"ModuleNotFoundError: scipy"**
- Run: `python -m pip install scipy`

**"Error in external function. Return code 1."**
- Check `rtemp_adapter.log` in the GoldSim directory
- Look for [ERROR] entries
- Common issues: negative water depth, invalid lat/lon

**Wrong solar radiation values**
- Verify REFERENCE_DATE matches your simulation start date
- Check timezone setting (hours from UTC)

## 📚 Documentation

Full documentation in your rTemp directory:
- `GOLDSIM_INTEGRATION_README.md` - Complete guide
- `TROUBLESHOOTING_GUIDE.md` - Detailed troubleshooting
- `QUICK_REFERENCE.md` - Quick reference for inputs/outputs
