# rTemp Method Selection Guide

This guide helps you choose the most appropriate calculation methods for your application.

## Table of Contents

1. [Overview](#overview)
2. [Solar Radiation Methods](#solar-radiation-methods)
3. [Longwave Radiation Methods](#longwave-radiation-methods)
4. [Wind Function Methods](#wind-function-methods)
5. [Decision Trees](#decision-trees)
6. [Method Comparison](#method-comparison)
7. [Recommendations by Application](#recommendations-by-application)

---

## Overview

The rTemp model offers multiple calculation methods for three key components:

1. **Solar Radiation**: How much shortwave radiation reaches the water surface
2. **Longwave Radiation**: How much thermal infrared radiation comes from the atmosphere
3. **Wind Function**: How wind affects evaporation and convection

Choosing appropriate methods depends on:
- Available input data
- Desired accuracy
- Computational requirements
- Site characteristics
- Calibration data availability

---

## Solar Radiation Methods

Solar radiation is typically the largest heat source for water bodies during daytime. The model offers four methods with varying complexity and data requirements.

### Bras Method

**Description:** Simple atmospheric attenuation model based on optical air mass and turbidity.

**Data Requirements:**
- Minimal: Only requires solar position (calculated from location/time)
- One parameter: atmospheric turbidity factor

**Advantages:**
- Simple and fast
- Minimal data requirements
- Good for general applications
- Well-tested and reliable

**Disadvantages:**
- Less accurate for hazy/polluted conditions
- No detailed atmospheric composition
- Single turbidity parameter may not capture all conditions

**Best For:**
- General applications
- Limited atmospheric data
- Quick assessments
- Most water temperature modeling

**Parameter Tuning:**
- `atmospheric_turbidity`: 2.0 (default)
  - Clear conditions: 1.5-2.5
  - Moderate haze: 2.5-3.5
  - Hazy/polluted: 3.5-5.0

**Example:**
```python
config = ModelConfiguration(
    solar_method="Bras",
    atmospheric_turbidity=2.0,
    # ... other parameters
)
```

### Bird-Hulstrom Method

**Description:** Detailed clear-sky model accounting for multiple atmospheric components.

**Data Requirements:**
- Extensive: Requires detailed atmospheric data
- Parameters: pressure, ozone, water vapor, aerosol optical depths, forward scattering, albedo

**Advantages:**
- Highest accuracy for clear skies
- Physically-based
- Separates direct and diffuse components
- Well-validated against measurements

**Disadvantages:**
- Requires extensive atmospheric data
- More complex
- Data may not be readily available
- Slower computation

**Best For:**
- High-accuracy applications
- Research studies
- Sites with detailed atmospheric monitoring
- Validation studies

**Data Sources:**
- Atmospheric pressure: Weather stations or calculated from elevation
- Ozone: Satellite data (OMI, TOMS) or climatology
- Water vapor: Radiosonde data or estimated from dewpoint
- Aerosol optical depth: AERONET network or satellite data
- Forward scattering: Typically 0.82-0.88
- Albedo: 0.05-0.20 for water

**Example:**
```python
# Add to meteorological data DataFrame:
met_data['pressure_mb'] = 1013.25  # or calculated
met_data['ozone_cm'] = 0.3  # typical value
met_data['water_vapor_cm'] = 1.5  # or calculated from dewpoint
met_data['aod_500nm'] = 0.1  # aerosol optical depth
met_data['aod_380nm'] = 0.15
met_data['forward_scatter'] = 0.85
met_data['ground_albedo'] = 0.15

config = ModelConfiguration(
    solar_method="Bird",
    # ... other parameters
)
```

### Ryan-Stolzenbach Method

**Description:** Simplified model with elevation correction for atmospheric transmission.

**Data Requirements:**
- Minimal: Only requires solar position and site elevation
- One parameter: atmospheric transmission coefficient

**Advantages:**
- Simple and fast
- Accounts for elevation effects
- Good for quick estimates
- Minimal data requirements

**Disadvantages:**
- Less accurate than Bras or Bird
- Single transmission coefficient
- Limited atmospheric detail

**Best For:**
- Quick estimates
- High-elevation sites
- Limited data availability
- Screening-level assessments

**Parameter Tuning:**
- `atmospheric_transmission_coeff`: 0.8 (default)
  - Very clear: 0.85-0.91
  - Clear: 0.80-0.85
  - Moderate: 0.75-0.80
  - Hazy: 0.70-0.75

**Example:**
```python
config = ModelConfiguration(
    solar_method="Ryan-Stolzenbach",
    atmospheric_transmission_coeff=0.8,
    # ... other parameters
)
```

### Iqbal Method

**Description:** Comprehensive atmospheric transmittance model with moderate data requirements.

**Data Requirements:**
- Moderate: Requires some atmospheric data
- Parameters: pressure, ozone, visibility, albedo

**Advantages:**
- Good accuracy
- Moderate data requirements
- Physically-based
- Separates direct and diffuse components

**Disadvantages:**
- More data than Bras
- More complex than simple methods
- Visibility data may not be available

**Best For:**
- Balance of accuracy and data requirements
- Sites with moderate atmospheric data
- Applications requiring good accuracy
- When Bird method data is not available

**Data Sources:**
- Pressure: Weather stations or calculated
- Ozone: Satellite data or climatology (0.25-0.35 cm typical)
- Visibility: Weather observations (15-25 km typical)
- Albedo: 0.05-0.20 for water

**Example:**
```python
# Add to meteorological data DataFrame:
met_data['pressure_mb'] = 1013.25
met_data['ozone_cm'] = 0.3
met_data['visibility_km'] = 23.0
met_data['ground_albedo'] = 0.15

config = ModelConfiguration(
    solar_method="Iqbal",
    # ... other parameters
)
```

---

## Longwave Radiation Methods

Longwave (thermal infrared) radiation from the atmosphere is a significant heat source, especially at night. The model offers six emissivity methods.

### Brunt Method (1932)

**Description:** Classic empirical formula based on vapor pressure.

**Data Requirements:**
- Standard: Air temperature and vapor pressure (from dewpoint)

**Formula:** ε = a + b * sqrt(e)  
where e is vapor pressure in mmHg

**Advantages:**
- Simple and well-established
- Widely used and validated
- Good general performance
- Minimal data requirements

**Disadvantages:**
- Empirical coefficients
- May not be optimal for all climates
- Does not account for all atmospheric factors

**Best For:**
- General applications
- Standard meteorological data
- Most water temperature modeling
- Default choice

**Example:**
```python
config = ModelConfiguration(
    longwave_method="Brunt",
    # ... other parameters
)
```

### Brutsaert Method (1982)

**Description:** Physically-based formula with adjustable coefficient.

**Data Requirements:**
- Standard: Air temperature and vapor pressure

**Formula:** ε = coeff * (e/T)^(1/7)  
where e is vapor pressure in hPa, T is temperature in K

**Advantages:**
- Physically-based
- Adjustable coefficient for calibration
- Good for humid climates
- Well-validated

**Disadvantages:**
- Requires coefficient selection
- May need calibration
- Similar data to Brunt

**Best For:**
- Humid climates
- Applications requiring calibration
- Research studies
- When Brunt performs poorly

**Parameter Tuning:**
- `brutsaert_coefficient`: 1.24 (default)
  - Humid climates: 1.20-1.24
  - Dry climates: 1.24-1.30
  - Calibrate to local data if available

**Example:**
```python
config = ModelConfiguration(
    longwave_method="Brutsaert",
    brutsaert_coefficient=1.24,
    # ... other parameters
)
```

### Satterlund Method (1979)

**Description:** Exponential formula based on dewpoint temperature.

**Data Requirements:**
- Standard: Air temperature and dewpoint

**Formula:** ε = 1.08 * (1 - exp(-e^(T_d/2016)))  
where T_d is dewpoint in K

**Advantages:**
- Good performance across conditions
- Uses dewpoint directly
- Well-validated
- Simple

**Disadvantages:**
- Empirical formula
- May overestimate in some conditions

**Best For:**
- Wide range of conditions
- When dewpoint is primary humidity measure
- General applications
- Alternative to Brunt

**Example:**
```python
config = ModelConfiguration(
    longwave_method="Satterlund",
    # ... other parameters
)
```

### Idso-Jackson Method (1969)

**Description:** Simple formula using only air temperature.

**Data Requirements:**
- Minimal: Only air temperature

**Formula:** ε = 1 - 0.261 * exp(-7.77e-4 * T^2)  
where T is air temperature in °C

**Advantages:**
- Minimal data requirements
- Simple and fast
- No humidity data needed

**Disadvantages:**
- Less accurate than methods using humidity
- Does not account for moisture effects
- May underestimate in humid conditions

**Best For:**
- Limited data availability
- Quick estimates
- When humidity data is unavailable
- Screening-level assessments

**Example:**
```python
config = ModelConfiguration(
    longwave_method="Idso-Jackson",
    # ... other parameters
)
```

### Swinbank Method (1963)

**Description:** Simple temperature-only formula.

**Data Requirements:**
- Minimal: Only air temperature

**Formula:** ε = 9.37e-6 * T^2  
where T is air temperature in K

**Advantages:**
- Very simple
- Minimal data requirements
- Fast computation

**Disadvantages:**
- Less accurate
- Does not account for humidity
- May not perform well in all conditions

**Best For:**
- Quick estimates
- Limited data
- Screening studies
- When humidity is unavailable

**Example:**
```python
config = ModelConfiguration(
    longwave_method="Swinbank",
    # ... other parameters
)
```

### Koberg Method (1964)

**Description:** Interpolation-based method using air temperature and clearness.

**Data Requirements:**
- Standard: Air temperature and atmospheric clearness

**Advantages:**
- Accounts for atmospheric clarity
- Good for specific conditions

**Disadvantages:**
- More complex
- Requires clearness parameter
- Less commonly used

**Best For:**
- Specific calibrated applications
- When clearness data is available

**Example:**
```python
config = ModelConfiguration(
    longwave_method="Koberg",
    # ... other parameters
)
```

---

## Wind Function Methods

Wind functions relate wind speed to evaporation and convection rates. The model offers five methods developed for different water body types.

### Brady-Graves-Geyer Method

**Description:** General-purpose wind function.

**Wind Height:** 7 meters

**Advantages:**
- General applicability
- Well-tested
- Good default choice
- Moderate values

**Disadvantages:**
- Not optimized for specific water body types
- May need calibration

**Best For:**
- General applications
- Mixed water body types
- Default choice
- When specific method is unknown

**Example:**
```python
config = ModelConfiguration(
    wind_function_method="Brady-Graves-Geyer",
    wind_height=7.0,  # or will be adjusted from measurement height
    # ... other parameters
)
```

### Marciano-Harbeck Method

**Description:** Lake Hefner formula developed for large lakes.

**Wind Height:** 7 meters

**Advantages:**
- Optimized for lakes
- Well-validated for large water bodies
- Widely used

**Disadvantages:**
- May overestimate for small water bodies
- Developed for specific conditions

**Best For:**
- Large lakes
- Reservoirs
- Open water bodies
- Lake studies

**Example:**
```python
config = ModelConfiguration(
    wind_function_method="Marciano-Harbeck",
    wind_height=7.0,
    effective_wind_factor=1.0,  # Typically fully exposed
    # ... other parameters
)
```

### Ryan-Harleman Method

**Description:** Formula with virtual temperature correction, developed for rivers.

**Wind Height:** 2 meters

**Advantages:**
- Accounts for stability effects
- Good for rivers and streams
- Physically-based correction
- Well-validated

**Disadvantages:**
- More complex
- Requires accurate temperature data

**Best For:**
- Rivers and streams
- Flowing water
- Applications requiring high accuracy
- When stability effects are important

**Example:**
```python
config = ModelConfiguration(
    wind_function_method="Ryan-Harleman",
    wind_height=2.0,
    effective_wind_factor=0.6,  # Often sheltered
    # ... other parameters
)
```

### East-Mesa Method

**Description:** Modified wind function combining temperature and wind effects.

**Wind Height:** 2 meters

**Advantages:**
- Combines multiple effects
- Good for specific applications

**Disadvantages:**
- Less commonly used
- May need calibration

**Best For:**
- Specific calibrated applications
- When other methods perform poorly

**Example:**
```python
config = ModelConfiguration(
    wind_function_method="East-Mesa",
    wind_height=2.0,
    # ... other parameters
)
```

### Helfrich Method

**Description:** Recalibrated Ryan-Harleman formula.

**Wind Height:** 2 meters

**Advantages:**
- Improved calibration
- Good for rivers and streams
- Similar to Ryan-Harleman but updated

**Disadvantages:**
- Similar limitations to Ryan-Harleman

**Best For:**
- Rivers and streams
- Alternative to Ryan-Harleman
- When Ryan-Harleman needs adjustment

**Example:**
```python
config = ModelConfiguration(
    wind_function_method="Helfrich",
    wind_height=2.0,
    # ... other parameters
)
```

---

## Decision Trees

### Solar Radiation Method Selection

```
Do you have detailed atmospheric data (ozone, aerosols, etc.)?
├─ YES → Use Bird method for highest accuracy
└─ NO
   ├─ Do you have visibility data?
   │  ├─ YES → Use Iqbal method for good accuracy
   │  └─ NO
   │     ├─ Is site at high elevation (>1000m)?
   │     │  ├─ YES → Consider Ryan-Stolzenbach
   │     │  └─ NO → Use Bras method (default)
   │     └─ Need quick estimate?
   │        └─ YES → Use Ryan-Stolzenbach
```

### Longwave Radiation Method Selection

```
Do you have humidity/dewpoint data?
├─ YES
│  ├─ Need calibration capability?
│  │  ├─ YES → Use Brutsaert method
│  │  └─ NO → Use Brunt method (default)
│  └─ Want alternative?
│     └─ Use Satterlund method
└─ NO (only air temperature)
   ├─ Need reasonable accuracy?
   │  └─ Use Idso-Jackson method
   └─ Quick estimate only?
      └─ Use Swinbank method
```

### Wind Function Method Selection

```
What type of water body?
├─ Large lake or reservoir
│  └─ Use Marciano-Harbeck method
├─ River or stream
│  ├─ Need high accuracy?
│  │  └─ Use Ryan-Harleman or Helfrich method
│  └─ General application?
│     └─ Use Brady-Graves-Geyer method
└─ Unknown or mixed
   └─ Use Brady-Graves-Geyer method (default)
```

---

## Method Comparison

### Solar Radiation Methods Comparison

| Method | Complexity | Data Needs | Accuracy | Speed | Best Use |
|--------|-----------|------------|----------|-------|----------|
| Bras | Low | Minimal | Good | Fast | General |
| Bird | High | Extensive | Excellent | Slow | Research |
| Ryan-Stolz | Low | Minimal | Moderate | Fast | Quick estimates |
| Iqbal | Medium | Moderate | Very Good | Medium | Balanced |

### Longwave Radiation Methods Comparison

| Method | Complexity | Data Needs | Accuracy | Calibration | Best Use |
|--------|-----------|------------|----------|-------------|----------|
| Brunt | Low | Standard | Good | No | General |
| Brutsaert | Low | Standard | Very Good | Yes | Humid climates |
| Satterlund | Low | Standard | Good | No | Wide conditions |
| Idso-Jackson | Very Low | Minimal | Moderate | No | Limited data |
| Swinbank | Very Low | Minimal | Moderate | No | Quick estimates |
| Koberg | Medium | Standard | Good | Yes | Specific apps |

### Wind Function Methods Comparison

| Method | Water Body | Wind Height | Complexity | Validation | Best Use |
|--------|-----------|-------------|------------|------------|----------|
| Brady-Graves-Geyer | General | 7m | Low | Good | Default |
| Marciano-Harbeck | Lakes | 7m | Low | Excellent | Large lakes |
| Ryan-Harleman | Rivers | 2m | Medium | Excellent | Rivers/streams |
| East-Mesa | Various | 2m | Medium | Moderate | Specific apps |
| Helfrich | Rivers | 2m | Medium | Very Good | Rivers/streams |

---

## Recommendations by Application

### Small Stream or Creek

```python
config = ModelConfiguration(
    solar_method="Bras",  # Simple, adequate accuracy
    longwave_method="Brunt",  # Standard choice
    wind_function_method="Ryan-Harleman",  # Good for streams
    atmospheric_turbidity=2.0,
    water_depth=0.3,
    effective_shade=0.4,  # Often shaded
    effective_wind_factor=0.5  # Sheltered
)
```

### Large River

```python
config = ModelConfiguration(
    solar_method="Bras",  # or Iqbal for better accuracy
    longwave_method="Brutsaert",  # Calibratable
    wind_function_method="Helfrich",  # River-specific
    atmospheric_turbidity=2.5,
    water_depth=3.0,
    effective_shade=0.1,  # Mostly open
    effective_wind_factor=0.7  # Partially sheltered
)
```

### Large Lake or Reservoir

```python
config = ModelConfiguration(
    solar_method="Bird",  # High accuracy if data available
    longwave_method="Brutsaert",
    wind_function_method="Marciano-Harbeck",  # Lake-specific
    water_depth=10.0,
    effective_shade=0.0,  # Open water
    effective_wind_factor=1.0,  # Fully exposed
    enable_diagnostics=True  # For detailed analysis
)
```

### High-Elevation Site

```python
config = ModelConfiguration(
    solar_method="Ryan-Stolzenbach",  # Accounts for elevation
    longwave_method="Satterlund",  # Good for variable conditions
    wind_function_method="Brady-Graves-Geyer",
    atmospheric_transmission_coeff=0.85,  # Clearer at elevation
    elevation=2000.0,
    water_depth=1.5
)
```

### Research/Validation Study

```python
config = ModelConfiguration(
    solar_method="Bird",  # Highest accuracy
    longwave_method="Brutsaert",  # Calibratable
    wind_function_method="Ryan-Harleman",  # Physically-based
    brutsaert_coefficient=1.24,  # Calibrate if possible
    enable_diagnostics=True,  # Full output
    stability_criteria=3.0  # Strict stability
)
```

### Quick Assessment/Screening

```python
config = ModelConfiguration(
    solar_method="Bras",  # Fast and simple
    longwave_method="Brunt",  # Standard
    wind_function_method="Brady-Graves-Geyer",  # General
    # Use all defaults
)
```

### Limited Data Availability

```python
config = ModelConfiguration(
    solar_method="Bras",  # Minimal data needs
    longwave_method="Idso-Jackson",  # Only needs air temp
    wind_function_method="Brady-Graves-Geyer",  # General
    # Provide what data you have
)
```

---

## Calibration and Validation

### When to Calibrate

Calibrate methods when:
- You have measured water temperature data
- Model predictions don't match observations
- Site has unusual characteristics
- High accuracy is required

### What to Calibrate

**Solar Radiation:**
- Atmospheric turbidity (Bras)
- Atmospheric transmission coefficient (Ryan-Stolzenbach)
- Cloud correction parameters (KCL1, KCL2)

**Longwave Radiation:**
- Brutsaert coefficient
- Cloud correction parameters (KCL3, KCL4)

**Wind Function:**
- Effective wind factor
- May need to develop site-specific function

### Calibration Process

1. **Collect Data:**
   - Measured water temperatures
   - Meteorological data
   - Site characteristics

2. **Initial Run:**
   - Use default methods and parameters
   - Compare predictions to observations

3. **Identify Issues:**
   - Systematic bias (too warm/cool)?
   - Diurnal range too large/small?
   - Specific conditions problematic?

4. **Adjust Parameters:**
   - Start with most sensitive parameters
   - Adjust one at a time
   - Document changes

5. **Validate:**
   - Test on independent data
   - Check multiple seasons/conditions
   - Verify physical reasonableness

### Validation Metrics

- Mean Error (ME): Average difference
- Mean Absolute Error (MAE): Average magnitude of errors
- Root Mean Square Error (RMSE): Overall accuracy
- Nash-Sutcliffe Efficiency (NSE): Model performance
- Correlation coefficient (R²): Linear relationship

---

## Summary

**Default Recommendation:**
```python
config = ModelConfiguration(
    solar_method="Bras",
    longwave_method="Brunt",
    wind_function_method="Brady-Graves-Geyer"
)
```

This combination works well for most applications with standard meteorological data.

**Upgrade Path:**
1. Start with defaults
2. If accuracy is insufficient, try Iqbal solar and Brutsaert longwave
3. If still insufficient, use Bird solar (if data available)
4. Calibrate parameters to local conditions
5. Consider site-specific wind function

**Key Principle:**
Choose the simplest methods that meet your accuracy requirements and data availability. More complex methods are not always better if you don't have the required input data or calibration capability.

