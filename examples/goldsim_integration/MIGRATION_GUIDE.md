# Migration Guide - File Location Changes

If you were using the GoldSim integration files from the root directory, they have been moved to `examples/goldsim_integration/`.

## File Location Changes

### Core Files

| Old Location (root) | New Location |
|---------------------|--------------|
| `rtemp_goldsim_adapter.py` | `examples/goldsim_integration/rtemp_goldsim_adapter.py` |
| `GSPy_314.json` | `examples/goldsim_integration/GSPy_314.json` |
| `validate_environment.py` | `examples/goldsim_integration/validate_environment.py` |
| `verify_json_config.py` | `examples/goldsim_integration/verify_json_config.py` |
| `setup_goldsim_integration.py` | `examples/goldsim_integration/setup_goldsim_integration.py` |

### Documentation Files

| Old Location (root) | New Location |
|---------------------|--------------|
| `GOLDSIM_INTEGRATION_README.md` | `examples/goldsim_integration/INTEGRATION_GUIDE.md` |
| `QUICK_REFERENCE.md` | `examples/goldsim_integration/QUICK_REFERENCE.md` |
| `TROUBLESHOOTING_GUIDE.md` | `examples/goldsim_integration/TROUBLESHOOTING.md` |
| `DEWPOINT_ESTIMATION_GUIDE.md` | `examples/goldsim_integration/DEWPOINT_ESTIMATION.md` |
| `GOLDSIM_WIRING_DIAGRAM.md` | `examples/goldsim_integration/WIRING_DIAGRAM.md` |
| `GOLDSIM_SETUP_CHECKLIST.md` | `examples/goldsim_integration/SETUP_CHECKLIST.md` |
| `SIMPLIFIED_INPUT_ORDER.md` | `examples/goldsim_integration/INPUT_ORDER.md` |
| `blog_post_goldsim_rtemp.html` | `examples/goldsim_integration/blog_post.html` |

### New Files

| File | Description |
|------|-------------|
| `examples/goldsim_integration/README.md` | Quick start guide |
| `examples/goldsim_integration/cloud_cover_estimation.md` | Cloud cover from precipitation |

## What Changed

### Simplified Adapter
The adapter has been simplified to 12 inputs (removed dewpoint inputs):
- Dewpoint is now estimated automatically from air temperature
- No need to provide dewpoint_min and dewpoint_max
- Adjust dewpoint depression values in script for your climate

### Removed Files
These temporary/duplicate files are no longer needed:
- `rtemp_goldsim_adapter_simplified.py` (merged into main adapter)
- `rtemp_goldsim_adapter_with_dewpoint_estimation.py` (merged into main adapter)
- `GSPy_314_simplified.json` (now just `GSPy_314.json`)
- `GSPy_314_fixed.json` (temporary file)
- `GSPy_314_updated.json` (temporary file)
- `rtemp_adapter.json` (old version)

## Migration Steps

### If You Have an Existing GoldSim Model

1. **Update File Paths**
   - Copy files from `examples/goldsim_integration/` to your GoldSim project directory
   - Or update your project to reference the new location

2. **Update GoldSim External Element**
   - If you had 14 inputs, remove inputs 9 and 10 (Dewpoint_Min, Dewpoint_Max)
   - You should now have 12 inputs
   - Outputs remain unchanged (3 outputs)

3. **Update JSON Configuration**
   - Use the new `GSPy_314.json` from `examples/goldsim_integration/`
   - Verify `python_path` points to your Python installation

4. **Update Python Adapter**
   - Use the new `rtemp_goldsim_adapter.py`
   - Set `REFERENCE_DATE` to match your simulation start date
   - Optionally adjust `DEWPOINT_DEPRESSION_MIN` and `DEWPOINT_DEPRESSION_MAX` for your climate

5. **Test**
   - Run `validate_environment.py` to verify setup
   - Run a short test simulation (10 days)
   - Check log file for any errors

### If You're Starting Fresh

Simply follow the instructions in `examples/goldsim_integration/README.md` - no migration needed!

## Input Order Change

### Old (14 inputs)
1. Current_Water_Temp
2. Current_Sediment_Temp
3. Water_Depth
4. Latitude
5. Longitude
6. Elevation
7. Timezone
8. Air_Temp_Min
9. Air_Temp_Max
10. **Dewpoint_Min** ← REMOVED
11. **Dewpoint_Max** ← REMOVED
12. Wind_Speed_Avg
13. Cloud_Cover_Avg
14. Simulation_Date

### New (12 inputs)
1. Current_Water_Temp
2. Current_Sediment_Temp
3. Water_Depth
4. Latitude
5. Longitude
6. Elevation
7. Timezone
8. Air_Temp_Min
9. Air_Temp_Max
10. Wind_Speed_Avg ← moved up
11. Cloud_Cover_Avg ← moved up
12. Simulation_Date ← moved up

## Dewpoint Estimation

The adapter now estimates dewpoint automatically:
- `Dewpoint_Min = Air_Temp_Min - 2°C` (humid nighttime)
- `Dewpoint_Max = Air_Temp_Max - 8°C` (drier daytime)

To adjust for your climate, edit `rtemp_goldsim_adapter.py`:

```python
# For humid climates (coastal, tropical)
DEWPOINT_DEPRESSION_MIN = 1.0
DEWPOINT_DEPRESSION_MAX = 5.0

# For moderate climates (default)
DEWPOINT_DEPRESSION_MIN = 2.0
DEWPOINT_DEPRESSION_MAX = 8.0

# For dry climates (arid, desert)
DEWPOINT_DEPRESSION_MIN = 5.0
DEWPOINT_DEPRESSION_MAX = 15.0
```

## Benefits of Migration

1. **Simpler Interface**: 12 inputs instead of 14
2. **Automatic Estimation**: No need to calculate dewpoint
3. **Better Organization**: All files in one directory
4. **Improved Documentation**: Multiple guides for different needs
5. **Easier Updates**: Single location for all integration files

## Support

If you encounter issues during migration:
1. Check `examples/goldsim_integration/TROUBLESHOOTING.md`
2. Review log file (`GSPy_314.log`) for errors
3. Run `validate_environment.py` to check setup
4. Open an issue on GitHub with details

## Backward Compatibility

If you need the old 14-input version with explicit dewpoint inputs:
1. Use `rtemp_goldsim_adapter_with_dewpoint_estimation.py` from the root directory (before cleanup)
2. Set dewpoint inputs to -999 to trigger estimation
3. Or provide actual dewpoint values when available

However, we recommend migrating to the simplified 12-input version for easier maintenance.
