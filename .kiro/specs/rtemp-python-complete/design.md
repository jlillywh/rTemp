# Design Document: rTemp Python Complete Implementation

## Overview

This design document describes the architecture and implementation approach for a complete Python port of the rTemp water temperature model. The system will calculate response temperature of water bodies using a comprehensive heat budget approach with multiple configurable calculation methods for solar radiation, longwave radiation, and wind functions.

The implementation will be organized into modular components that separate concerns: solar position calculations, atmospheric radiation models, heat flux calculations, and the main model orchestration. This modular design ensures maintainability, testability, and allows users to easily select different calculation methods.

## Architecture

### High-Level Architecture

The system follows a layered architecture:

1. **Data Layer**: Input validation, data preprocessing, and output formatting
2. **Physics Layer**: Core calculation modules for solar, atmospheric, and heat flux physics
3. **Model Layer**: Orchestration of calculations and state management
4. **Configuration Layer**: Parameter management and method selection

### Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     RTempModel (Main)                        │
│  - Configuration management                                  │
│  - Timestep iteration                                        │
│  - State management (water temp, sediment temp)             │
└────────────┬────────────────────────────────────────────────┘
             │
             ├──────────────────────────────────────────────────┐
             │                                                   │
┌────────────▼──────────┐  ┌──────────────▼─────────────┐     │
│   SolarCalculator     │  │  AtmosphericRadiation      │     │
│  - NOAA position      │  │  - Longwave models         │     │
│  - Sunrise/sunset     │  │  - Cloud corrections       │     │
│  - Multiple models    │  │  - Emissivity calcs        │     │
└───────────────────────┘  └────────────────────────────┘     │
                                                                │
┌───────────────────────────────────────────────────────┐     │
│              HeatFluxCalculator                        │◄────┘
│  - Evaporation                                         │
│  - Convection                                          │
│  - Sediment exchange                                   │
│  - Groundwater exchange                                │
└────────────┬──────────────────────────────────────────┘
             │
┌────────────▼──────────┐
│   HelperFunctions     │
│  - Vapor pressure     │
│  - Unit conversions   │
│  - Wind adjustments   │
└───────────────────────┘
```


## Components and Interfaces

### 1. SolarCalculator Module

**Purpose**: Calculate solar position and radiation using multiple methods

**Classes**:
- `NOAASolarPosition`: NOAA algorithm implementation
- `SolarRadiationBras`: Bras atmospheric attenuation model
- `SolarRadiationBird`: Bird & Hulstrom clear sky model
- `SolarRadiationRyanStolz`: Ryan-Stolzenbach model
- `SolarRadiationIqbal`: Iqbal atmospheric transmittance model

**Key Methods**:
```python
class NOAASolarPosition:
    @staticmethod
    def calc_julian_day(year: int, month: int, day: int) -> float
    
    @staticmethod
    def calc_solar_position(lat: float, lon: float, dt: datetime, 
                           timezone: float, dlstime: int) -> Tuple[float, float, float]
        # Returns: (azimuth, elevation, earth_radius_vector)
    
    @staticmethod
    def calc_sunrise(lat: float, lon: float, year: int, month: int, 
                    day: int, timezone: float, dlstime: int) -> float
    
    @staticmethod
    def calc_sunset(lat: float, lon: float, year: int, month: int, 
                   day: int, timezone: float, dlstime: int) -> float

class SolarRadiationBras:
    @staticmethod
    def calculate(elevation: float, earth_sun_distance: float, 
                 turbidity: float) -> float
        # Returns: clear sky radiation in W/m²

class SolarRadiationBird:
    @staticmethod
    def calculate(zenith: float, earth_sun_distance: float, 
                 pressure_mb: float, ozone_cm: float, water_cm: float,
                 aod_500nm: float, aod_380nm: float, forward_scatter: float,
                 albedo: float) -> Dict[str, float]
        # Returns: {direct_beam, direct_hz, global_hz, diffuse_hz}
```

### 2. AtmosphericRadiation Module

**Purpose**: Calculate longwave atmospheric radiation using multiple emissivity models

**Classes**:
- `LongwaveEmissivity`: Base class for emissivity calculations
- `EmissivityBrunt`: Brunt 1932 method
- `EmissivityBrutsaert`: Brutsaert 1982 method
- `EmissivitySatterlund`: Satterlund 1979 method
- `EmissivityIdsoJackson`: Idso-Jackson 1969 method
- `EmissivitySwinbank`: Swinbank 1963 method
- `EmissivityKoberg`: Koberg 1964 method

**Key Methods**:
```python
class LongwaveEmissivity:
    @abstractmethod
    def calculate(self, air_temp_c: float, vapor_pressure_mmhg: float, 
                 cloud_cover: float, **kwargs) -> float
        # Returns: atmospheric emissivity (0-1)

class LongwaveRadiation:
    @staticmethod
    def calculate_atmospheric(emissivity: float, air_temp_c: float,
                             cloud_cover: float, cloud_method: str,
                             kcl3: float, kcl4: float) -> float
        # Returns: longwave atmospheric radiation in cal/cm²/day
    
    @staticmethod
    def calculate_back_radiation(water_temp_c: float) -> float
        # Returns: longwave back radiation in cal/cm²/day
```

### 3. WindFunction Module

**Purpose**: Calculate wind function for evaporation and convection

**Classes**:
- `WindFunction`: Base class
- `WindFunctionBradyGravesGeyer`: Default method
- `WindFunctionMarcianoHarbeck`: Lake Hefner method
- `WindFunctionRyanHarleman`: Virtual temperature method
- `WindFunctionEastMesa`: Modified method
- `WindFunctionHelfrich`: Recalibrated Ryan-Harleman

**Key Methods**:
```python
class WindFunction:
    @abstractmethod
    def calculate(self, wind_speed: float, air_temp: float, 
                 water_temp: float, vapor_pressure_air: float,
                 vapor_pressure_water: float) -> float
        # Returns: wind function in cal/cm²/day/mmHg

class WindAdjustment:
    @staticmethod
    def adjust_for_height(wind_speed: float, measured_height: float,
                         target_height: float) -> float
        # Returns: adjusted wind speed in m/s
```


### 4. HeatFluxCalculator Module

**Purpose**: Calculate all heat flux components

**Key Methods**:
```python
class HeatFluxCalculator:
    @staticmethod
    def calculate_evaporation(wind_function: float, 
                             vapor_pressure_water: float,
                             vapor_pressure_air: float) -> float
        # Returns: evaporation flux in cal/cm²/day
    
    @staticmethod
    def calculate_convection(wind_function: float, water_temp: float,
                            air_temp: float, bowen_ratio: float) -> float
        # Returns: convection flux in cal/cm²/day
    
    @staticmethod
    def calculate_sediment_conduction(water_temp: float, sediment_temp: float,
                                     thermal_conductivity: float,
                                     sediment_thickness: float) -> float
        # Returns: sediment conduction flux in cal/cm²/day
    
    @staticmethod
    def calculate_hyporheic_exchange(water_temp: float, sediment_temp: float,
                                    exchange_rate: float) -> float
        # Returns: hyporheic exchange flux in cal/cm²/day
    
    @staticmethod
    def calculate_groundwater_flux(water_temp: float, groundwater_temp: float,
                                  inflow_rate: float) -> float
        # Returns: groundwater flux in cal/cm²/day
```

### 5. HelperFunctions Module

**Purpose**: Utility functions for atmospheric and unit calculations

**Key Methods**:
```python
class AtmosphericHelpers:
    @staticmethod
    def saturation_vapor_pressure(temp_c: float) -> float
        # Returns: saturation vapor pressure in mmHg
    
    @staticmethod
    def dewpoint_from_rh(air_temp: float, relative_humidity: float) -> float
        # Returns: dewpoint temperature in °C
    
    @staticmethod
    def relative_humidity_from_dewpoint(air_temp: float, dewpoint: float) -> float
        # Returns: relative humidity as fraction
    
    @staticmethod
    def pressure_from_altitude(altitude_m: float) -> float
        # Returns: atmospheric pressure in mb
    
    @staticmethod
    def water_vapor_saturation_lowe(temp_k: float, ice: bool = False) -> float
        # Returns: saturated vapor pressure in hPa

class UnitConversions:
    @staticmethod
    def watts_m2_to_cal_cm2_day(watts_m2: float) -> float
    
    @staticmethod
    def cal_cm2_day_to_watts_m2(cal_cm2_day: float) -> float
    
    @staticmethod
    def deg_to_rad(degrees: float) -> float
    
    @staticmethod
    def rad_to_deg(radians: float) -> float
    
    @staticmethod
    def celsius_to_kelvin(celsius: float) -> float
    
    @staticmethod
    def meters_to_centimeters(meters: float) -> float
```

### 6. InputValidator Module

**Purpose**: Validate and sanitize input data

**Key Methods**:
```python
class InputValidator:
    @staticmethod
    def validate_site_parameters(params: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]
        # Returns: (validated_params, warnings)
    
    @staticmethod
    def validate_meteorological_data(data: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]
        # Returns: (validated_data, warnings)
    
    @staticmethod
    def check_timestep(current_time: datetime, previous_time: datetime) -> Optional[str]
        # Returns: warning message if timestep is problematic
```

### 7. RTempModel Class (Main Orchestrator)

**Purpose**: Main model class that orchestrates all calculations

**Key Methods**:
```python
class RTempModel:
    def __init__(self, config: ModelConfiguration):
        # Initialize with configuration
    
    def run(self, met_data: pd.DataFrame) -> pd.DataFrame:
        # Main execution loop
        # Returns: DataFrame with results
    
    def _calculate_timestep(self, met_row: pd.Series, 
                           previous_state: ModelState) -> ModelState:
        # Calculate one timestep
    
    def _check_stability(self, new_temp: float, old_temp: float) -> None:
        # Check for numerical instability
    
    def export_results(self, output_path: str, include_diagnostics: bool = False):
        # Export results to file
```


## Data Models

### ModelConfiguration

Configuration object containing all model parameters and method selections.

```python
@dataclass
class ModelConfiguration:
    # Site parameters
    latitude: float
    longitude: float
    elevation: float  # meters
    timezone: float  # hours from UTC
    daylight_savings: int  # 0 or 1
    
    # Initial conditions
    initial_water_temp: float  # °C
    initial_sediment_temp: float  # °C
    minimum_temperature: float  # °C
    
    # Water body parameters
    water_depth: float  # meters
    effective_shade: float  # 0-1
    wind_height: float  # meters
    effective_wind_factor: float  # 0-1
    
    # Sediment parameters
    sediment_thermal_conductivity: float  # W/m/°C
    sediment_thermal_diffusivity: float  # cm²/s
    sediment_thickness: float  # cm
    hyporheic_exchange_rate: float  # cm/day
    
    # Groundwater parameters
    groundwater_temperature: float  # °C
    groundwater_inflow: float  # cm/day
    
    # Method selections
    solar_method: str  # 'Bras', 'Bird', 'Ryan-Stolzenbach', 'Iqbal'
    longwave_method: str  # 'Brunt', 'Brutsaert', 'Satterlund', etc.
    wind_function_method: str  # 'Brady-Graves-Geyer', 'Marciano-Harbeck', etc.
    
    # Model parameters
    atmospheric_turbidity: float  # for Bras (2-5)
    atmospheric_transmission_coeff: float  # for Ryan-Stolzenbach (0.7-0.91)
    brutsaert_coefficient: float  # for Brutsaert longwave
    
    # Cloud correction parameters
    solar_cloud_kcl1: float  # 0-1
    solar_cloud_kcl2: float  # 0-5
    longwave_cloud_method: str  # 'Eqn 1' or 'Eqn 2'
    longwave_cloud_kcl3: float  # 0-1
    longwave_cloud_kcl4: float  # 0-5
    
    # Stability checking
    stability_criteria: float  # °C
    
    # Output options
    enable_diagnostics: bool
```

### ModelState

State object tracking current conditions at each timestep.

```python
@dataclass
class ModelState:
    datetime: datetime
    water_temperature: float  # °C
    sediment_temperature: float  # °C
    water_depth: float  # meters (can vary with time)
    effective_shade: float  # 0-1 (can vary with time)
```

### MeteorologicalData

Input meteorological data structure.

```python
@dataclass
class MeteorologicalData:
    datetime: datetime
    air_temperature: float  # °C
    dewpoint_temperature: float  # °C
    wind_speed: float  # m/s
    cloud_cover: float  # 0-1
    
    # Optional measured solar radiation
    solar_radiation: Optional[float] = None  # W/m²
    
    # Optional Bird-Hulstrom parameters
    pressure_mb: Optional[float] = None
    ozone_cm: Optional[float] = None
    water_vapor_cm: Optional[float] = None
    aod_500nm: Optional[float] = None
    aod_380nm: Optional[float] = None
    forward_scatter: Optional[float] = None
    ground_albedo: Optional[float] = None
    
    # Optional Iqbal parameters
    visibility_km: Optional[float] = None
    
    # Optional time-varying parameters
    water_depth_override: Optional[float] = None  # meters
    effective_shade_override: Optional[float] = None  # 0-1
```

### HeatFluxComponents

Output structure for heat flux breakdown.

```python
@dataclass
class HeatFluxComponents:
    solar_radiation: float  # W/m²
    longwave_atmospheric: float  # W/m²
    longwave_back: float  # W/m²
    evaporation: float  # W/m²
    convection: float  # W/m²
    sediment_conduction: float  # W/m²
    hyporheic_exchange: float  # W/m²
    groundwater: float  # W/m²
    net_flux: float  # W/m²
```

### SolarPositionResult

Output structure for solar position calculations.

```python
@dataclass
class SolarPositionResult:
    azimuth: float  # degrees from north
    elevation: float  # degrees above horizon
    zenith: float  # degrees from vertical
    earth_sun_distance: float  # AU
    sunrise_time: float  # fraction of day
    sunset_time: float  # fraction of day
    photoperiod: float  # hours
```

### DiagnosticOutput

Extended output for debugging and analysis.

```python
@dataclass
class DiagnosticOutput:
    # Solar diagnostics
    solar_potential: float  # W/m² before corrections
    solar_after_cloud: float  # W/m² after cloud correction
    solar_after_shade: float  # W/m² after shade correction
    albedo: float  # surface reflection fraction
    
    # Atmospheric diagnostics
    vapor_pressure_water: float  # mmHg
    vapor_pressure_air: float  # mmHg
    atmospheric_emissivity: float  # 0-1
    
    # Wind diagnostics
    wind_speed_2m: float  # m/s
    wind_speed_7m: float  # m/s
    wind_function: float  # cal/cm²/day/mmHg
    
    # Temperature change rates
    water_temp_change_rate: float  # °C/day
    sediment_temp_change_rate: float  # °C/day
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Julian Day Calculation Consistency
*For any* valid calendar date (year, month, day), calculating the Julian Day and then converting back to calendar date should produce the original date.
**Validates: Requirements 1.1**

### Property 2: Solar Position Determinism
*For any* location (latitude, longitude), datetime, and timezone, calculating solar position twice with identical inputs should produce identical results (azimuth, elevation, earth-sun distance).
**Validates: Requirements 1.2-1.16**

### Property 3: Sunrise Before Sunset
*For any* location and date where both sunrise and sunset occur, the sunrise time should be less than the sunset time.
**Validates: Requirements 2.1-2.9**

### Property 4: Solar Noon Between Sunrise and Sunset
*For any* location and date, solar noon should occur between sunrise and sunset times.
**Validates: Requirements 2.7**

### Property 5: Solar Radiation Non-Negativity
*For any* solar radiation calculation method and inputs, the calculated radiation should be greater than or equal to zero.
**Validates: Requirements 3.1-3.19**

### Property 6: Solar Radiation Zero at Night
*For any* solar radiation calculation when solar elevation is zero or negative, the calculated radiation should equal zero.
**Validates: Requirements 3.16**

### Property 7: Cloud Cover Reduces Solar Radiation
*For any* solar radiation calculation, increasing cloud cover (0 to 1) should monotonically decrease the calculated radiation.
**Validates: Requirements 3.17**

### Property 8: Shade Reduces Solar Radiation
*For any* solar radiation calculation, increasing effective shade (0 to 1) should monotonically decrease the calculated radiation.
**Validates: Requirements 3.18**

### Property 9: Longwave Emissivity Bounds
*For any* longwave radiation emissivity calculation method and inputs, the calculated emissivity should be between 0 and 1 inclusive.
**Validates: Requirements 4.1-4.6**

### Property 10: Longwave Radiation Increases with Temperature
*For any* longwave radiation calculation method, increasing air temperature should monotonically increase atmospheric longwave radiation.
**Validates: Requirements 4.10**

### Property 11: Wind Function Positivity
*For any* wind function calculation method and non-negative wind speed, the calculated wind function should be positive.
**Validates: Requirements 5.1-5.5**

### Property 12: Wind Function Increases with Wind Speed
*For any* wind function calculation method, increasing wind speed should monotonically increase the wind function value.
**Validates: Requirements 5.1-5.5**

### Property 13: Energy Conservation in Heat Budget
*For any* timestep calculation, the sum of all heat flux components should equal the rate of temperature change multiplied by heat capacity and depth.
**Validates: Requirements 6.8**

### Property 14: Unit Conversion Round Trip
*For any* numeric value and unit conversion pair (e.g., W/m² to cal/cm²/day), converting forward and then backward should produce the original value within numerical precision.
**Validates: Requirements 7.1-7.8**

### Property 15: Invalid Inputs Rejected
*For any* input parameter that violates validation rules (e.g., negative depth, shade > 1), the system should reject the input or issue a warning.
**Validates: Requirements 8.1-8.15**

### Property 16: Missing Data Handling
*For any* meteorological data point with missing values (≤ -999), the system should substitute default values and issue warnings.
**Validates: Requirements 8.11-8.15**

### Property 17: Timestep Monotonicity
*For any* sequence of meteorological data, timestamps should be monotonically increasing (no time travel).
**Validates: Requirements 9.3**

### Property 18: Temperature Minimum Enforcement
*For any* calculated water or sediment temperature, the final value should be greater than or equal to the specified minimum temperature.
**Validates: Requirements 11.1-11.3**

### Property 19: Vapor Pressure Monotonicity
*For any* temperature, saturation vapor pressure should monotonically increase with temperature.
**Validates: Requirements 12.1**

### Property 20: Dewpoint-RH Round Trip
*For any* air temperature and relative humidity, calculating dewpoint and then calculating RH from that dewpoint should produce the original RH within numerical precision.
**Validates: Requirements 12.2-12.3**

### Property 21: Configuration Completeness
*For any* model configuration, all required parameters should be present and within valid ranges before model execution begins.
**Validates: Requirements 13.1-13.10**

### Property 22: Output Completeness
*For any* model execution, the output DataFrame should contain all required columns (datetime, water_temp, sediment_temp, heat fluxes).
**Validates: Requirements 16.1-16.7**

### Property 23: Diagnostic Output Completeness
*For any* model execution with diagnostics enabled, the diagnostic output should contain all specified diagnostic fields.
**Validates: Requirements 14.1-14.8**

### Property 24: Edge Case Stability
*For any* edge case input (e.g., solar elevation = 0, latitude = 89.8°), the system should produce valid numeric output without errors or NaN values.
**Validates: Requirements 17.1-17.11**


## Error Handling

### Input Validation Errors

**Strategy**: Fail fast with clear error messages for invalid configuration

- Invalid depth (≤ 0): Raise `ValueError` with message "Water depth must be greater than zero"
- Invalid shade (< 0 or > 1): Raise `ValueError` with message "Effective shade must be between 0 and 1"
- Invalid wind height (≤ 0): Raise `ValueError` with message "Wind height must be greater than zero"
- Invalid method selection: Raise `ValueError` with message listing valid options

### Data Quality Warnings

**Strategy**: Issue warnings but continue execution with corrected values

- Missing meteorological data: Log warning and substitute default value
- Negative groundwater inflow: Log warning and set to zero
- Timestep > 2 hours: Log warning about potential accuracy issues
- Timestep > 4 hours: Log warning and reset temperatures

### Numerical Stability Errors

**Strategy**: Halt execution with diagnostic information

- Temperature change exceeds stability criteria: Raise `RuntimeError` with message including:
  - Current timestep
  - Temperature change magnitude
  - Recommendation to reduce timestep or resample data

### Edge Case Handling

**Strategy**: Gracefully handle edge cases with appropriate defaults

- Solar elevation ≤ 0: Set all solar radiation to zero
- Extreme latitudes (> 89.8°): Clamp to ±89.8°
- Cosine values outside [-1, 1]: Clamp to valid range
- Division by zero: Check denominators and handle appropriately

### Logging Strategy

Use Python's `logging` module with the following levels:

- `ERROR`: Critical failures that halt execution
- `WARNING`: Data quality issues that are corrected automatically
- `INFO`: Normal execution milestones (start, progress, completion)
- `DEBUG`: Detailed calculation information for troubleshooting

## Testing Strategy

### Unit Testing

**Framework**: pytest

**Coverage Goals**: 
- 100% coverage of all calculation functions
- All edge cases explicitly tested
- All error conditions tested

**Key Unit Test Categories**:

1. **Solar Position Tests**
   - Test Julian Day calculation against known values
   - Test solar position against NOAA reference data
   - Test sunrise/sunset calculations for various latitudes
   - Test edge cases (polar regions, equator, solstices, equinoxes)

2. **Solar Radiation Tests**
   - Test each model (Bras, Bird, Ryan-Stolz, Iqbal) independently
   - Test that radiation is zero when elevation ≤ 0
   - Test cloud cover and shade corrections
   - Test albedo calculations

3. **Longwave Radiation Tests**
   - Test each emissivity model independently
   - Test cloud correction methods
   - Test that emissivity is bounded [0, 1]
   - Test Stefan-Boltzmann calculations

4. **Wind Function Tests**
   - Test each wind function method independently
   - Test wind height adjustments
   - Test virtual temperature calculations

5. **Heat Flux Tests**
   - Test each flux component independently
   - Test energy conservation
   - Test temperature change calculations

6. **Helper Function Tests**
   - Test vapor pressure calculations
   - Test unit conversions (including round trips)
   - Test atmospheric property calculations

7. **Validation Tests**
   - Test all input validation rules
   - Test warning generation
   - Test error message content

### Property-Based Testing

**Framework**: Hypothesis

**Configuration**: Minimum 100 iterations per property test

**Key Property Tests**:

1. **Property Test: Julian Day Round Trip** (Property 1)
   - Generate random valid dates
   - Convert to Julian Day and back
   - Assert original date is recovered

2. **Property Test: Solar Position Determinism** (Property 2)
   - Generate random location, datetime, timezone
   - Calculate solar position twice
   - Assert results are identical

3. **Property Test: Sunrise Before Sunset** (Property 3)
   - Generate random location and date
   - Calculate sunrise and sunset
   - Assert sunrise < sunset (when both exist)

4. **Property Test: Solar Radiation Non-Negativity** (Property 5)
   - Generate random inputs for each solar model
   - Calculate radiation
   - Assert result ≥ 0

5. **Property Test: Cloud Cover Monotonicity** (Property 7)
   - Generate random base inputs
   - Calculate radiation at cloud_cover = 0 and cloud_cover = 1
   - Assert radiation decreases

6. **Property Test: Emissivity Bounds** (Property 9)
   - Generate random inputs for each emissivity model
   - Calculate emissivity
   - Assert 0 ≤ emissivity ≤ 1

7. **Property Test: Wind Function Positivity** (Property 11)
   - Generate random non-negative wind speeds
   - Calculate wind function
   - Assert result > 0

8. **Property Test: Unit Conversion Round Trip** (Property 14)
   - Generate random numeric values
   - Apply forward and backward conversion
   - Assert original value recovered within tolerance

9. **Property Test: Temperature Minimum Enforcement** (Property 18)
   - Generate random inputs that might produce low temperatures
   - Run model timestep
   - Assert final temperature ≥ minimum

10. **Property Test: Vapor Pressure Monotonicity** (Property 19)
    - Generate random temperature pairs where T1 < T2
    - Calculate vapor pressures
    - Assert VP(T1) < VP(T2)

**Property Test Annotations**:
Each property-based test must include a comment with the format:
```python
# Feature: rtemp-python-complete, Property X: [property description]
# Validates: Requirements Y.Z
```

### Integration Testing

**Purpose**: Test complete model execution with realistic data

**Test Cases**:

1. **Simple Scenario Test**
   - Single day of hourly data
   - All default parameters
   - Verify output structure and completeness

2. **Multi-Day Scenario Test**
   - One week of hourly data
   - Verify temperature trends are reasonable
   - Verify no NaN or infinite values

3. **Variable Timestep Test**
   - Data with irregular timesteps
   - Verify warnings are issued appropriately
   - Verify calculations handle variable timesteps

4. **All Methods Test**
   - Run with each combination of solar/longwave/wind methods
   - Verify all combinations execute successfully
   - Verify results are reasonable

5. **Edge Case Integration Test**
   - Data including extreme conditions (very hot, very cold, high wind, etc.)
   - Verify model remains stable
   - Verify edge case handling works in context

### VBA Comparison Testing

**Purpose**: Validate that Python implementation matches VBA results

**Approach**:
1. Create test dataset with known VBA outputs
2. Run Python implementation with identical inputs
3. Compare outputs within tolerance:
   - Solar position: ±0.01°
   - Solar radiation: ±0.1 W/m²
   - Heat fluxes: ±0.1 W/m²
   - Temperature: ±0.01°C

**Test Data**:
- Use actual meteorological data from reference sites
- Include variety of conditions (seasons, weather, locations)
- Document any known differences and their causes


## Implementation Notes

### Module Organization

```
rtemp/
├── __init__.py
├── model.py                    # RTempModel main class
├── config.py                   # ModelConfiguration and data models
├── solar/
│   ├── __init__.py
│   ├── position.py            # NOAASolarPosition
│   ├── radiation_bras.py      # SolarRadiationBras
│   ├── radiation_bird.py      # SolarRadiationBird
│   ├── radiation_ryan.py      # SolarRadiationRyanStolz
│   └── radiation_iqbal.py     # SolarRadiationIqbal
├── atmospheric/
│   ├── __init__.py
│   ├── longwave.py            # LongwaveRadiation
│   └── emissivity.py          # All emissivity models
├── wind/
│   ├── __init__.py
│   ├── functions.py           # All wind function models
│   └── adjustment.py          # WindAdjustment
├── heat_flux/
│   ├── __init__.py
│   └── calculator.py          # HeatFluxCalculator
├── utils/
│   ├── __init__.py
│   ├── atmospheric.py         # AtmosphericHelpers
│   ├── conversions.py         # UnitConversions
│   └── validation.py          # InputValidator
└── constants.py               # Physical constants

tests/
├── unit/
│   ├── test_solar_position.py
│   ├── test_solar_radiation.py
│   ├── test_longwave.py
│   ├── test_wind.py
│   ├── test_heat_flux.py
│   ├── test_helpers.py
│   └── test_validation.py
├── property/
│   ├── test_properties_solar.py
│   ├── test_properties_atmospheric.py
│   ├── test_properties_conversions.py
│   └── test_properties_model.py
├── integration/
│   ├── test_model_execution.py
│   └── test_vba_comparison.py
└── fixtures/
    ├── reference_data.py
    └── test_data/
```

### Dependencies

**Core Dependencies**:
- `numpy>=1.20.0`: Numerical calculations
- `pandas>=1.3.0`: Data handling
- `python-dateutil>=2.8.0`: Date/time handling

**Development Dependencies**:
- `pytest>=7.0.0`: Unit testing framework
- `hypothesis>=6.0.0`: Property-based testing
- `pytest-cov>=3.0.0`: Coverage reporting
- `black>=22.0.0`: Code formatting
- `mypy>=0.950`: Type checking
- `flake8>=4.0.0`: Linting

### Performance Considerations

1. **Vectorization**: Use numpy vectorized operations where possible for batch calculations
2. **Caching**: Cache expensive calculations (e.g., solar position) when processing multiple timesteps
3. **Lazy Evaluation**: Only calculate diagnostic outputs when requested
4. **Memory Management**: Process large datasets in chunks if needed

### Backward Compatibility

The implementation should maintain compatibility with the VBA version's:
- Input data format (CSV with specific columns)
- Output data format
- Parameter names and units
- Calculation methods and results

### Documentation Requirements

1. **API Documentation**: 
   - Docstrings for all public classes and methods
   - Type hints for all parameters and return values
   - Examples in docstrings

2. **User Guide**:
   - Installation instructions
   - Quick start tutorial
   - Configuration guide
   - Method selection guide
   - Troubleshooting section

3. **Developer Guide**:
   - Architecture overview
   - Adding new calculation methods
   - Testing guidelines
   - Contributing guidelines

### Future Enhancements

Potential future additions (not in current scope):

1. **Parallel Processing**: Support for parallel execution of multiple scenarios
2. **Calibration Tools**: Automated parameter calibration against observed data
3. **Sensitivity Analysis**: Built-in sensitivity analysis tools
4. **Visualization**: Plotting utilities for results
5. **Additional Models**: Support for additional solar/longwave/wind models
6. **Uncertainty Quantification**: Monte Carlo simulation support
7. **Database Integration**: Direct database input/output
8. **Web API**: REST API for model execution

## References

### Scientific References

1. **NOAA Solar Position Algorithm**: 
   - Reda, I., and A. Andreas (2004). Solar position algorithm for solar radiation applications. Solar Energy, 76(5), 577-589.

2. **Bras Solar Model**:
   - Bras, R.L. (1990). Hydrology: An Introduction to Hydrologic Science. Addison-Wesley.

3. **Bird & Hulstrom Model**:
   - Bird, R.E., and R.L. Hulstrom (1981). A Simplified Clear Sky Model for Direct and Diffuse Insolation on Horizontal Surfaces. SERI Technical Report SERI/TR-642-761.

4. **Ryan-Stolzenbach Model**:
   - Ryan, P.J., and K.D. Stolzenbach (1972). Engineering Aspects of Heat Disposal from Power Generation. MIT Press.

5. **Iqbal Model**:
   - Iqbal, M. (1983). An Introduction to Solar Radiation. Academic Press.

6. **Longwave Radiation Models**:
   - Brunt, D. (1932). Notes on radiation in the atmosphere. Quarterly Journal of the Royal Meteorological Society, 58, 389-420.
   - Brutsaert, W. (1982). Evaporation into the Atmosphere. D. Reidel Publishing Company.
   - Satterlund, D.R. (1979). An improved equation for estimating long-wave radiation from the atmosphere. Water Resources Research, 15(6), 1649-1650.

7. **Wind Functions**:
   - Brady, D.K., W.L. Graves, and J.C. Geyer (1969). Surface Heat Exchange at Power Plant Cooling Lakes. Edison Electric Institute.
   - Ryan, P.J., and D.R.F. Harleman (1973). An Analytical and Experimental Study of Transient Cooling Pond Behavior. MIT.

### Software References

1. **Original VBA Implementation**: rTemp by Greg Pelletier, Washington State Department of Ecology
2. **NOAA Solar Calculator**: https://www.esrl.noaa.gov/gmd/grad/solcalc/
3. **Hypothesis Documentation**: https://hypothesis.readthedocs.io/
4. **Pytest Documentation**: https://docs.pytest.org/

