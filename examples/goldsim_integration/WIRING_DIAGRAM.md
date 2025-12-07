# GoldSim External Element Wiring Diagram

## Quick Setup Visual Guide

```
┌─────────────────────────────────────────────────────────────────┐
│                    GOLDSIM MODEL STRUCTURE                      │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: Site Parameters (Constants)                            │
├─────────────────────────────────────────────────────────────────┤
│  Latitude = 45.0        (degrees, -90 to 90)                   │
│  Longitude = -120.0     (degrees, -180 to 180)                 │
│  Elevation = 500.0      (meters)                               │
│  Timezone = 8.0         (hours from UTC, PST = 8)              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: Meteorological Data (Time Series or Expressions)       │
├─────────────────────────────────────────────────────────────────┤
│  Air_Temp_Min = [Time Series or Expression]  (°C)             │
│  Air_Temp_Max = [Time Series or Expression]  (°C)             │
│  Dewpoint_Min = [Time Series or Expression]  (°C)             │
│  Dewpoint_Max = [Time Series or Expression]  (°C)             │
│  Wind_Speed_Avg = [Time Series or Expression]  (m/s)          │
│  Cloud_Cover_Avg = [Time Series or Expression]  (0-1)         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 3: Hydraulic Model (Your Water Balance)                   │
├─────────────────────────────────────────────────────────────────┤
│  Water_Depth = [Your calculation]  (meters, must be ≥ 0)      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 4: State Variables (Previous Value Elements)              │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Previous Value: Water_Temperature                        │  │
│  │   Initial Value: 15.0  (°C)                             │  │
│  │   Previous Value = rTemp_Physics.New_Water_Temp         │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Previous Value: Sediment_Temperature                     │  │
│  │   Initial Value: 15.0  (°C)                             │  │
│  │   Previous Value = rTemp_Physics.New_Sediment_Temp      │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 5: External Element - rTemp_Physics                       │
├─────────────────────────────────────────────────────────────────┤
│  DLL: rtemp_adapter.dll                                        │
│  Function: GSPy                                                │
│                                                                 │
│  INPUTS (14):                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ [0] Current_Water_Temp ← Water_Temperature               │  │
│  │ [1] Current_Sediment_Temp ← Sediment_Temperature         │  │
│  │ [2] Water_Depth ← Water_Depth                            │  │
│  │ [3] Latitude ← Latitude                                  │  │
│  │ [4] Longitude ← Longitude                                │  │
│  │ [5] Elevation ← Elevation                                │  │
│  │ [6] Timezone ← Timezone                                  │  │
│  │ [7] Air_Temp_Min ← Air_Temp_Min                          │  │
│  │ [8] Air_Temp_Max ← Air_Temp_Max                          │  │
│  │ [9] Dewpoint_Min ← Dewpoint_Min                          │  │
│  │ [10] Dewpoint_Max ← Dewpoint_Max                         │  │
│  │ [11] Wind_Speed_Avg ← Wind_Speed_Avg                     │  │
│  │ [12] Cloud_Cover_Avg ← Cloud_Cover_Avg                   │  │
│  │ [13] Simulation_Date ← ElapsedTime                       │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  OUTPUTS (3):                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ [0] New_Water_Temp → (°C)                                │  │
│  │ [1] New_Sediment_Temp → (°C)                             │  │
│  │ [2] Daily_Avg_Net_Flux → (W/m²)                          │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 6: Results Collection (Time History Elements)             │
├─────────────────────────────────────────────────────────────────┤
│  Water_Temp_History ← rTemp_Physics.New_Water_Temp             │
│  Sediment_Temp_History ← rTemp_Physics.New_Sediment_Temp       │
│  Net_Flux_History ← rTemp_Physics.Daily_Avg_Net_Flux           │
└─────────────────────────────────────────────────────────────────┘
```

## Critical Configuration Details

### External Element Dialog Box Settings

**General Tab:**
- Element Name: `rTemp_Physics`
- DLL Path: `rtemp_adapter.dll` (can be relative path)
- Function Name: `GSPy` ⚠️ **MUST BE "GSPy" NOT "process_data"**

**Inputs Tab:**
Click "Add" 14 times and configure each:

| # | Name | Type | Link To |
|---|------|------|---------|
| 0 | Current_Water_Temp | Scalar | Water_Temperature |
| 1 | Current_Sediment_Temp | Scalar | Sediment_Temperature |
| 2 | Water_Depth | Scalar | Water_Depth |
| 3 | Latitude | Scalar | Latitude |
| 4 | Longitude | Scalar | Longitude |
| 5 | Elevation | Scalar | Elevation |
| 6 | Timezone | Scalar | Timezone |
| 7 | Air_Temp_Min | Scalar | Air_Temp_Min |
| 8 | Air_Temp_Max | Scalar | Air_Temp_Max |
| 9 | Dewpoint_Min | Scalar | Dewpoint_Min |
| 10 | Dewpoint_Max | Scalar | Dewpoint_Max |
| 11 | Wind_Speed_Avg | Scalar | Wind_Speed_Avg |
| 12 | Cloud_Cover_Avg | Scalar | Cloud_Cover_Avg |
| 13 | Simulation_Date | Scalar | ElapsedTime |

**Outputs Tab:**
Click "Add" 3 times and configure each:

| # | Name | Type | Units |
|---|------|------|-------|
| 0 | New_Water_Temp | Scalar | °C |
| 1 | New_Sediment_Temp | Scalar | °C |
| 2 | Daily_Avg_Net_Flux | Scalar | W/m² |

## Example Values for Testing

Use these values for initial testing:

```
Site Parameters:
  Latitude = 45.0 (Portland, OR area)
  Longitude = -122.0
  Elevation = 100.0 meters
  Timezone = 8.0 (PST)

Initial Conditions:
  Water_Temperature = 15.0 °C
  Sediment_Temperature = 15.0 °C
  Water_Depth = 1.0 meters

Summer Day Meteorology:
  Air_Temp_Min = 15.0 °C
  Air_Temp_Max = 30.0 °C
  Dewpoint_Min = 10.0 °C
  Dewpoint_Max = 15.0 °C
  Wind_Speed_Avg = 2.0 m/s
  Cloud_Cover_Avg = 0.3 (30% clouds)
```

## Simulation Settings

**Timestep:** Daily (1 day)
- GoldSim calls rTemp once per day
- rTemp internally runs at hourly resolution
- Returns end-of-day state

**Duration:** Start with 10 days for testing
- Should complete in ~1 second
- Check results before running longer simulations

## Common Mistakes to Avoid

❌ **Function Name = "process_data"**
✅ **Function Name = "GSPy"**

❌ **Inputs in wrong order**
✅ **Follow exact order 0-13 as listed above**

❌ **Outputs in wrong order**
✅ **Follow exact order 0-2 as listed above**

❌ **Forgot to create feedback loops**
✅ **Previous Value elements must feed back to External inputs**

❌ **REFERENCE_DATE doesn't match simulation start**
✅ **Edit rtemp_goldsim_adapter.py to set correct date**

❌ **Negative water depth**
✅ **Ensure Water_Depth ≥ 0 always**

## Testing Checklist

Before running full simulation:

- [ ] DLL file exists and is named `rtemp_adapter.dll`
- [ ] Function name is `GSPy` (not "process_data")
- [ ] All 14 inputs configured in correct order
- [ ] All 3 outputs configured in correct order
- [ ] Previous Value elements created for state variables
- [ ] Feedback loops connected (outputs → Previous Values → inputs)
- [ ] REFERENCE_DATE set in adapter script
- [ ] Validation script passed: `python validate_environment.py`
- [ ] Test run with 10 days completes successfully
- [ ] Check log file: `rtemp_adapter.log` for errors

## Where to Find Help

1. **Log File:** `rtemp_adapter.log` in GoldSim directory
   - Check for [ERROR] entries
   - Shows detailed Python tracebacks

2. **Documentation:**
   - `GOLDSIM_INTEGRATION_README.md` - Full guide
   - `TROUBLESHOOTING_GUIDE.md` - Common issues
   - `QUICK_REFERENCE.md` - Input/output specs

3. **Validation:**
   - Run `python validate_environment.py` to check setup
   - Run `python verify_json_config.py` to check JSON
