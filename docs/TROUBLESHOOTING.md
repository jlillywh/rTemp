# rTemp Troubleshooting Guide

This guide helps you diagnose and resolve common issues when using the rTemp water temperature model.

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Configuration Errors](#configuration-errors)
3. [Data Issues](#data-issues)
4. [Runtime Errors](#runtime-errors)
5. [Output Issues](#output-issues)
6. [Performance Issues](#performance-issues)
7. [Accuracy Issues](#accuracy-issues)
8. [Common Error Messages](#common-error-messages)

---

## Installation Issues

### Problem: pip install fails

**Symptoms:**
```
ERROR: Could not find a version that satisfies the requirement...
```

**Solutions:**

1. **Check Python version:**
```bash
python --version  # Should be 3.8 or higher
```

2. **Upgrade pip:**
```bash
python -m pip install --upgrade pip
```

3. **Install dependencies separately:**
```bash
pip install numpy pandas python-dateutil
pip install -e .
```

4. **Use virtual environment:**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
```

### Problem: Import errors after installation

**Symptoms:**
```python
ImportError: No module named 'rtemp'
```

**Solutions:**

1. **Verify installation:**
```bash
pip list | grep rtemp
```

2. **Check Python path:**
```python
import sys
print(sys.path)
```

3. **Reinstall in development mode:**
```bash
pip uninstall rtemp
pip install -e .
```

4. **Ensure virtual environment is activated:**
```bash
which python  # Should point to .venv/bin/python
```

---

## Configuration Errors

### Problem: ValueError - Water depth must be greater than zero

**Cause:** Water depth is set to zero or negative value.

**Solution:**
```python
config = ModelConfiguration(
    water_depth=1.0,  # Must be > 0
    # ... other parameters
)
```

### Problem: ValueError - Effective shade must be between 0 and 1

**Cause:** Shade value is outside valid range.

**Solution:**
```python
config = ModelConfiguration(
    effective_shade=0.3,  # Must be 0-1 (0% to 100%)
    # ... other parameters
)
```

### Problem: ValueError - Invalid method selection

**Cause:** Method name is misspelled or not recognized.

**Solution:**

Valid method names (case-sensitive):

**Solar methods:**
- "Bras"
- "Bird"
- "Ryan-Stolzenbach"
- "Iqbal"

**Longwave methods:**
- "Brunt"
- "Brutsaert"
- "Satterlund"
- "Idso-Jackson"
- "Swinbank"
- "Koberg"

**Wind function methods:**
- "Brady-Graves-Geyer"
- "Marciano-Harbeck"
- "Ryan-Harleman"
- "East-Mesa"
- "Helfrich"

```python
config = ModelConfiguration(
    solar_method="Bras",  # Correct spelling
    # ... other parameters
)
```

### Problem: Warning - Negative groundwater inflow set to zero

**Cause:** Groundwater inflow is negative.

**Solution:**

This is automatically corrected, but check your input:
```python
config = ModelConfiguration(
    groundwater_inflow=5.0,  # Must be >= 0
    # ... other parameters
)
```

---

## Data Issues

### Problem: Missing required columns in meteorological data

**Symptoms:**
```
KeyError: 'air_temp'
```

**Solution:**

Ensure DataFrame has all required columns:
```python
required_columns = ['datetime', 'air_temp', 'dewpoint', 'wind_speed', 'cloud_cover']

# Check columns
print(met_data.columns.tolist())

# Rename if needed
met_data = met_data.rename(columns={
    'temperature': 'air_temp',
    'dew_point': 'dewpoint',
    'wind': 'wind_speed',
    'clouds': 'cloud_cover'
})
```

### Problem: datetime column not recognized

**Symptoms:**
```
TypeError: Cannot convert datetime column
```

**Solution:**

Ensure datetime column is proper datetime type:
```python
# Convert string to datetime
met_data['datetime'] = pd.to_datetime(met_data['datetime'])

# Or when reading CSV
met_data = pd.read_csv('data.csv', parse_dates=['datetime'])

# Check type
print(met_data['datetime'].dtype)  # Should be datetime64[ns]
```

### Problem: Warning - Missing data substituted with defaults

**Cause:** Data contains missing values (NaN or -999).

**Solution:**

1. **Fill missing values before running:**
```python
# Forward fill
met_data = met_data.fillna(method='ffill')

# Interpolate
met_data = met_data.interpolate(method='linear')

# Fill with specific values
met_data['air_temp'].fillna(20.0, inplace=True)
```

2. **Or accept defaults:**
- Air temperature: 20°C
- Dewpoint: 10°C
- Wind speed: 0 m/s
- Cloud cover: 0

### Problem: Warning - Timestep greater than 2 hours

**Cause:** Time gaps in data are too large.

**Solution:**

1. **Resample to hourly:**
```python
met_data = met_data.set_index('datetime')
met_data = met_data.resample('1H').interpolate()
met_data = met_data.reset_index()
```

2. **Or accept warning** (accuracy may be reduced)

### Problem: Data values out of reasonable range

**Symptoms:**
- Unrealistic temperatures (e.g., 100°C air temp)
- Negative wind speeds
- Cloud cover > 1

**Solution:**

Validate and clean data:
```python
# Check ranges
print(met_data.describe())

# Clip values
met_data['cloud_cover'] = met_data['cloud_cover'].clip(0, 1)
met_data['wind_speed'] = met_data['wind_speed'].clip(0, None)

# Flag suspicious values
suspicious = met_data[
    (met_data['air_temp'] < -40) | 
    (met_data['air_temp'] > 50)
]
print(f"Found {len(suspicious)} suspicious temperature values")
```

---

## Runtime Errors

### Problem: RuntimeError - Numerical instability detected

**Symptoms:**
```
RuntimeError: Temperature change of 12.5°C exceeds stability criteria of 5.0°C
```

**Causes:**
- Timestep too large
- Extreme meteorological conditions
- Very shallow water
- Configuration issues

**Solutions:**

1. **Reduce timestep:**
```python
# Resample to smaller timestep
met_data = met_data.set_index('datetime')
met_data = met_data.resample('30min').interpolate()
met_data = met_data.reset_index()
```

2. **Increase stability criteria** (use with caution):
```python
config = ModelConfiguration(
    stability_criteria=10.0,  # Default is 5.0
    # ... other parameters
)
```

3. **Check for data issues:**
```python
# Look for sudden jumps
met_data['air_temp_diff'] = met_data['air_temp'].diff()
print(met_data[met_data['air_temp_diff'].abs() > 10])
```

4. **Increase water depth:**
```python
config = ModelConfiguration(
    water_depth=1.0,  # Deeper water is more stable
    # ... other parameters
)
```

### Problem: Model runs very slowly

**Causes:**
- Very long time series
- Diagnostic output enabled
- Complex methods

**Solutions:**

1. **Disable diagnostics:**
```python
config = ModelConfiguration(
    enable_diagnostics=False,  # Faster
    # ... other parameters
)
```

2. **Use simpler methods:**
```python
config = ModelConfiguration(
    solar_method="Bras",  # Faster than Bird
    # ... other parameters
)
```

3. **Process in chunks:**
```python
chunk_size = 1000  # rows
results_list = []

for i in range(0, len(met_data), chunk_size):
    chunk = met_data.iloc[i:i+chunk_size]
    
    # Update initial conditions from previous chunk
    if i > 0:
        config.initial_water_temp = results_list[-1]['water_temp'].iloc[-1]
        config.initial_sediment_temp = results_list[-1]['sediment_temp'].iloc[-1]
    
    model = RTempModel(config)
    results = model.run(chunk)
    results_list.append(results)

final_results = pd.concat(results_list, ignore_index=True)
```

### Problem: Memory error with large datasets

**Symptoms:**
```
MemoryError: Unable to allocate array
```

**Solutions:**

1. **Process in chunks** (see above)

2. **Reduce data frequency:**
```python
# Use hourly instead of sub-hourly
met_data = met_data.set_index('datetime')
met_data = met_data.resample('1H').mean()
met_data = met_data.reset_index()
```

3. **Disable diagnostics:**
```python
config = ModelConfiguration(
    enable_diagnostics=False,
    # ... other parameters
)
```

---

## Output Issues

### Problem: NaN values in output

**Causes:**
- Division by zero
- Invalid input data
- Numerical issues

**Solutions:**

1. **Check input data:**
```python
# Find NaN in inputs
print(met_data.isnull().sum())

# Fill NaN before running
met_data = met_data.fillna(method='ffill')
```

2. **Check for zero depth:**
```python
if 'water_depth_override' in met_data.columns:
    print(met_data[met_data['water_depth_override'] <= 0])
```

3. **Enable diagnostics to identify issue:**
```python
config = ModelConfiguration(
    enable_diagnostics=True,
    # ... other parameters
)
```

### Problem: Unrealistic temperature values

**Symptoms:**
- Water temperature > 40°C
- Water temperature < 0°C (when not expected)
- Constant temperature (no variation)

**Solutions:**

1. **Check input data quality:**
```python
# Plot inputs
import matplotlib.pyplot as plt

fig, axes = plt.subplots(4, 1, figsize=(12, 10))
met_data.plot(x='datetime', y='air_temp', ax=axes[0])
met_data.plot(x='datetime', y='dewpoint', ax=axes[1])
met_data.plot(x='datetime', y='wind_speed', ax=axes[2])
met_data.plot(x='datetime', y='cloud_cover', ax=axes[3])
plt.tight_layout()
plt.show()
```

2. **Check configuration:**
```python
# Verify parameters are reasonable
print(f"Water depth: {config.water_depth} m")
print(f"Shade: {config.effective_shade}")
print(f"Wind factor: {config.effective_wind_factor}")
```

3. **Compare heat flux components:**
```python
# Plot heat fluxes
results[['solar_radiation', 'longwave_atm', 'evaporation', 
         'convection', 'net_flux']].plot(figsize=(12, 6))
plt.axhline(y=0, color='k', linestyle='--')
plt.ylabel('Heat Flux (W/m²)')
plt.show()
```

4. **Check for configuration issues:**
```python
# Very shallow water can cause extreme temperatures
if config.water_depth < 0.1:
    print("Warning: Very shallow water may cause extreme temperatures")

# Full shade prevents solar heating
if config.effective_shade > 0.9:
    print("Warning: High shade may prevent warming")
```

### Problem: Output file is very large

**Cause:** Diagnostic output enabled with long time series.

**Solutions:**

1. **Disable diagnostics:**
```python
config = ModelConfiguration(
    enable_diagnostics=False,
    # ... other parameters
)
```

2. **Save only essential columns:**
```python
essential_cols = ['datetime', 'water_temp', 'sediment_temp', 
                  'solar_radiation', 'net_flux']
results[essential_cols].to_csv('output.csv', index=False)
```

3. **Compress output:**
```python
results.to_csv('output.csv.gz', index=False, compression='gzip')
```

---

## Performance Issues

### Problem: Model takes too long to run

**Solutions:**

1. **Profile to find bottleneck:**
```python
import time

start = time.time()
results = model.run(met_data)
end = time.time()

print(f"Runtime: {end - start:.2f} seconds")
print(f"Timesteps: {len(met_data)}")
print(f"Time per timestep: {(end - start) / len(met_data) * 1000:.2f} ms")
```

2. **Optimize data frequency:**
```python
# Hourly is usually sufficient
met_data = met_data.set_index('datetime')
met_data = met_data.resample('1H').mean()
met_data = met_data.reset_index()
```

3. **Use simpler methods:**
```python
config = ModelConfiguration(
    solar_method="Bras",  # Faster than Bird
    longwave_method="Brunt",  # Faster than complex methods
    # ... other parameters
)
```

### Problem: High memory usage

**Solutions:**

1. **Process in chunks** (see Runtime Errors section)

2. **Use appropriate data types:**
```python
# Convert to float32 instead of float64
for col in ['air_temp', 'dewpoint', 'wind_speed', 'cloud_cover']:
    met_data[col] = met_data[col].astype('float32')
```

3. **Delete intermediate results:**
```python
import gc

# After processing each chunk
results_list.append(results.copy())
del results
gc.collect()
```

---

## Accuracy Issues

### Problem: Model predictions don't match observations

**Causes:**
- Incorrect configuration
- Poor method selection
- Data quality issues
- Site-specific factors not captured

**Diagnostic Steps:**

1. **Compare time series:**
```python
import matplotlib.pyplot as plt

plt.figure(figsize=(12, 6))
plt.plot(results['datetime'], results['water_temp'], label='Modeled')
plt.plot(observed['datetime'], observed['water_temp'], label='Observed')
plt.xlabel('Date/Time')
plt.ylabel('Water Temperature (°C)')
plt.legend()
plt.grid(True)
plt.show()
```

2. **Calculate error metrics:**
```python
import numpy as np

# Merge modeled and observed
comparison = pd.merge(results, observed, on='datetime', suffixes=('_mod', '_obs'))

# Calculate metrics
me = np.mean(comparison['water_temp_mod'] - comparison['water_temp_obs'])
mae = np.mean(np.abs(comparison['water_temp_mod'] - comparison['water_temp_obs']))
rmse = np.sqrt(np.mean((comparison['water_temp_mod'] - comparison['water_temp_obs'])**2))

print(f"Mean Error: {me:.2f}°C")
print(f"Mean Absolute Error: {mae:.2f}°C")
print(f"Root Mean Square Error: {rmse:.2f}°C")
```

3. **Check systematic bias:**
```python
# Scatter plot
plt.figure(figsize=(8, 8))
plt.scatter(comparison['water_temp_obs'], comparison['water_temp_mod'], alpha=0.5)
plt.plot([0, 40], [0, 40], 'r--', label='1:1 line')
plt.xlabel('Observed Temperature (°C)')
plt.ylabel('Modeled Temperature (°C)')
plt.legend()
plt.grid(True)
plt.show()

# If points are above line: model too warm
# If points are below line: model too cool
```

**Solutions:**

1. **Adjust atmospheric turbidity:**
```python
# If model too warm during day:
config.atmospheric_turbidity = 3.0  # Increase (more attenuation)

# If model too cool during day:
config.atmospheric_turbidity = 1.5  # Decrease (less attenuation)
```

2. **Adjust wind factor:**
```python
# If model too warm (not enough cooling):
config.effective_wind_factor = 1.0  # Increase wind effect

# If model too cool (too much cooling):
config.effective_wind_factor = 0.5  # Decrease wind effect
```

3. **Try different methods:**
```python
# Try different solar method
config.solar_method = "Iqbal"  # Instead of Bras

# Try different longwave method
config.longwave_method = "Brutsaert"  # Instead of Brunt

# Try different wind function
config.wind_function_method = "Ryan-Harleman"  # Instead of Brady-Graves-Geyer
```

4. **Check for missing processes:**
```python
# Add groundwater if present
config.groundwater_inflow = 5.0  # cm/day
config.groundwater_temperature = 10.0  # °C

# Add hyporheic exchange
config.hyporheic_exchange_rate = 10.0  # cm/day
```

### Problem: Diurnal range too large or too small

**Too Large (model swings more than observations):**

Solutions:
- Increase water depth
- Increase sediment thermal mass
- Check if shade is too low
- Reduce atmospheric turbidity

```python
config.water_depth = 2.0  # Increase from 1.0
config.sediment_thermal_conductivity = 2.0  # Increase
```

**Too Small (model doesn't vary enough):**

Solutions:
- Decrease water depth
- Check if shade is too high
- Increase atmospheric turbidity
- Check wind factor

```python
config.water_depth = 0.5  # Decrease from 1.0
config.effective_shade = 0.1  # Decrease from 0.5
```

---

## Common Error Messages

### "Water depth must be greater than zero"

**Fix:**
```python
config.water_depth = 1.0  # Must be > 0
```

### "Effective shade must be between 0 and 1"

**Fix:**
```python
config.effective_shade = 0.3  # Must be 0-1
```

### "Wind height must be greater than zero"

**Fix:**
```python
config.wind_height = 2.0  # Must be > 0
```

### "Invalid solar method: 'bras'"

**Fix:**
```python
config.solar_method = "Bras"  # Capital B
```

### "Required column 'air_temp' not found"

**Fix:**
```python
# Rename column
met_data = met_data.rename(columns={'temperature': 'air_temp'})
```

### "Temperature change exceeds stability criteria"

**Fix:**
```python
# Reduce timestep or increase criteria
config.stability_criteria = 10.0
```

### "Cannot convert datetime column"

**Fix:**
```python
met_data['datetime'] = pd.to_datetime(met_data['datetime'])
```

---

## Getting Additional Help

### Enable Logging

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Run model - will print detailed messages
results = model.run(met_data)
```

### Enable Diagnostics

```python
config = ModelConfiguration(
    enable_diagnostics=True,
    # ... other parameters
)

results = model.run(met_data)

# Examine diagnostic columns
diagnostic_cols = [col for col in results.columns if col not in 
                   ['datetime', 'water_temp', 'sediment_temp']]
print(results[diagnostic_cols].describe())
```

### Create Minimal Reproducible Example

When reporting issues:

```python
import pandas as pd
from rtemp import RTempModel, ModelConfiguration

# Minimal configuration
config = ModelConfiguration(
    latitude=47.5,
    longitude=-122.0,
    elevation=100.0,
    timezone=8.0,
    initial_water_temp=15.0,
    water_depth=1.0
)

# Minimal data
met_data = pd.DataFrame({
    'datetime': pd.date_range('2024-06-01', periods=24, freq='1H'),
    'air_temp': 20.0,
    'dewpoint': 12.0,
    'wind_speed': 2.0,
    'cloud_cover': 0.3
})

# Run and report error
try:
    model = RTempModel(config)
    results = model.run(met_data)
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
```

### Check Documentation

- **API Reference**: `docs/API_REFERENCE.md`
- **User Guide**: `docs/USER_GUIDE.md`
- **Configuration Guide**: `docs/CONFIGURATION_GUIDE.md`
- **Method Selection**: `docs/METHOD_SELECTION_GUIDE.md`

### Report Issues

If you've tried the solutions above and still have issues:

1. Check existing GitHub issues
2. Create a new issue with:
   - Error message (full traceback)
   - Minimal reproducible example
   - Python version and package versions
   - Operating system
   - What you've already tried

---

## Prevention Tips

1. **Validate data before running:**
```python
# Check for required columns
required = ['datetime', 'air_temp', 'dewpoint', 'wind_speed', 'cloud_cover']
missing = [col for col in required if col not in met_data.columns]
if missing:
    print(f"Missing columns: {missing}")

# Check for missing values
print(met_data.isnull().sum())

# Check data ranges
print(met_data.describe())
```

2. **Start simple:**
```python
# Use defaults first
config = ModelConfiguration(
    latitude=47.5,
    longitude=-122.0,
    elevation=100.0,
    timezone=8.0,
    initial_water_temp=15.0,
    water_depth=1.0
)
```

3. **Test with short period:**
```python
# Test with 1-2 days first
test_data = met_data.iloc[:48]  # First 48 hours
results = model.run(test_data)
```

4. **Enable diagnostics for debugging:**
```python
config.enable_diagnostics = True
```

5. **Save configuration:**
```python
import json

config_dict = {
    'latitude': config.latitude,
    'longitude': config.longitude,
    # ... all parameters
}

with open('model_config.json', 'w') as f:
    json.dump(config_dict, f, indent=2)
```

