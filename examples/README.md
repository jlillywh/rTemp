# rTemp Example Scripts

This directory contains example scripts demonstrating various features and capabilities of the rTemp water temperature model.

## Available Examples

### 1. basic_usage.py
**Purpose**: Simple introduction to the rTemp model with default parameters

**What it demonstrates**:
- Basic model configuration
- Creating sample meteorological data
- Running the model
- Viewing and exporting results

**Run it**:
```bash
python examples/basic_usage.py
```

**Output**: 
- Console summary of results
- CSV file: `rtemp_basic_output.csv`

---

### 2. all_methods_demo.py
**Purpose**: Compare all available calculation methods

**What it demonstrates**:
- All 4 solar radiation methods (Bras, Bird, Ryan-Stolzenbach, Iqbal)
- All 6 longwave radiation methods (Brunt, Brutsaert, Satterlund, Idso-Jackson, Swinbank, Koberg)
- All 5 wind function methods (Brady-Graves-Geyer, Marciano-Harbeck, Ryan-Harleman, East Mesa, Helfrich)
- Side-by-side comparison of results

**Run it**:
```bash
python examples/all_methods_demo.py
```

**Output**: 
- Console comparison tables showing differences between methods
- Helps you choose the most appropriate methods for your application

---

### 3. diagnostic_output_demo.py
**Purpose**: Enable and use diagnostic output for detailed analysis

**What it demonstrates**:
- Enabling diagnostic output
- Accessing intermediate calculations
- Analyzing vapor pressure, emissivity, wind adjustments
- Understanding temperature change rates
- Detailed timestep-by-timestep analysis

**Run it**:
```bash
python examples/diagnostic_output_demo.py
```

**Output**: 
- Console diagnostic analysis
- CSV file: `rtemp_diagnostic_output.csv` (includes all diagnostic fields)

**Use this when**:
- Debugging model behavior
- Understanding why temperatures change
- Validating calculations
- Comparing with other models

---

### 4. time_varying_parameters_demo.py
**Purpose**: Demonstrate time-varying water depth and shade

**What it demonstrates**:
- Time-varying water depth (simulating tidal influence)
- Time-varying effective shade (simulating cloud shadows or vegetation)
- Combined time-varying parameters
- Impact on temperature and solar radiation

**Run it**:
```bash
python examples/time_varying_parameters_demo.py
```

**Output**: 
- Console analysis of time-varying effects
- CSV files:
  - `rtemp_varying_depth_output.csv`
  - `rtemp_varying_shade_output.csv`
  - `rtemp_combined_varying_output.csv`

**Use this when**:
- Modeling tidal systems
- Accounting for riparian vegetation
- Simulating regulated flows
- Modeling dynamic shade conditions

---

### 5. solar_corrections_demo.py
**Purpose**: Demonstrate solar radiation corrections

**What it demonstrates**:
- Cloud cover correction
- Shade correction
- Anderson albedo calculation
- Combined corrections
- Effect of solar elevation on albedo

**Run it**:
```bash
python examples/solar_corrections_demo.py
```

**Output**: 
- Console demonstration of correction effects
- Shows how each correction reduces solar radiation

---

## Quick Start Guide

### Minimal Example

```python
from datetime import datetime, timedelta
import pandas as pd
from rtemp import ModelConfiguration, RTempModel

# Configure the model
config = ModelConfiguration(
    latitude=47.5,
    longitude=-122.0,
    elevation=100.0,
    timezone=8.0,
    daylight_savings=0,
    initial_water_temp=15.0,
    initial_sediment_temp=15.0,
    minimum_temperature=0.0,
    water_depth=2.0,
    effective_shade=0.0,
    wind_height=2.0,
    effective_wind_factor=1.0,
    solar_method="Bras",
    longwave_method="Brunt",
    wind_function_method="Brady-Graves-Geyer",
)

# Create meteorological data
met_data = pd.DataFrame({
    'datetime': [datetime(2024, 7, 15, 12, 0)],
    'air_temperature': [25.0],
    'dewpoint_temperature': [15.0],
    'wind_speed': [3.0],
    'cloud_cover': [0.3],
})

# Run the model
model = RTempModel(config)
results = model.run(met_data)

# View results
print(results[['datetime', 'water_temperature', 'solar_radiation']])

# Export results
model.export_results('output.csv')
```

## Input Data Requirements

All examples require meteorological data with these columns:

**Required**:
- `datetime`: Timestamp (datetime object)
- `air_temperature`: Air temperature (°C)
- `dewpoint_temperature`: Dewpoint temperature (°C)
- `wind_speed`: Wind speed (m/s)
- `cloud_cover`: Cloud cover fraction (0-1)

**Optional** (for specific methods):
- `pressure_mb`: Atmospheric pressure (millibars) - for Bird/Iqbal
- `ozone_cm`: Ozone layer thickness (cm-atm) - for Bird/Iqbal
- `water_vapor_cm`: Precipitable water (cm) - for Bird
- `visibility_km`: Visibility (km) - for Iqbal
- `water_depth_override`: Time-varying water depth (m)
- `effective_shade_override`: Time-varying shade (0-1)

## Method Selection Guide

### Solar Radiation Methods

- **Bras**: Simple, requires only turbidity factor. Good for general use.
- **Bird**: Detailed, requires aerosol and atmospheric composition data. Best for clear-sky conditions.
- **Ryan-Stolzenbach**: Medium complexity, good for water bodies with elevation effects.
- **Iqbal**: Very detailed, requires visibility and atmospheric data. Most comprehensive.

### Longwave Radiation Methods

- **Brunt**: Classic method, simple vapor pressure relationship.
- **Brutsaert**: Improved Brunt with configurable coefficient.
- **Satterlund**: Exponential formula, good for humid conditions.
- **Idso-Jackson**: Temperature-only method, simplest.
- **Swinbank**: Temperature-based, good for clear skies.
- **Koberg**: Includes clearness factor, comprehensive.

### Wind Function Methods

- **Brady-Graves-Geyer**: General purpose, widely used.
- **Marciano-Harbeck**: Calibrated for Lake Hefner, large lakes.
- **Ryan-Harleman**: Uses virtual temperature, good for rivers.
- **East Mesa**: Modified virtual temperature approach.
- **Helfrich**: Recalibrated Ryan-Harleman, improved accuracy.

## Tips for Using Examples

1. **Start with basic_usage.py** to understand the workflow
2. **Use all_methods_demo.py** to choose appropriate methods for your site
3. **Enable diagnostics** when debugging or validating results
4. **Use time-varying parameters** for realistic scenarios
5. **Adjust timesteps** based on your data availability (hourly recommended)

## Common Issues

### Stability Warnings
If you see stability warnings, try:
- Reducing timestep (use hourly or sub-hourly data)
- Checking for unrealistic input data
- Adjusting `stability_criteria` parameter

### Missing Data
The model will:
- Issue warnings for missing data
- Substitute default values
- Continue execution

### Sediment Warnings
If sediment thermal properties are zero:
- Model assumes sediment properties equal to water
- This is acceptable for shallow water bodies
- Specify actual values for better accuracy in deep water

## Further Information

- See `../README.md` for full model documentation
- See `../.kiro/specs/rtemp-python-complete/` for detailed specifications
- See `../tests/` for test examples and validation

## Contributing

To add new examples:
1. Follow the existing example structure
2. Include clear comments and docstrings
3. Demonstrate a specific feature or use case
4. Update this README with your example
