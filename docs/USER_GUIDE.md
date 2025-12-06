# rTemp User Guide

Welcome to the rTemp water temperature model user guide. This guide will help you get started with installing, configuring, and running the model.

## About rTemp

**Response Temperature Model**  
**Original Author:** Greg Pelletier, Washington State Department of Ecology  
**Concept by:** J.E. Edinger Associates

Response temperature is the temperature that a column of fully mixed water would have if heat fluxes across the surface were the only heat transfer processes. The model calculates water temperature by solving the heat budget equation using meteorological data.

### Key Features

- **Simple yet comprehensive**: Accounts for all major heat exchange processes
- **Long-term statistics**: Use historical meteorological data to estimate natural water temperature patterns
- **Extended capabilities**: Includes streambed conduction, groundwater inflow, and hyporheic exchange
- **Multiple methods**: Choose from various solar radiation, longwave radiation, and wind function models
- **Validated**: Excellent agreement with original VBA implementation (0.13°C RMSE)

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Input Data Preparation](#input-data-preparation)
4. [Running the Model](#running-the-model)
5. [Understanding Output](#understanding-output)
6. [Advanced Usage](#advanced-usage)
7. [Best Practices](#best-practices)
8. [Validation Results](#validation-results)

---

## Installation

### Requirements

- Python 3.8 or higher
- pip package manager

### Installing from Source

1. Clone or download the repository:
```bash
git clone <repository-url>
cd rtemp
```

2. Create a virtual environment (recommended):
```bash
python -m venv .venv

# On Windows:
.venv\Scripts\activate

# On macOS/Linux:
source .venv/bin/activate
```

3. Install the package:
```bash
# For users:
pip install -e .

# For developers (includes testing tools):
pip install -e ".[dev]"
```

### Verifying Installation

Test your installation:
```python
python -c "from rtemp import RTempModel; print('rTemp installed successfully!')"
```

---

## Quick Start

Here's a minimal example to get you started:

```python
from rtemp import RTempModel, ModelConfiguration
import pandas as pd
from datetime import datetime, timedelta

# 1. Create model configuration
config = ModelConfiguration(
    latitude=47.5,           # Seattle area
    longitude=-122.0,
    elevation=100.0,         # meters
    timezone=8.0,            # PST (UTC-8)
    initial_water_temp=15.0, # °C
    water_depth=2.0          # meters
)

# 2. Prepare meteorological data
dates = pd.date_range(start='2024-06-01', end='2024-06-02', freq='1H')
met_data = pd.DataFrame({
    'datetime': dates,
    'air_temp': 20.0,      # °C
    'dewpoint': 12.0,      # °C
    'wind_speed': 2.0,     # m/s
    'cloud_cover': 0.3     # fraction (0-1)
})

# 3. Run the model
model = RTempModel(config)
results = model.run(met_data)

# 4. View results
print(results[['datetime', 'water_temp', 'net_flux']].head())

# 5. Save results
results.to_csv('water_temperature_output.csv', index=False)
```

---

## Input Data Preparation

### Required Meteorological Data

Your input DataFrame must contain these columns:

| Column | Type | Units | Description |
|--------|------|-------|-------------|
| `datetime` | datetime | - | Timestamp for each observation |
| `air_temp` | float | °C | Air temperature |
| `dewpoint` | float | °C | Dewpoint temperature |
| `wind_speed` | float | m/s | Wind speed |
| `cloud_cover` | float | 0-1 | Cloud cover fraction |

### Data Format Example

```python
import pandas as pd

# From CSV file
met_data = pd.read_csv('meteorological_data.csv', parse_dates=['datetime'])

# Or create manually
met_data = pd.DataFrame({
    'datetime': pd.date_range('2024-06-01', periods=24, freq='1H'),
    'air_temp': [15, 16, 18, 20, 22, 23, 24, 24, 23, 21, 19, 17,
                 16, 15, 14, 14, 15, 16, 18, 19, 20, 19, 18, 16],
    'dewpoint': [10, 11, 12, 13, 14, 14, 15, 15, 14, 13, 12, 11,
                 10, 10, 9, 9, 10, 11, 12, 13, 13, 12, 11, 10],
    'wind_speed': [2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.0, 4.5, 4.0,
                   3.5, 3.0, 2.5, 2.0, 1.5, 1.5, 2.0, 2.5, 3.0, 3.5,
                   4.0, 3.5, 3.0, 2.5],
    'cloud_cover': [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.7, 0.6, 0.5,
                    0.4, 0.3, 0.2, 0.1, 0.1, 0.2, 0.3, 0.4, 0.5, 0.4,
                    0.3, 0.2, 0.2, 0.2]
})
```

### Optional Data Columns

You can include additional columns for advanced features:

**Time-Varying Parameters:**
- `water_depth_override`: Override water depth (meters)
- `effective_shade_override`: Override shade fraction (0-1)

**Measured Solar Radiation:**
- `solar_radiation`: Measured solar radiation (W/m²)

**Bird-Hulstrom Method Parameters:**
- `pressure_mb`: Atmospheric pressure (millibars)
- `ozone_cm`: Ozone layer thickness (cm)
- `water_vapor_cm`: Precipitable water vapor (cm)
- `aod_500nm`: Aerosol optical depth at 500nm
- `aod_380nm`: Aerosol optical depth at 380nm
- `forward_scatter`: Forward scattering fraction
- `ground_albedo`: Ground albedo

**Iqbal Method Parameters:**
- `visibility_km`: Visibility (km)
- `ozone_cm`: Ozone layer thickness (cm)
- `ground_albedo`: Ground albedo

### Data Quality Considerations

**Timestep Recommendations:**
- Hourly data is recommended for best accuracy
- Sub-hourly data (15-30 minutes) provides excellent results
- Data with timesteps > 2 hours will generate warnings
- Data with timesteps > 4 hours may cause temperature resets

**Missing Data:**
- Missing values should be coded as -999 or NaN
- The model will substitute defaults and issue warnings
- Default substitutions:
  - Air temperature: 20°C
  - Dewpoint: 10°C
  - Wind speed: 0 m/s
  - Cloud cover: 0

**Data Range Checks:**
- Air temperature: Typically -40°C to 50°C
- Dewpoint: Should be ≤ air temperature
- Wind speed: ≥ 0 m/s
- Cloud cover: 0 to 1

---

## Running the Model

### Basic Configuration

```python
from rtemp import ModelConfiguration

config = ModelConfiguration(
    # Site location (required)
    latitude=47.5,
    longitude=-122.0,
    elevation=100.0,
    timezone=8.0,
    
    # Initial conditions
    initial_water_temp=15.0,
    initial_sediment_temp=15.0,
    
    # Water body characteristics
    water_depth=2.0,
    effective_shade=0.0,
    wind_height=2.0,
    effective_wind_factor=1.0
)
```

### Running the Simulation

```python
from rtemp import RTempModel

# Create model instance
model = RTempModel(config)

# Run simulation
results = model.run(met_data)

# Results is a pandas DataFrame
print(f"Simulation complete: {len(results)} timesteps")
print(f"Final water temperature: {results['water_temp'].iloc[-1]:.2f}°C")
```

### Handling Errors

```python
try:
    results = model.run(met_data)
except ValueError as e:
    print(f"Configuration error: {e}")
except RuntimeError as e:
    print(f"Numerical instability: {e}")
    print("Try using smaller timesteps or resampling your data")
```

### Monitoring Progress

For long simulations, you can monitor progress:

```python
import logging

# Enable logging
logging.basicConfig(level=logging.INFO)

# Run model (will print progress messages)
results = model.run(met_data)
```

---

## Understanding Output

### Output Columns

The results DataFrame contains:

**Timestamps:**
- `datetime`: Timestamp for each calculation

**Temperatures:**
- `water_temp`: Calculated water temperature (°C)
- `sediment_temp`: Calculated sediment temperature (°C)

**Solar Information:**
- `solar_azimuth`: Solar azimuth angle (degrees from north)
- `solar_elevation`: Solar elevation angle (degrees above horizon)
- `solar_radiation`: Solar radiation reaching water surface (W/m²)

**Heat Flux Components (all in W/m²):**
- `longwave_atm`: Incoming atmospheric longwave radiation
- `longwave_back`: Outgoing longwave radiation from water
- `evaporation`: Evaporative heat loss (negative = cooling)
- `convection`: Convective heat exchange (negative = cooling)
- `sediment_flux`: Heat exchange with sediments
- `hyporheic_flux`: Hyporheic exchange flux
- `groundwater_flux`: Groundwater inflow flux
- `net_flux`: Sum of all heat fluxes

### Interpreting Results

**Temperature Trends:**
- Water temperature should follow realistic diurnal patterns
- Typical daily range: 2-5°C for shallow water, less for deep water
- Sediment temperature lags water temperature

**Heat Flux Interpretation:**
- Positive flux = heat gain (warming)
- Negative flux = heat loss (cooling)
- Solar radiation is typically the largest heat source during day
- Evaporation is typically the largest heat sink

**Quality Checks:**
- No NaN or infinite values should appear
- Temperature changes should be gradual
- Heat fluxes should be reasonable (typically < 1000 W/m²)

### Visualizing Results

```python
import matplotlib.pyplot as plt

# Temperature time series
plt.figure(figsize=(12, 6))
plt.plot(results['datetime'], results['water_temp'], label='Water')
plt.plot(results['datetime'], results['sediment_temp'], label='Sediment')
plt.plot(results['datetime'], met_data['air_temp'], label='Air', alpha=0.5)
plt.xlabel('Date/Time')
plt.ylabel('Temperature (°C)')
plt.legend()
plt.title('Temperature Time Series')
plt.grid(True)
plt.tight_layout()
plt.savefig('temperature_timeseries.png')
plt.show()

# Heat flux components
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(results['datetime'], results['solar_radiation'], label='Solar')
ax.plot(results['datetime'], results['longwave_atm'], label='Longwave Atm')
ax.plot(results['datetime'], results['evaporation'], label='Evaporation')
ax.plot(results['datetime'], results['convection'], label='Convection')
ax.plot(results['datetime'], results['net_flux'], label='Net Flux', linewidth=2)
ax.axhline(y=0, color='k', linestyle='--', alpha=0.3)
ax.set_xlabel('Date/Time')
ax.set_ylabel('Heat Flux (W/m²)')
ax.legend()
ax.set_title('Heat Flux Components')
ax.grid(True)
plt.tight_layout()
plt.savefig('heat_flux_components.png')
plt.show()
```

---

## Advanced Usage

### Using Diagnostic Output

Enable detailed diagnostic information:

```python
config = ModelConfiguration(
    latitude=47.5,
    longitude=-122.0,
    elevation=100.0,
    timezone=8.0,
    initial_water_temp=15.0,
    water_depth=2.0,
    enable_diagnostics=True  # Enable diagnostics
)

model = RTempModel(config)
results = model.run(met_data)

# Additional diagnostic columns will be included:
# - solar_potential, solar_after_cloud, solar_after_shade
# - vapor_pressure_water, vapor_pressure_air
# - atmospheric_emissivity
# - wind_speed_2m, wind_speed_7m, wind_function
# - water_temp_change_rate, sediment_temp_change_rate
```

### Time-Varying Parameters

Simulate changing water depth or shade:

```python
# Add time-varying columns to meteorological data
met_data['water_depth_override'] = 2.0  # Start at 2m
met_data.loc[met_data['datetime'] > '2024-06-15', 'water_depth_override'] = 1.5  # Drop to 1.5m

met_data['effective_shade_override'] = 0.0  # Start with no shade
met_data.loc[met_data['datetime'].dt.hour.between(10, 14), 'effective_shade_override'] = 0.3  # 30% shade midday

results = model.run(met_data)
```

### Using Measured Solar Radiation

If you have measured solar radiation data:

```python
# Add measured solar radiation to met_data
met_data['solar_radiation'] = measured_solar_data

# The model will use measured values instead of calculating
results = model.run(met_data)
```

### Batch Processing Multiple Sites

```python
sites = [
    {'name': 'Site A', 'lat': 47.5, 'lon': -122.0, 'elev': 100},
    {'name': 'Site B', 'lat': 48.0, 'lon': -121.5, 'elev': 200},
    {'name': 'Site C', 'lat': 46.5, 'lon': -122.5, 'elev': 50},
]

results_dict = {}

for site in sites:
    config = ModelConfiguration(
        latitude=site['lat'],
        longitude=site['lon'],
        elevation=site['elev'],
        timezone=8.0,
        initial_water_temp=15.0,
        water_depth=2.0
    )
    
    model = RTempModel(config)
    results = model.run(met_data)
    results_dict[site['name']] = results
    
    # Save individual results
    results.to_csv(f"results_{site['name']}.csv", index=False)

print(f"Processed {len(sites)} sites successfully")
```

### Sensitivity Analysis

Test sensitivity to parameters:

```python
import numpy as np

depths = np.arange(0.5, 5.0, 0.5)  # Test depths from 0.5 to 5.0 meters
final_temps = []

for depth in depths:
    config = ModelConfiguration(
        latitude=47.5,
        longitude=-122.0,
        elevation=100.0,
        timezone=8.0,
        initial_water_temp=15.0,
        water_depth=depth
    )
    
    model = RTempModel(config)
    results = model.run(met_data)
    final_temps.append(results['water_temp'].iloc[-1])

# Plot sensitivity
plt.figure(figsize=(8, 6))
plt.plot(depths, final_temps, 'o-')
plt.xlabel('Water Depth (m)')
plt.ylabel('Final Water Temperature (°C)')
plt.title('Sensitivity to Water Depth')
plt.grid(True)
plt.savefig('depth_sensitivity.png')
plt.show()
```

---

## Best Practices

### Data Preparation

1. **Use consistent timesteps**: Hourly or sub-hourly data works best
2. **Check for gaps**: Fill or interpolate missing data before running
3. **Validate ranges**: Ensure all values are physically reasonable
4. **Include metadata**: Document data sources and any preprocessing

### Model Configuration

1. **Start simple**: Use default methods first, then experiment
2. **Match site conditions**: Choose methods appropriate for your location
3. **Calibrate if possible**: Compare to measured water temperatures
4. **Document settings**: Save configuration for reproducibility

### Running Simulations

1. **Test with short periods**: Verify setup with 1-2 days before long runs
2. **Monitor warnings**: Address data quality issues
3. **Check stability**: Ensure no numerical instability errors
4. **Validate output**: Check that results are physically reasonable

### Result Analysis

1. **Plot time series**: Visual inspection catches many issues
2. **Check heat budget**: Net flux should explain temperature changes
3. **Compare to observations**: Validate against measured data if available
4. **Document assumptions**: Note any limitations or uncertainties

### Performance Tips

1. **Resample if needed**: Hourly data is usually sufficient
2. **Use appropriate methods**: Simpler methods run faster
3. **Disable diagnostics**: Only enable when needed for debugging
4. **Process in chunks**: For very long time series, process in segments

### Common Pitfalls to Avoid

1. **Don't ignore warnings**: They indicate data quality issues
2. **Don't use extreme timesteps**: > 4 hours causes problems
3. **Don't skip validation**: Always check input data ranges
4. **Don't over-interpret**: Model is a simplification of reality
5. **Don't forget units**: All inputs must use specified units

---

## Getting Help

### Documentation

- **API Reference**: See `docs/API_REFERENCE.md` for detailed API documentation
- **Configuration Guide**: See `docs/CONFIGURATION_GUIDE.md` for parameter details
- **Method Selection Guide**: See `docs/METHOD_SELECTION_GUIDE.md` for choosing methods
- **Troubleshooting**: See `docs/TROUBLESHOOTING.md` for common issues

### Examples

Check the `examples/` directory for working code examples:
- `basic_usage.py`: Simple example
- `all_methods_demo.py`: All calculation methods
- `diagnostic_output_demo.py`: Using diagnostics
- `time_varying_parameters_demo.py`: Time-varying inputs
- `solar_corrections_demo.py`: Solar radiation corrections

### Support

- **Issues**: Report bugs or request features on GitHub
- **Discussions**: Ask questions in GitHub Discussions
- **Contributing**: See `CONTRIBUTING.md` for contribution guidelines

---

## Next Steps

Now that you understand the basics:

1. Review the [Configuration Guide](CONFIGURATION_GUIDE.md) for detailed parameter descriptions
2. Read the [Method Selection Guide](METHOD_SELECTION_GUIDE.md) to choose appropriate calculation methods
3. Check the [API Reference](API_REFERENCE.md) for complete function documentation
4. Explore the `examples/` directory for more complex use cases
5. Run the model with your own data!



---

## Validation Results

The Python implementation has been rigorously validated against the original VBA rTemp model to ensure accuracy and reliability.

### Validation Methodology

- **Test Period**: October-December 2003 (3 months, 8,828 timesteps)
- **Location**: Washington State (48.45°N, 122.33°W)
- **Timestep**: 15 minutes
- **Comparison**: Direct comparison with VBA model output

### Water Temperature Accuracy

| Metric | Value | Status |
|--------|-------|--------|
| RMSE | 0.13°C | ✅ Excellent |
| Mean Difference | 0.096°C | ✅ Excellent |
| Maximum Difference | 0.39°C | ✅ Acceptable |
| Mean % Error | < 2% | ✅ Excellent |

**Interpretation**: The Python model matches VBA output with exceptional accuracy. The 0.13°C RMSE is well within acceptable limits for water temperature modeling applications.

### Heat Flux Component Accuracy

| Component | RMSE | Mean % Error | Status |
|-----------|------|--------------|--------|
| Solar Radiation | 6.82 W/m² | 2.4% | ✅ Excellent |
| Longwave Atmospheric | 0.13 W/m² | 0.07% | ✅ Excellent |
| Longwave Back | 0.60 W/m² | 0.59% | ✅ Excellent |
| Convection | 0.64 W/m² | - | ✅ Good |
| Evaporation | 0.71 W/m² | - | ✅ Good |
| Sediment Conduction | 5.44 W/m² | - | ✅ Acceptable |

### Solar Position Accuracy

- **Elevation Difference**: 0.02-0.09° (excellent agreement)
- **NOAA Algorithm**: Verified correct implementation
- **Azimuth**: Minor differences due to 360° wrapping (cosmetic only)

### Test Coverage

- **Total Tests**: 346 passing
- **Unit Tests**: All components individually tested
- **Property Tests**: Edge cases and invariants verified
- **Integration Tests**: Full model scenarios validated
- **Validation Tests**: Direct VBA comparison

### Key Improvements

This Python implementation includes several improvements over the original VBA:

1. **Fixed Bras Solar Radiation Formula**
   - Corrected extraterrestrial radiation calculation
   - Fixed molecular scattering coefficient
   - Updated air mass formula

2. **Measured Solar Radiation Support**
   - Automatically uses measured data when available
   - Applies appropriate corrections

3. **Enhanced Validation**
   - Comprehensive input checking
   - Informative warnings for data quality issues
   - Better error messages

4. **Improved Numerical Stability**
   - Better handling of edge cases
   - Stability criteria checking
   - Minimum temperature enforcement

### Confidence Level

**Production-Ready**: The model is suitable for:
- ✅ Water temperature predictions
- ✅ Long-term statistical analysis
- ✅ Regulatory compliance modeling
- ✅ Research applications
- ✅ Educational purposes

### Limitations

While the model shows excellent agreement with VBA:

1. **Maximum Temperature Difference**: 0.39°C occurs on 1 day out of 92 (1% of period)
2. **Edge Cases**: Small differences near sunrise/sunset when sun is very low
3. **Accumulated Differences**: Small errors can accumulate over very long periods

These limitations are acceptable for most water temperature modeling applications.

### References

For detailed validation results, see:
- [Solar Radiation Fix Summary](validation/SOLAR_RADIATION_FIX_SUMMARY.md) - Solar radiation validation
- [Validation Documentation](validation/) - Comprehensive validation results
- `../tests/validation/` - Validation scripts and test data

---

## Comparison with Original VBA Model

### Advantages of Python Implementation

1. **Modern Language**: Python is widely used in scientific computing
2. **Better Testing**: Comprehensive automated test suite
3. **Easier Integration**: Works with pandas, numpy, and other Python tools
4. **Version Control**: Git-friendly text-based code
5. **Cross-Platform**: Runs on Windows, macOS, and Linux
6. **Open Source**: MIT license allows free use and modification
7. **Documentation**: Comprehensive inline and external documentation
8. **Type Hints**: Better code clarity and IDE support

### Maintained Compatibility

- **Same Physics**: Identical heat budget equations
- **Same Methods**: All VBA calculation methods available
- **Same Parameters**: Compatible parameter definitions
- **Validated Results**: Excellent agreement with VBA output

### Migration from VBA

If you're migrating from the VBA version:

1. **Parameter Mapping**: Most parameters have identical names
2. **Input Format**: CSV format similar to VBA
3. **Output Format**: Can export to CSV matching VBA structure
4. **Validation**: Run both models side-by-side to verify results

See the [Developer Guide](DEVELOPER_GUIDE.md) for more details on the implementation.
