# GoldSim-rTemp Integration Quick Reference Card

## Essential Commands

### Validate Environment
```cmd
py -3.11 validate_environment.py
```

### Check Python Version
```cmd
py -3.11 --version
```

### Install Packages
```cmd
py -3.11 -m pip install numpy pandas scipy rtemp
```

### Find Python Path
```cmd
py -3.11 -c "import sys; print(sys.prefix)"
```

## Critical Configuration

### REFERENCE_DATE (in rtemp_goldsim_adapter.py)
```python
REFERENCE_DATE = datetime(2024, 1, 1)  # MUST match GoldSim start date
```

### python_path (in rtemp_adapter.json)
```json
"python_path": "C:\\Users\\YourName\\AppData\\Local\\Programs\\Python\\Python311"
```

### Log Level (in rtemp_adapter.json)
```json
"log_level": 0  // 0=ERROR, 1=WARNING, 2=INFO, 3=DEBUG
```

## Input Parameters (14 total)

| # | Name | Type | Units | Range |
|---|------|------|-------|-------|
| 0 | Current_Water_Temp | scalar | °C | -5 to 50 |
| 1 | Current_Sediment_Temp | scalar | °C | -5 to 50 |
| 2 | Water_Depth | scalar | m | ≥0 |
| 3 | Latitude | scalar | deg | -90 to 90 |
| 4 | Longitude | scalar | deg | -180 to 180 |
| 5 | Elevation | scalar | m | -500 to 5000 |
| 6 | Timezone | scalar | hrs | -12 to 14 |
| 7 | Air_Temp_Min | scalar | °C | -50 to 50 |
| 8 | Air_Temp_Max | scalar | °C | -50 to 50 |
| 9 | Dewpoint_Min | scalar | °C | -50 to 50 |
| 10 | Dewpoint_Max | scalar | °C | -50 to 50 |
| 11 | Wind_Speed_Avg | scalar | m/s | 0 to 50 |
| 12 | Cloud_Cover_Avg | scalar | frac | 0 to 1 |
| 13 | Simulation_Date | scalar | days | ≥0 |

## Output Parameters (3 total)

| # | Name | Type | Units |
|---|------|------|-------|
| 0 | New_Water_Temp | scalar | °C |
| 1 | New_Sediment_Temp | scalar | °C |
| 2 | Daily_Avg_Net_Flux | scalar | W/m² |

## Common Errors

### "Cannot load DLL"
→ Add Python to PATH, restart computer

### "Error in external function"
→ Check `rtemp_adapter.log` for details

### Wrong solar radiation
→ Fix REFERENCE_DATE in adapter script

### Slow performance
→ Set `"log_level": 0` in JSON

## File Locations

```
project/
├── model.gsm                      # GoldSim model
├── rtemp_adapter.dll              # GSPy DLL
├── rtemp_adapter.json             # Configuration
├── rtemp_goldsim_adapter.py       # Adapter script
└── results/
    └── rtemp_adapter.log          # Log file
```

## GoldSim External Element

- **DLL Path**: `rtemp_adapter.dll`
- **Function Name**: `GSPy` (not "process_data")
- **Inputs**: 14 (see table above)
- **Outputs**: 3 (see table above)

## State Variables

```
Previous Value: Water_Temperature
  Initial: 15.0
  Expression: rTemp_Physics.New_Water_Temp

Previous Value: Sediment_Temperature
  Initial: 15.0
  Expression: rTemp_Physics.New_Sediment_Temp
```

## Example Values (for testing)

```
Latitude = 45.0
Longitude = -120.0
Elevation = 100.0
Timezone = 8.0
Air_Temp_Min = 10.0
Air_Temp_Max = 25.0
Dewpoint_Min = 5.0
Dewpoint_Max = 15.0
Wind_Speed_Avg = 3.0
Cloud_Cover_Avg = 0.3
Water_Depth = 1.0
```

## Performance Expectations

- Per day: ~0.1 seconds
- 1 year: ~36 seconds
- 10 years: ~6 minutes

## Documentation Files

- **Quick Start**: `QUICKSTART_GUIDE.md` (15 min)
- **Full Guide**: `GOLDSIM_INTEGRATION_README.md`
- **Troubleshooting**: `TROUBLESHOOTING_GUIDE.md`
- **Diagrams**: `GOLDSIM_MODEL_DIAGRAM.md`
- **Index**: `DOCUMENTATION_INDEX.md`

## Support

1. Run validation: `py -3.11 validate_environment.py`
2. Check log: `rtemp_adapter.log`
3. Search docs: Use Ctrl+F in markdown files
4. Review troubleshooting guide

---

**Version**: 1.0 | **Date**: 2024-12-06
