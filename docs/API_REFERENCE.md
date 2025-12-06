# rTemp API Reference

This document provides detailed API documentation for the rTemp water temperature model.

## About This Implementation

This Python implementation is based on the original VBA rTemp model by Greg Pelletier (Washington State Department of Ecology) and has been validated to ensure accuracy:

- **Water Temperature RMSE**: 0.13°C (excellent agreement with VBA)
- **Heat Flux Accuracy**: < 7 W/m² RMSE for all components
- **Test Coverage**: 346 automated tests passing
- **Status**: Production-ready for water temperature modeling

See the [User Guide](USER_GUIDE.md#validation-results) for detailed validation results.

## Table of Contents

- [Main Model Class](#main-model-class)
- [Configuration](#configuration)
- [Data Models](#data-models)
- [Solar Module](#solar-module)
- [Atmospheric Module](#atmospheric-module)
- [Wind Module](#wind-module)
- [Heat Flux Module](#heat-flux-module)
- [Utilities](#utilities)
- [Validation and Accuracy](#validation-and-accuracy)

---

## Main Model Class

### RTempModel

The main class for running water temperature simulations.

```python
from rtemp import RTempModel, ModelConfiguration
```

#### Constructor

```python
RTempModel(config: ModelConfiguration)
```

**Parameters:**
- `config` (ModelConfiguration): Model configuration object containing all parameters and method selections

**Example:**
```python
config = ModelConfiguration(
    latitude=47.5,
    longitude=-122.0,
    elevation=100.0,
    timezone=8.0,
    initial_water_temp=15.0,
    water_depth=2.0
)
model = RTempModel(config)
```

#### Methods

##### run()

```python
run(met_data: pd.DataFrame) -> pd.DataFrame
```

Execute the model for a time series of meteorological data.

**Parameters:**
- `met_data` (pd.DataFrame): Meteorological input data with required columns:
  - `datetime` (datetime): Timestamp
  - `air_temp` (float): Air temperature in °C
  - `dewpoint` (float): Dewpoint temperature in °C
  - `wind_speed` (float): Wind speed in m/s
  - `cloud_cover` (float): Cloud cover fraction (0-1)

**Returns:**
- pd.DataFrame: Results with columns:
  - `datetime`: Timestamp
  - `water_temp`: Calculated water temperature (°C)
  - `sediment_temp`: Calculated sediment temperature (°C)
  - `solar_radiation`: Solar radiation (W/m²)
  - `longwave_atm`: Atmospheric longwave radiation (W/m²)
  - `longwave_back`: Back radiation from water (W/m²)
  - `evaporation`: Evaporation heat flux (W/m²)
  - `convection`: Convection heat flux (W/m²)
  - `sediment_flux`: Sediment conduction flux (W/m²)
  - `hyporheic_flux`: Hyporheic exchange flux (W/m²)
  - `groundwater_flux`: Groundwater flux (W/m²)
  - `net_flux`: Net heat flux (W/m²)
  - `solar_azimuth`: Solar azimuth angle (degrees)
  - `solar_elevation`: Solar elevation angle (degrees)

**Raises:**
- `ValueError`: If input data is invalid
- `RuntimeError`: If numerical instability is detected

**Example:**
```python
results = model.run(met_data)
results.to_csv("output.csv", index=False)
```

---

## Configuration

### ModelConfiguration

Configuration dataclass containing all model parameters.

```python
from rtemp import ModelConfiguration
```

#### Parameters

**Site Parameters:**
- `latitude` (float): Site latitude in decimal degrees (positive north)
- `longitude` (float): Site longitude in decimal degrees (positive east, negative west)
- `elevation` (float): Site elevation in meters above sea level
- `timezone` (float): Hours from UTC (positive for west, e.g., 8.0 for PST)
- `daylight_savings` (int): Daylight savings time offset (0 or 1)

**Initial Conditions:**
- `initial_water_temp` (float): Initial water temperature in °C (default: 15.0)
- `initial_sediment_temp` (float): Initial sediment temperature in °C (default: 15.0)
- `minimum_temperature` (float): Minimum allowed temperature in °C (default: 0.0)

**Water Body Parameters:**
- `water_depth` (float): Water depth in meters (default: 1.0)
- `effective_shade` (float): Effective shade fraction 0-1 (default: 0.0)
- `wind_height` (float): Wind measurement height in meters (default: 2.0)
- `effective_wind_factor` (float): Wind reduction factor 0-1 (default: 1.0)

**Sediment Parameters:**
- `sediment_thermal_conductivity` (float): Thermal conductivity in W/m/°C (default: 1.0)
- `sediment_thermal_diffusivity` (float): Thermal diffusivity in cm²/s (default: 0.005)
- `sediment_thickness` (float): Active sediment layer thickness in cm (default: 10.0)
- `hyporheic_exchange_rate` (float): Hyporheic exchange rate in cm/day (default: 0.0)

**Groundwater Parameters:**
- `groundwater_temperature` (float): Groundwater temperature in °C (default: 10.0)
- `groundwater_inflow` (float): Groundwater inflow rate in cm/day (default: 0.0)

**Method Selections:**
- `solar_method` (str): Solar radiation method - "Bras", "Bird", "Ryan-Stolzenbach", or "Iqbal" (default: "Bras")
- `longwave_method` (str): Longwave radiation method - "Brunt", "Brutsaert", "Satterlund", "Idso-Jackson", "Swinbank", or "Koberg" (default: "Brunt")
- `wind_function_method` (str): Wind function method - "Brady-Graves-Geyer", "Marciano-Harbeck", "Ryan-Harleman", "East-Mesa", or "Helfrich" (default: "Brady-Graves-Geyer")

**Model Parameters:**
- `atmospheric_turbidity` (float): Atmospheric turbidity factor for Bras method (default: 2.0)
- `atmospheric_transmission_coeff` (float): Transmission coefficient for Ryan-Stolzenbach (default: 0.8)
- `brutsaert_coefficient` (float): Coefficient for Brutsaert longwave method (default: 1.24)
- `solar_cloud_kcl1` (float): Solar cloud correction parameter 1 (default: 0.65)
- `solar_cloud_kcl2` (float): Solar cloud correction parameter 2 (default: 2.0)
- `longwave_cloud_method` (str): Longwave cloud correction - "Eqn 1" or "Eqn 2" (default: "Eqn 1")
- `longwave_cloud_kcl3` (float): Longwave cloud correction parameter 3 (default: 0.17)
- `longwave_cloud_kcl4` (float): Longwave cloud correction parameter 4 (default: 2.0)
- `stability_criteria` (float): Maximum allowed temperature change per timestep in °C (default: 5.0)

**Output Options:**
- `enable_diagnostics` (bool): Enable detailed diagnostic output (default: False)

**Example:**
```python
config = ModelConfiguration(
    latitude=47.5,
    longitude=-122.0,
    elevation=100.0,
    timezone=8.0,
    initial_water_temp=15.0,
    water_depth=2.0,
    solar_method="Bird",
    longwave_method="Brutsaert",
    wind_function_method="Ryan-Harleman",
    enable_diagnostics=True
)
```

---

## Data Models

### MeteorologicalData

Input meteorological data structure (typically as DataFrame columns).

**Required Columns:**
- `datetime` (datetime): Timestamp
- `air_temp` (float): Air temperature in °C
- `dewpoint` (float): Dewpoint temperature in °C
- `wind_speed` (float): Wind speed in m/s
- `cloud_cover` (float): Cloud cover fraction (0-1)

**Optional Columns:**
- `solar_radiation` (float): Measured solar radiation in W/m²
- `pressure_mb` (float): Atmospheric pressure in millibars (for Bird method)
- `ozone_cm` (float): Ozone layer thickness in cm (for Bird/Iqbal methods)
- `water_vapor_cm` (float): Precipitable water vapor in cm (for Bird method)
- `aod_500nm` (float): Aerosol optical depth at 500nm (for Bird method)
- `aod_380nm` (float): Aerosol optical depth at 380nm (for Bird method)
- `forward_scatter` (float): Forward scattering fraction (for Bird method)
- `ground_albedo` (float): Ground albedo (for Bird/Iqbal methods)
- `visibility_km` (float): Visibility in km (for Iqbal method)
- `water_depth_override` (float): Time-varying water depth in meters
- `effective_shade_override` (float): Time-varying shade fraction (0-1)

---

## Solar Module

### NOAASolarPosition

NOAA solar position algorithm implementation.

```python
from rtemp.solar import NOAASolarPosition
```

#### Methods

##### calc_solar_position()

```python
@staticmethod
calc_solar_position(
    lat: float,
    lon: float,
    dt: datetime,
    timezone: float,
    dlstime: int
) -> Tuple[float, float, float]
```

Calculate solar position for given location and time.

**Parameters:**
- `lat`: Latitude in decimal degrees
- `lon`: Longitude in decimal degrees (negative for west)
- `dt`: Datetime object
- `timezone`: Hours from UTC
- `dlstime`: Daylight savings offset (0 or 1)

**Returns:**
- Tuple of (azimuth, elevation, earth_sun_distance)
  - azimuth: Solar azimuth in degrees from north
  - elevation: Solar elevation in degrees above horizon
  - earth_sun_distance: Earth-Sun distance in AU

**Example:**
```python
from datetime import datetime
azimuth, elevation, distance = NOAASolarPosition.calc_solar_position(
    lat=47.5,
    lon=-122.0,
    dt=datetime(2024, 6, 21, 12, 0),
    timezone=8.0,
    dlstime=1
)
```

### Solar Radiation Models

#### SolarRadiationBras

Bras atmospheric attenuation model.

```python
from rtemp.solar import SolarRadiationBras

radiation = SolarRadiationBras.calculate(
    elevation=45.0,  # degrees
    earth_sun_distance=1.0,  # AU
    turbidity=2.0  # atmospheric turbidity factor
)
```

#### SolarRadiationBird

Bird & Hulstrom clear sky model.

```python
from rtemp.solar import SolarRadiationBird

result = SolarRadiationBird.calculate(
    zenith=45.0,  # degrees
    earth_sun_distance=1.0,  # AU
    pressure_mb=1013.25,
    ozone_cm=0.3,
    water_cm=1.5,
    aod_500nm=0.1,
    aod_380nm=0.15,
    forward_scatter=0.85,
    albedo=0.2
)
# result is dict with keys: direct_beam, direct_hz, global_hz, diffuse_hz
```

#### SolarRadiationRyanStolz

Ryan-Stolzenbach model.

```python
from rtemp.solar import SolarRadiationRyanStolz

radiation = SolarRadiationRyanStolz.calculate(
    elevation=45.0,  # degrees
    earth_sun_distance=1.0,  # AU
    atm_transmission_coeff=0.8,
    site_elevation=100.0  # meters
)
```

#### SolarRadiationIqbal

Iqbal atmospheric transmittance model.

```python
from rtemp.solar import SolarRadiationIqbal

result = SolarRadiationIqbal.calculate(
    zenith=45.0,  # degrees
    earth_sun_distance=1.0,  # AU
    pressure_mb=1013.25,
    ozone_cm=0.3,
    visibility_km=23.0,
    albedo=0.2
)
# result is dict with keys: direct, diffuse, global_hz
```

---

## Atmospheric Module

### Longwave Emissivity Models

All emissivity models inherit from `LongwaveEmissivity` base class.

```python
from rtemp.atmospheric import (
    EmissivityBrunt,
    EmissivityBrutsaert,
    EmissivitySatterlund,
    EmissivityIdsoJackson,
    EmissivitySwinbank,
    EmissivityKoberg
)
```

#### calculate()

```python
calculate(
    air_temp_c: float,
    vapor_pressure_mmhg: float,
    cloud_cover: float = 0.0,
    **kwargs
) -> float
```

Calculate atmospheric emissivity.

**Parameters:**
- `air_temp_c`: Air temperature in °C
- `vapor_pressure_mmhg`: Vapor pressure in mmHg
- `cloud_cover`: Cloud cover fraction (0-1)
- `**kwargs`: Method-specific parameters

**Returns:**
- float: Atmospheric emissivity (0-1)

**Example:**
```python
emissivity = EmissivityBrunt().calculate(
    air_temp_c=20.0,
    vapor_pressure_mmhg=12.0,
    cloud_cover=0.5
)
```

### LongwaveRadiation

Calculate longwave radiation fluxes.

```python
from rtemp.atmospheric import LongwaveRadiation
```

#### calculate_atmospheric()

```python
@staticmethod
calculate_atmospheric(
    emissivity: float,
    air_temp_c: float,
    cloud_cover: float,
    cloud_method: str,
    kcl3: float,
    kcl4: float
) -> float
```

Calculate atmospheric longwave radiation.

**Returns:**
- float: Longwave atmospheric radiation in W/m²

#### calculate_back_radiation()

```python
@staticmethod
calculate_back_radiation(water_temp_c: float) -> float
```

Calculate longwave back radiation from water surface.

**Returns:**
- float: Back radiation in W/m²

---

## Wind Module

### Wind Function Models

```python
from rtemp.wind import (
    WindFunctionBradyGravesGeyer,
    WindFunctionMarcianoHarbeck,
    WindFunctionRyanHarleman,
    WindFunctionEastMesa,
    WindFunctionHelfrich
)
```

#### calculate()

```python
calculate(
    wind_speed: float,
    air_temp: float,
    water_temp: float,
    vapor_pressure_air: float,
    vapor_pressure_water: float
) -> float
```

Calculate wind function for evaporation/convection.

**Parameters:**
- `wind_speed`: Wind speed in m/s
- `air_temp`: Air temperature in °C
- `water_temp`: Water temperature in °C
- `vapor_pressure_air`: Air vapor pressure in mmHg
- `vapor_pressure_water`: Water surface vapor pressure in mmHg

**Returns:**
- float: Wind function value

### WindAdjustment

Adjust wind speed for height.

```python
from rtemp.wind import WindAdjustment

adjusted_speed = WindAdjustment.adjust_for_height(
    wind_speed=5.0,  # m/s
    measured_height=10.0,  # meters
    target_height=2.0  # meters
)
```

---

## Heat Flux Module

### HeatFluxCalculator

Calculate individual heat flux components.

```python
from rtemp.heat_flux import HeatFluxCalculator
```

All methods are static and return heat flux in W/m².

#### calculate_evaporation()

```python
@staticmethod
calculate_evaporation(
    wind_function: float,
    vapor_pressure_water: float,
    vapor_pressure_air: float
) -> float
```

#### calculate_convection()

```python
@staticmethod
calculate_convection(
    wind_function: float,
    water_temp: float,
    air_temp: float,
    bowen_ratio: float = 0.61
) -> float
```

#### calculate_sediment_conduction()

```python
@staticmethod
calculate_sediment_conduction(
    water_temp: float,
    sediment_temp: float,
    thermal_conductivity: float,
    sediment_thickness: float
) -> float
```

#### calculate_hyporheic_exchange()

```python
@staticmethod
calculate_hyporheic_exchange(
    water_temp: float,
    sediment_temp: float,
    exchange_rate: float
) -> float
```

#### calculate_groundwater_flux()

```python
@staticmethod
calculate_groundwater_flux(
    water_temp: float,
    groundwater_temp: float,
    inflow_rate: float
) -> float
```

---

## Utilities

### AtmosphericHelpers

Atmospheric property calculations.

```python
from rtemp.utils import AtmosphericHelpers
```

#### saturation_vapor_pressure()

```python
@staticmethod
saturation_vapor_pressure(temp_c: float) -> float
```

Calculate saturation vapor pressure using Magnus formula.

**Returns:**
- float: Saturation vapor pressure in mmHg

#### dewpoint_from_rh()

```python
@staticmethod
dewpoint_from_rh(air_temp: float, relative_humidity: float) -> float
```

Calculate dewpoint from relative humidity.

**Returns:**
- float: Dewpoint temperature in °C

#### relative_humidity_from_dewpoint()

```python
@staticmethod
relative_humidity_from_dewpoint(air_temp: float, dewpoint: float) -> float
```

Calculate relative humidity from dewpoint.

**Returns:**
- float: Relative humidity as fraction (0-1)

### UnitConversions

Unit conversion utilities.

```python
from rtemp.utils import UnitConversions
```

Available conversions:
- `watts_m2_to_cal_cm2_day(watts_m2: float) -> float`
- `cal_cm2_day_to_watts_m2(cal_cm2_day: float) -> float`
- `deg_to_rad(degrees: float) -> float`
- `rad_to_deg(radians: float) -> float`
- `celsius_to_kelvin(celsius: float) -> float`
- `meters_to_centimeters(meters: float) -> float`

### InputValidator

Input validation utilities.

```python
from rtemp.utils import InputValidator
```

#### validate_site_parameters()

```python
@staticmethod
validate_site_parameters(params: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]
```

Validate site parameters and return corrected values with warnings.

#### validate_meteorological_data()

```python
@staticmethod
validate_meteorological_data(data: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]
```

Validate meteorological data and return corrected DataFrame with warnings.

---

## Constants

Physical constants used in calculations.

```python
from rtemp.constants import (
    STEFAN_BOLTZMANN,  # Stefan-Boltzmann constant
    WATER_DENSITY,  # Water density (g/cm³)
    WATER_SPECIFIC_HEAT,  # Water specific heat (cal/g/°C)
    SEDIMENT_DENSITY,  # Sediment density (g/cm³)
    SEDIMENT_SPECIFIC_HEAT,  # Sediment specific heat (cal/g/°C)
    BOWEN_RATIO,  # Bowen ratio
    WATER_EMISSIVITY,  # Water surface emissivity
    SOLAR_CONSTANT  # Solar constant (W/m²)
)
```

---

## Error Handling

### Exceptions

The model raises the following exceptions:

- `ValueError`: Invalid input parameters or configuration
- `RuntimeError`: Numerical instability detected during execution

### Warnings

The model issues warnings for:
- Missing or invalid meteorological data (substitutes defaults)
- Large timesteps (> 2 hours)
- Very large timesteps (> 4 hours, resets temperatures)
- Negative values that are set to zero
- Out-of-range values that are clamped

Warnings are logged using Python's `logging` module at the WARNING level.

---

## Examples

See the `examples/` directory for complete working examples:
- `basic_usage.py`: Simple model run
- `all_methods_demo.py`: Demonstration of all calculation methods
- `diagnostic_output_demo.py`: Using diagnostic output
- `time_varying_parameters_demo.py`: Time-varying depth and shade
- `solar_corrections_demo.py`: Solar radiation corrections



---

## Validation and Accuracy

### Model Validation

The Python implementation has been rigorously validated against the original VBA rTemp model:

#### Validation Dataset
- **Period**: October-December 2003 (3 months)
- **Timesteps**: 8,828 (15-minute intervals)
- **Location**: Washington State (48.45°N, 122.33°W)
- **Methods**: All calculation methods tested

#### Accuracy Metrics

**Water Temperature:**
```python
RMSE = 0.13°C          # Excellent
Mean Difference = 0.096°C  # < 2% error
Max Difference = 0.39°C    # Acceptable
```

**Heat Flux Components:**
```python
Solar Radiation RMSE = 6.82 W/m²      # 2.4% error
Longwave Atmospheric RMSE = 0.13 W/m²  # 0.07% error
Longwave Back RMSE = 0.60 W/m²        # 0.59% error
Convection RMSE = 0.64 W/m²
Evaporation RMSE = 0.71 W/m²
Sediment Conduction RMSE = 5.44 W/m²
```

### Method-Specific Validation

#### Solar Radiation Methods

All solar radiation methods have been validated:

**Bras Method:**
- Formula corrected from VBA implementation
- RMSE: 6.82 W/m² when using measured data
- Recommended for: General use, clear sky conditions

**Bird-Hulstrom Method:**
- Comprehensive atmospheric model
- Requires additional atmospheric parameters
- Recommended for: Detailed studies, research

**Ryan-Stolzenbach Method:**
- Simplified atmospheric transmission
- Fast computation
- Recommended for: Quick estimates, screening

**Iqbal Method:**
- Detailed spectral model
- Requires visibility and atmospheric data
- Recommended for: Research, detailed analysis

#### Longwave Radiation Methods

**Brunt Method:**
- Classic emissivity formula
- RMSE: 0.13 W/m² (0.07% error)
- Recommended for: General use

**Brutsaert Method:**
- Improved vapor pressure relationship
- Excellent accuracy
- Recommended for: Humid conditions

**Swinbank Method:**
- Temperature-based only
- Good for missing humidity data
- Recommended for: Limited data availability

#### Wind Function Methods

**Brady-Graves-Geyer:**
- Quadratic wind relationship
- Validated against VBA
- Recommended for: General use, lakes

**Ryan-Harleman:**
- Includes stability effects
- More complex
- Recommended for: Detailed studies

**Marciano-Harbeck:**
- Linear wind relationship
- Simple and fast
- Recommended for: Quick estimates

### Numerical Stability

The model includes several stability checks:

```python
# Stability criteria (default: 0.5°C)
config = ModelConfiguration(
    stability_criteria=0.5  # Maximum temperature change per timestep
)
```

**Recommendations:**
- Use timesteps ≤ 1 hour for best results
- Use timesteps ≤ 15 minutes for high accuracy
- Enable stability checking for long simulations

### Known Limitations

1. **Maximum Temperature Difference**: 0.39°C occurs on 1 day out of 92 (1% of validation period)
2. **Edge Cases**: Small differences near sunrise/sunset when sun elevation < 2°
3. **Accumulated Errors**: Small differences can accumulate over very long periods (> 3 months)

These limitations are acceptable for most water temperature modeling applications.

### Confidence Intervals

Based on validation results, expected accuracy for typical applications:

| Application | Expected Accuracy | Confidence |
|-------------|------------------|------------|
| Daily mean temperature | ± 0.1°C | High |
| Hourly temperature | ± 0.2°C | High |
| Peak temperature | ± 0.4°C | Medium-High |
| Long-term statistics | ± 0.15°C | High |

### Testing

The implementation includes comprehensive testing:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=rtemp --cov-report=html

# Run validation tests only
pytest tests/validation/
```

**Test Categories:**
- **Unit Tests**: Individual component testing (200+ tests)
- **Property Tests**: Edge cases and invariants (100+ tests)
- **Integration Tests**: Full model scenarios (40+ tests)
- **Validation Tests**: VBA comparison (6 tests)

### References

For detailed validation methodology and results:
- [Solar Radiation Fix Summary](validation/SOLAR_RADIATION_FIX_SUMMARY.md) - Solar radiation validation
- [Validation Documentation](validation/) - Comprehensive validation results
- [User Guide - Validation Results](USER_GUIDE.md#validation-results) - User-friendly summary
- `../tests/validation/` - Validation scripts and test data

### Version History

**Current Version**: 1.0.0
- ✅ All VBA methods implemented
- ✅ Comprehensive validation complete
- ✅ Production-ready
- ✅ 346 tests passing

---

## Support and Contributing

### Getting Help

- **Documentation**: See [User Guide](USER_GUIDE.md) for usage examples
- **Issues**: Report bugs on GitHub
- **Discussions**: Ask questions in GitHub Discussions

### Contributing

Contributions are welcome! See `CONTRIBUTING.md` for guidelines.

### License

MIT License - See `LICENSE` file for details.
