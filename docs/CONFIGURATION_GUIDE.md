# rTemp Configuration Guide

This guide provides detailed information about all configuration parameters in the rTemp water temperature model.

## Table of Contents

1. [Overview](#overview)
2. [Site Parameters](#site-parameters)
3. [Initial Conditions](#initial-conditions)
4. [Water Body Parameters](#water-body-parameters)
5. [Sediment Parameters](#sediment-parameters)
6. [Groundwater Parameters](#groundwater-parameters)
7. [Method Selections](#method-selections)
8. [Model Parameters](#model-parameters)
9. [Output Options](#output-options)
10. [Configuration Examples](#configuration-examples)

---

## Overview

The `ModelConfiguration` dataclass contains all parameters needed to run the rTemp model. Parameters are organized into logical groups based on their purpose.

```python
from rtemp import ModelConfiguration

config = ModelConfiguration(
    # ... parameters ...
)
```

---

## Site Parameters

These parameters define the geographic location and timezone of your site.

### latitude

**Type:** float  
**Units:** Decimal degrees  
**Range:** -90 to 90  
**Required:** Yes

Latitude of the site in decimal degrees. Positive values are north of the equator, negative values are south.

**Examples:**
- Seattle, WA: 47.6
- Miami, FL: 25.8
- Sydney, Australia: -33.9

**Notes:**
- Used for solar position calculations
- Affects photoperiod and solar radiation intensity
- Extreme latitudes (> 89.8°) are automatically clamped

### longitude

**Type:** float  
**Units:** Decimal degrees  
**Range:** -180 to 180  
**Required:** Yes

Longitude of the site in decimal degrees. Positive values are east of the Prime Meridian, negative values are west.

**Examples:**
- Seattle, WA: -122.3
- Miami, FL: -80.2
- Sydney, Australia: 151.2

**Notes:**
- Used for solar position calculations
- Affects local solar time
- Western hemisphere uses negative values

### elevation

**Type:** float  
**Units:** Meters above sea level  
**Range:** -500 to 9000  
**Required:** Yes

Elevation of the site above mean sea level.

**Examples:**
- Sea level: 0
- Denver, CO: 1609
- Death Valley, CA: -86

**Notes:**
- Affects atmospheric pressure calculations
- Influences solar radiation (less atmosphere at higher elevations)
- Used in Ryan-Stolzenbach solar radiation model

### timezone

**Type:** float  
**Units:** Hours from UTC  
**Range:** -12 to 14  
**Required:** Yes

Time zone offset from UTC in hours. Positive values for time zones west of UTC.

**Examples:**
- Pacific Standard Time (PST): 8.0
- Eastern Standard Time (EST): 5.0
- Central European Time (CET): -1.0
- Australian Eastern Standard Time (AEST): -10.0

**Notes:**
- Used for solar position calculations
- Does NOT automatically adjust for daylight savings
- Use positive values for western hemisphere

### daylight_savings

**Type:** int  
**Units:** Hours  
**Range:** 0 or 1  
**Default:** 0

Daylight savings time offset in hours.

**Values:**
- 0: Standard time
- 1: Daylight savings time (add 1 hour)

**Notes:**
- Set to 1 during daylight savings periods
- Set to 0 during standard time periods
- You may need to change this value seasonally

---

## Initial Conditions

These parameters set the starting temperatures for the simulation.

### initial_water_temp

**Type:** float  
**Units:** °C  
**Range:** -5 to 50  
**Default:** 15.0

Initial water temperature at the start of the simulation.

**Recommendations:**
- Use measured water temperature if available
- Otherwise, estimate from recent air temperatures
- For cold climates in winter: 0-5°C
- For temperate climates: 10-20°C
- For warm climates in summer: 20-30°C

**Notes:**
- Model will equilibrate after initial spin-up period
- First 1-2 days may show adjustment from initial condition
- Consider running a spin-up period and discarding early results

### initial_sediment_temp

**Type:** float  
**Units:** °C  
**Range:** -5 to 50  
**Default:** 15.0

Initial sediment temperature at the start of the simulation.

**Recommendations:**
- Often set equal to initial water temperature
- Can be set slightly cooler in spring (sediment lags warming)
- Can be set slightly warmer in fall (sediment lags cooling)

**Notes:**
- Sediment temperature affects heat exchange with water
- Less critical than water temperature for most applications
- Model will equilibrate sediment temperature over time

### minimum_temperature

**Type:** float  
**Units:** °C  
**Range:** -5 to 10  
**Default:** 0.0

Minimum allowed water and sediment temperature.

**Recommendations:**
- Use 0.0°C for most applications (freezing point)
- Can use slightly negative values for saline water
- Use higher values if ice formation is not modeled

**Notes:**
- Prevents unrealistic sub-freezing temperatures
- Model does not simulate ice formation
- Temperatures are clamped to this minimum after each timestep

---

## Water Body Parameters

These parameters describe the physical characteristics of the water body.

### water_depth

**Type:** float  
**Units:** Meters  
**Range:** 0.01 to 1000  
**Default:** 1.0

Mean water depth of the water body.

**Typical Values:**
- Shallow stream: 0.1-0.5 m
- Small river: 0.5-2 m
- Large river: 2-10 m
- Shallow lake: 1-5 m
- Deep lake: 5-100 m

**Notes:**
- Deeper water has more thermal inertia (slower temperature changes)
- Can be time-varying using `water_depth_override` in met data
- Must be > 0 (validation error if ≤ 0)

### effective_shade

**Type:** float  
**Units:** Fraction  
**Range:** 0 to 1  
**Default:** 0.0

Fraction of water surface shaded from direct solar radiation.

**Values:**
- 0.0: No shade (fully exposed)
- 0.5: 50% shaded
- 1.0: Fully shaded

**Examples:**
- Open water: 0.0-0.1
- Partially vegetated stream: 0.2-0.5
- Heavily vegetated stream: 0.5-0.9
- Completely covered: 0.9-1.0

**Notes:**
- Reduces solar radiation proportionally
- Can be time-varying using `effective_shade_override` in met data
- Accounts for riparian vegetation, structures, etc.
- Does not affect longwave radiation

### wind_height

**Type:** float  
**Units:** Meters  
**Range:** 0.1 to 100  
**Default:** 2.0

Height above water surface where wind speed is measured.

**Standard Heights:**
- 2 meters: Standard meteorological height
- 7 meters: Some wind function methods use this
- 10 meters: Common for weather stations

**Notes:**
- Wind speed is adjusted to appropriate height for each wind function
- Most wind functions use 2m or 7m height
- Adjustment uses exponential profile with exponent 0.15

### effective_wind_factor

**Type:** float  
**Units:** Fraction  
**Range:** 0 to 1  
**Default:** 1.0

Factor to reduce wind speed for sheltered locations.

**Values:**
- 1.0: Fully exposed (no shelter)
- 0.7-0.9: Partially sheltered
- 0.3-0.7: Sheltered
- 0.1-0.3: Highly sheltered

**Examples:**
- Open lake: 1.0
- River with low banks: 0.8-0.9
- River with high banks: 0.5-0.7
- Stream in forest: 0.2-0.4

**Notes:**
- Accounts for topographic sheltering
- Multiplies wind speed after height adjustment
- Affects evaporation and convection

---

## Sediment Parameters

These parameters control heat exchange with sediments.

### sediment_thermal_conductivity

**Type:** float  
**Units:** W/m/°C  
**Range:** 0 to 10  
**Default:** 1.0

Thermal conductivity of sediment material.

**Typical Values:**
- Water: 0.6
- Organic sediment: 0.5-1.0
- Sand: 1.5-2.5
- Gravel: 2.0-3.0
- Clay: 1.0-1.5
- Rock: 2.0-7.0

**Notes:**
- Higher values = more heat transfer
- Use 0 to disable sediment conduction
- Negative values are set to 0 with warning

### sediment_thermal_diffusivity

**Type:** float  
**Units:** cm²/s  
**Range:** 0.001 to 0.1  
**Default:** 0.005

Thermal diffusivity of sediment material.

**Typical Values:**
- Water: 0.0014
- Organic sediment: 0.002-0.005
- Sand: 0.005-0.010
- Gravel: 0.008-0.015
- Clay: 0.003-0.006
- Rock: 0.010-0.030

**Notes:**
- Controls rate of temperature change in sediment
- Related to conductivity, density, and specific heat
- Zero or negative values trigger warning and use water properties

### sediment_thickness

**Type:** float  
**Units:** Centimeters  
**Range:** 1 to 1000  
**Default:** 10.0

Thickness of active sediment layer for heat exchange.

**Typical Values:**
- Shallow interaction: 5-10 cm
- Moderate interaction: 10-30 cm
- Deep interaction: 30-100 cm

**Notes:**
- Represents depth of sediment that exchanges heat with water
- Thicker layer = more thermal mass
- Zero or negative values are set to 10 cm with warning

### hyporheic_exchange_rate

**Type:** float  
**Units:** cm/day  
**Range:** 0 to 1000  
**Default:** 0.0

Rate of hyporheic exchange (water flowing through sediments).

**Typical Values:**
- No exchange: 0
- Low exchange: 1-10 cm/day
- Moderate exchange: 10-50 cm/day
- High exchange: 50-200 cm/day

**Notes:**
- Represents water cycling through streambed
- Affects heat exchange between water and sediment
- Set to 0 to disable hyporheic exchange
- Negative values are set to 0 with warning

---

## Groundwater Parameters

These parameters control groundwater inflow effects.

### groundwater_temperature

**Type:** float  
**Units:** °C  
**Range:** 0 to 30  
**Default:** 10.0

Temperature of groundwater entering the water body.

**Typical Values:**
- Cold springs: 5-10°C
- Temperate groundwater: 10-15°C
- Warm groundwater: 15-20°C

**Notes:**
- Groundwater temperature is typically stable year-round
- Often close to mean annual air temperature
- Can be measured or estimated from regional data
- Must be ≥ 0 (validation error if negative)

### groundwater_inflow

**Type:** float  
**Units:** cm/day  
**Range:** 0 to 1000  
**Default:** 0.0

Rate of groundwater inflow per unit surface area.

**Typical Values:**
- No inflow: 0
- Low inflow: 0.1-1 cm/day
- Moderate inflow: 1-10 cm/day
- High inflow: 10-100 cm/day

**Notes:**
- Represents groundwater entering from below or sides
- Affects heat budget if groundwater temp differs from water temp
- Set to 0 to disable groundwater flux
- Negative values are set to 0 with warning

---

## Method Selections

These parameters select which calculation methods to use.

### solar_method

**Type:** str  
**Options:** "Bras", "Bird", "Ryan-Stolzenbach", "Iqbal"  
**Default:** "Bras"

Solar radiation calculation method.

**Methods:**

**"Bras"** (Default)
- Simple atmospheric attenuation model
- Requires: turbidity factor
- Best for: General use, limited data
- Accuracy: Good for clear skies

**"Bird"** (Bird-Hulstrom)
- Detailed clear-sky model
- Requires: pressure, ozone, water vapor, aerosol optical depths
- Best for: High accuracy, detailed atmospheric data available
- Accuracy: Excellent for clear skies

**"Ryan-Stolzenbach"**
- Simplified model with elevation correction
- Requires: atmospheric transmission coefficient
- Best for: Quick estimates, limited data
- Accuracy: Moderate

**"Iqbal"**
- Comprehensive atmospheric transmittance model
- Requires: pressure, ozone, visibility
- Best for: Good accuracy with moderate data requirements
- Accuracy: Very good

**Selection Guide:**
- Use "Bras" for most applications
- Use "Bird" if you have detailed atmospheric data
- Use "Ryan-Stolzenbach" for quick estimates
- Use "Iqbal" for balance of accuracy and data requirements

### longwave_method

**Type:** str  
**Options:** "Brunt", "Brutsaert", "Satterlund", "Idso-Jackson", "Swinbank", "Koberg"  
**Default:** "Brunt"

Longwave atmospheric radiation emissivity method.

**Methods:**

**"Brunt"** (Default)
- Classic empirical formula
- Requires: air temp, vapor pressure
- Best for: General use
- Accuracy: Good

**"Brutsaert"**
- Physically-based formula
- Requires: air temp, vapor pressure, coefficient
- Best for: Humid climates
- Accuracy: Very good

**"Satterlund"**
- Exponential formula
- Requires: air temp, dewpoint
- Best for: Wide range of conditions
- Accuracy: Good

**"Idso-Jackson"**
- Temperature-only formula
- Requires: air temp only
- Best for: Limited data
- Accuracy: Moderate

**"Swinbank"**
- Simple temperature formula
- Requires: air temp only
- Best for: Quick estimates
- Accuracy: Moderate

**"Koberg"**
- Interpolation-based method
- Requires: air temp, clearness
- Best for: Specific conditions
- Accuracy: Good

**Selection Guide:**
- Use "Brunt" for most applications
- Use "Brutsaert" for humid climates
- Use "Satterlund" for variable conditions
- Use "Idso-Jackson" or "Swinbank" if only air temp available

### wind_function_method

**Type:** str  
**Options:** "Brady-Graves-Geyer", "Marciano-Harbeck", "Ryan-Harleman", "East-Mesa", "Helfrich"  
**Default:** "Brady-Graves-Geyer"

Wind function for evaporation and convection calculations.

**Methods:**

**"Brady-Graves-Geyer"** (Default)
- General purpose formula
- Wind at 7m height
- Best for: Most water bodies
- Accuracy: Good

**"Marciano-Harbeck"**
- Lake Hefner formula
- Wind at 7m height
- Best for: Large lakes
- Accuracy: Good for lakes

**"Ryan-Harleman"**
- Virtual temperature correction
- Wind at 2m height
- Best for: Rivers and streams
- Accuracy: Very good

**"East-Mesa"**
- Modified formula
- Combines temperature and wind effects
- Best for: Specific applications
- Accuracy: Good

**"Helfrich"**
- Recalibrated Ryan-Harleman
- Wind at 2m height
- Best for: Rivers and streams
- Accuracy: Very good

**Selection Guide:**
- Use "Brady-Graves-Geyer" for most applications
- Use "Marciano-Harbeck" for large lakes
- Use "Ryan-Harleman" or "Helfrich" for rivers/streams
- Use "East-Mesa" for specific calibrated applications

---

## Model Parameters

These parameters control model behavior and corrections.

### atmospheric_turbidity

**Type:** float  
**Units:** Dimensionless  
**Range:** 1 to 10  
**Default:** 2.0

Atmospheric turbidity factor for Bras solar radiation method.

**Typical Values:**
- Very clear: 1.5-2.0
- Clear: 2.0-3.0
- Moderate: 3.0-4.0
- Hazy: 4.0-5.0
- Very hazy: 5.0-10.0

**Notes:**
- Only used with Bras solar method
- Higher values = more atmospheric attenuation
- Varies with air quality, humidity, aerosols

### atmospheric_transmission_coeff

**Type:** float  
**Units:** Dimensionless  
**Range:** 0.5 to 1.0  
**Default:** 0.8

Atmospheric transmission coefficient for Ryan-Stolzenbach solar method.

**Typical Values:**
- Very clear: 0.85-0.91
- Clear: 0.80-0.85
- Moderate: 0.75-0.80
- Hazy: 0.70-0.75

**Notes:**
- Only used with Ryan-Stolzenbach solar method
- Represents fraction of extraterrestrial radiation reaching surface
- Adjusted for elevation automatically

### brutsaert_coefficient

**Type:** float  
**Units:** Dimensionless  
**Range:** 1.0 to 1.5  
**Default:** 1.24

Coefficient for Brutsaert longwave emissivity method.

**Typical Values:**
- Standard: 1.24
- Humid climates: 1.20-1.24
- Dry climates: 1.24-1.30

**Notes:**
- Only used with Brutsaert longwave method
- Original Brutsaert (1975) used 1.24
- Can be calibrated for specific locations

### solar_cloud_kcl1

**Type:** float  
**Units:** Dimensionless  
**Range:** 0 to 1  
**Default:** 0.65

Solar radiation cloud correction parameter 1.

**Notes:**
- Controls baseline clear-sky fraction
- Formula: radiation * (kcl1 + kcl2 * (1 - cloud_cover)^2)
- Higher values = less cloud effect
- Typical range: 0.5-0.8

### solar_cloud_kcl2

**Type:** float  
**Units:** Dimensionless  
**Range:** 0 to 5  
**Default:** 2.0

Solar radiation cloud correction parameter 2.

**Notes:**
- Controls cloud attenuation strength
- Formula: radiation * (kcl1 + kcl2 * (1 - cloud_cover)^2)
- Higher values = stronger cloud effect
- Typical range: 1.5-3.0

### longwave_cloud_method

**Type:** str  
**Options:** "Eqn 1", "Eqn 2"  
**Default:** "Eqn 1"

Longwave radiation cloud correction method.

**"Eqn 1"**: Multiplicative correction
- Formula: emissivity * (1 + kcl3 * cloud_cover^kcl4)
- Increases emissivity with cloud cover

**"Eqn 2"**: Blending correction
- Formula: emissivity * (1 - kcl3 * cloud_cover^kcl4) + kcl3 * cloud_cover^kcl4
- Blends clear-sky and overcast emissivity

**Notes:**
- Both methods increase longwave radiation with clouds
- Eqn 1 is simpler and more commonly used
- Eqn 2 provides more physical basis

### longwave_cloud_kcl3

**Type:** float  
**Units:** Dimensionless  
**Range:** 0 to 1  
**Default:** 0.17

Longwave radiation cloud correction parameter 3.

**Notes:**
- Controls magnitude of cloud effect
- Higher values = stronger cloud effect
- Typical range: 0.1-0.3

### longwave_cloud_kcl4

**Type:** float  
**Units:** Dimensionless  
**Range:** 0 to 5  
**Default:** 2.0

Longwave radiation cloud correction parameter 4.

**Notes:**
- Controls shape of cloud response
- Higher values = more nonlinear response
- Typical range: 1.5-3.0

### stability_criteria

**Type:** float  
**Units:** °C  
**Range:** 1 to 20  
**Default:** 5.0

Maximum allowed temperature change per timestep.

**Typical Values:**
- Strict: 2-3°C
- Moderate: 5°C (default)
- Relaxed: 10°C

**Notes:**
- Prevents numerical instability
- Triggers error if exceeded
- Reduce if getting stability errors
- Increase for very large timesteps (not recommended)

---

## Output Options

### enable_diagnostics

**Type:** bool  
**Options:** True, False  
**Default:** False

Enable detailed diagnostic output.

**When True, adds columns:**
- `solar_potential`: Solar radiation before corrections
- `solar_after_cloud`: After cloud correction
- `solar_after_shade`: After shade correction
- `albedo`: Surface reflection fraction
- `vapor_pressure_water`: Water surface vapor pressure
- `vapor_pressure_air`: Air vapor pressure
- `atmospheric_emissivity`: Calculated emissivity
- `wind_speed_2m`: Wind speed at 2m
- `wind_speed_7m`: Wind speed at 7m
- `wind_function`: Calculated wind function
- `water_temp_change_rate`: Rate of water temp change
- `sediment_temp_change_rate`: Rate of sediment temp change

**Notes:**
- Useful for debugging and analysis
- Increases output file size
- Minimal performance impact

---

## Configuration Examples

### Example 1: Simple Stream

```python
config = ModelConfiguration(
    # Location
    latitude=47.5,
    longitude=-122.0,
    elevation=100.0,
    timezone=8.0,
    
    # Water body
    water_depth=0.5,  # Shallow stream
    effective_shade=0.3,  # Some riparian vegetation
    wind_height=2.0,
    effective_wind_factor=0.6,  # Sheltered by banks
    
    # Initial conditions
    initial_water_temp=12.0,
    initial_sediment_temp=12.0,
    
    # Methods (defaults are fine)
    solar_method="Bras",
    longwave_method="Brunt",
    wind_function_method="Ryan-Harleman"  # Good for streams
)
```

### Example 2: Large Lake

```python
config = ModelConfiguration(
    # Location
    latitude=42.0,
    longitude=-88.0,
    elevation=200.0,
    timezone=6.0,
    
    # Water body
    water_depth=10.0,  # Deep lake
    effective_shade=0.0,  # Open water
    wind_height=10.0,  # Weather station height
    effective_wind_factor=1.0,  # Fully exposed
    
    # Initial conditions
    initial_water_temp=18.0,
    initial_sediment_temp=17.0,
    
    # Methods
    solar_method="Bird",  # High accuracy
    longwave_method="Brutsaert",
    wind_function_method="Marciano-Harbeck",  # Lake-specific
    
    # Enable diagnostics
    enable_diagnostics=True
)
```

### Example 3: Groundwater-Fed Stream

```python
config = ModelConfiguration(
    # Location
    latitude=45.0,
    longitude=-120.0,
    elevation=500.0,
    timezone=8.0,
    
    # Water body
    water_depth=0.8,
    effective_shade=0.5,
    
    # Groundwater influence
    groundwater_temperature=10.0,  # Cool groundwater
    groundwater_inflow=5.0,  # Significant inflow
    
    # Sediment exchange
    hyporheic_exchange_rate=20.0,  # Active hyporheic zone
    
    # Initial conditions
    initial_water_temp=14.0,
    initial_sediment_temp=12.0,
    
    # Methods
    solar_method="Bras",
    longwave_method="Satterlund",
    wind_function_method="Helfrich"
)
```

### Example 4: High-Accuracy Configuration

```python
config = ModelConfiguration(
    # Location
    latitude=40.0,
    longitude=-105.0,
    elevation=1600.0,  # High elevation
    timezone=7.0,
    
    # Water body
    water_depth=2.0,
    effective_shade=0.1,
    
    # High-accuracy methods
    solar_method="Bird",  # Most accurate
    longwave_method="Brutsaert",
    wind_function_method="Ryan-Harleman",
    
    # Tuned parameters
    atmospheric_turbidity=2.5,
    brutsaert_coefficient=1.24,
    solar_cloud_kcl1=0.70,
    solar_cloud_kcl2=2.5,
    
    # Strict stability
    stability_criteria=3.0,
    
    # Enable diagnostics
    enable_diagnostics=True
)
```

---

## Parameter Validation

The model automatically validates all parameters:

**Errors (halt execution):**
- Water depth ≤ 0
- Effective shade < 0 or > 1
- Wind height ≤ 0
- Effective wind factor < 0
- Groundwater temperature < 0
- Invalid method selection

**Warnings (auto-correct and continue):**
- Negative groundwater inflow → set to 0
- Negative sediment conductivity → set to 0
- Zero/negative sediment diffusivity → use water properties
- Zero/negative sediment thickness → set to 10 cm
- Negative hyporheic exchange → set to 0

---

## Tips for Parameter Selection

1. **Start with defaults**: Default values work well for many applications
2. **Calibrate if possible**: Compare to measured data and adjust
3. **Document choices**: Keep notes on why you selected specific values
4. **Test sensitivity**: Vary parameters to understand their impact
5. **Use appropriate methods**: Match methods to your data availability
6. **Consider uncertainty**: Parameters are estimates, not exact values
7. **Validate results**: Check that output is physically reasonable

