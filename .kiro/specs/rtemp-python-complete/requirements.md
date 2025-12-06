# Requirements Document: rTemp Python Complete Implementation

## Introduction

This document specifies the requirements for a complete Python implementation of the rTemp water temperature model, which calculates response temperature of water bodies based on meteorological inputs and site characteristics. The implementation must replicate all functionality from the original VBA code, including multiple solar radiation models, longwave radiation methods, wind functions, and comprehensive heat budget calculations.

## Glossary

- **rTemp Model**: Response Temperature model - calculates water temperature based on heat budget
- **Heat Budget**: The balance of energy fluxes affecting water temperature
- **Solar Radiation**: Shortwave radiation from the sun (Jsnt)
- **Longwave Radiation**: Thermal infrared radiation from atmosphere (longat) and water surface (back)
- **Evaporation Flux**: Heat loss due to water evaporation (evap)
- **Convection Flux**: Heat exchange between water and air (conv)
- **Sediment Flux**: Heat exchange with sediments (Jsedcond)
- **Hyporheic Exchange**: Heat exchange through groundwater-surface water interaction
- **Solar Elevation**: Angle of sun above horizon in degrees
- **Solar Azimuth**: Compass direction of sun in degrees from north
- **Zenith Angle**: Angle from vertical to sun position (90° - elevation)
- **Julian Day**: Day number in year (1-366)
- **Albedo**: Fraction of solar radiation reflected from water surface
- **Transmittance**: Fraction of radiation passing through atmosphere
- **AU**: Astronomical Unit - mean Earth-Sun distance
- **NOAA Algorithm**: National Oceanic and Atmospheric Administration solar position algorithm
- **Timestep**: Time interval between meteorological data points in days
- **Response Temperature**: Calculated water temperature in degrees Celsius
- **Sediment Temperature**: Temperature of sediment layer in degrees Celsius
- **Wind Function**: Empirical relationship between wind speed and evaporation/convection

## Requirements

### Requirement 1

**User Story:** As a water quality modeler, I want to calculate solar position accurately using the NOAA algorithm, so that solar radiation calculations reflect the actual sun position at any date, time, and location.

#### Acceptance Criteria

1. WHEN the system calculates solar position THEN the system SHALL compute Julian Day from calendar date using the standard astronomical formula
2. WHEN the system calculates solar position THEN the system SHALL compute time in Julian centuries since J2000.0 epoch
3. WHEN the system calculates solar position THEN the system SHALL calculate geometric mean longitude of the sun with proper modulo 360 handling
4. WHEN the system calculates solar position THEN the system SHALL calculate geometric mean anomaly of the sun
5. WHEN the system calculates solar position THEN the system SHALL calculate eccentricity of Earth's orbit
6. WHEN the system calculates solar position THEN the system SHALL calculate equation of center for the sun
7. WHEN the system calculates solar position THEN the system SHALL calculate sun's true longitude and apparent longitude
8. WHEN the system calculates solar position THEN the system SHALL calculate mean obliquity of the ecliptic and obliquity correction
9. WHEN the system calculates solar position THEN the system SHALL calculate sun's right ascension and declination
10. WHEN the system calculates solar position THEN the system SHALL calculate equation of time in minutes
11. WHEN the system calculates solar position THEN the system SHALL calculate true solar time accounting for longitude and timezone
12. WHEN the system calculates solar position THEN the system SHALL calculate hour angle from true solar time
13. WHEN the system calculates solar position THEN the system SHALL calculate solar zenith angle from latitude, declination, and hour angle
14. WHEN the system calculates solar position THEN the system SHALL calculate solar elevation with atmospheric refraction correction
15. WHEN the system calculates solar position THEN the system SHALL calculate solar azimuth from north
16. WHEN the system calculates solar position THEN the system SHALL calculate Earth-Sun distance in astronomical units
17. WHEN the system processes longitude input THEN the system SHALL convert negative western hemisphere values to positive for internal calculations
18. WHEN the system processes timezone input THEN the system SHALL convert to positive hours for western hemisphere
19. WHEN the system processes daylight savings time THEN the system SHALL adjust time by the specified offset in hours

### Requirement 2

**User Story:** As a water quality modeler, I want to calculate sunrise, sunset, and solar noon times, so that I can determine photoperiod and validate solar calculations.

#### Acceptance Criteria

1. WHEN the system calculates sunrise THEN the system SHALL compute hour angle at sunrise for the given latitude and solar declination
2. WHEN the system calculates sunrise THEN the system SHALL use iterative refinement with two passes for accuracy
3. WHEN the system calculates sunrise THEN the system SHALL return sunrise time in local time as fraction of day
4. WHEN the system calculates sunset THEN the system SHALL compute hour angle at sunset for the given latitude and solar declination
5. WHEN the system calculates sunset THEN the system SHALL use iterative refinement with two passes for accuracy
6. WHEN the system calculates sunset THEN the system SHALL return sunset time in local time as fraction of day
7. WHEN the system calculates solar noon THEN the system SHALL compute time of solar noon in local time as fraction of day
8. WHEN the system calculates sunrise or sunset for latitudes greater than 89.8 degrees THEN the system SHALL clamp latitude to 89.8 degrees
9. WHEN the system calculates sunrise or sunset for latitudes less than -89.8 degrees THEN the system SHALL clamp latitude to -89.8 degrees

### Requirement 3

**User Story:** As a water quality modeler, I want multiple solar radiation models available, so that I can choose the most appropriate method for my location and data availability.

#### Acceptance Criteria

1. WHEN the system calculates solar radiation using Bras method THEN the system SHALL compute extraterrestrial radiation corrected for Earth-Sun distance
2. WHEN the system calculates solar radiation using Bras method THEN the system SHALL compute optical air mass using Kasten-Young formula
3. WHEN the system calculates solar radiation using Bras method THEN the system SHALL compute molecular scattering coefficient
4. WHEN the system calculates solar radiation using Bras method THEN the system SHALL apply atmospheric turbidity factor to calculate clear-sky radiation
5. WHEN the system calculates solar radiation using Bird-Hulstrom method THEN the system SHALL compute Rayleigh scattering transmittance
6. WHEN the system calculates solar radiation using Bird-Hulstrom method THEN the system SHALL compute ozone transmittance from ozone layer thickness
7. WHEN the system calculates solar radiation using Bird-Hulstrom method THEN the system SHALL compute uniformly mixed gases transmittance
8. WHEN the system calculates solar radiation using Bird-Hulstrom method THEN the system SHALL compute water vapor transmittance from precipitable water
9. WHEN the system calculates solar radiation using Bird-Hulstrom method THEN the system SHALL compute aerosol transmittance from aerosol optical depth
10. WHEN the system calculates solar radiation using Bird-Hulstrom method THEN the system SHALL compute direct beam, direct horizontal, diffuse, and global horizontal irradiance
11. WHEN the system calculates solar radiation using Ryan-Stolzenbach method THEN the system SHALL apply atmospheric transmission coefficient adjusted for elevation
12. WHEN the system calculates solar radiation using Ryan-Stolzenbach method THEN the system SHALL compute relative air mass corrected for site elevation
13. WHEN the system calculates solar radiation using Iqbal method THEN the system SHALL compute atmospheric transmittances for Rayleigh scattering, ozone, gases, water vapor, and aerosols
14. WHEN the system calculates solar radiation using Iqbal method THEN the system SHALL compute direct and diffuse irradiance components separately
15. WHEN the system calculates solar radiation using Iqbal method THEN the system SHALL compute multiple scattering between ground and atmosphere
16. WHEN solar elevation is zero or negative THEN the system SHALL set solar radiation to zero
17. WHEN the system applies cloud cover correction THEN the system SHALL reduce solar radiation using formula with user-specified KCL1 and KCL2 parameters
18. WHEN the system applies shade correction THEN the system SHALL reduce solar radiation by effective shade fraction
19. WHEN the system applies albedo correction THEN the system SHALL reduce solar radiation by surface reflection fraction calculated from Anderson method

### Requirement 4

**User Story:** As a water quality modeler, I want multiple longwave atmospheric radiation models available, so that I can accurately estimate atmospheric thermal radiation for different atmospheric conditions.

#### Acceptance Criteria

1. WHEN the system calculates longwave radiation using Brunt method THEN the system SHALL compute atmospheric emissivity from Brunt formula with vapor pressure
2. WHEN the system calculates longwave radiation using Brutsaert method THEN the system SHALL compute atmospheric emissivity from Brutsaert formula with configurable coefficient
3. WHEN the system calculates longwave radiation using Satterlund method THEN the system SHALL compute atmospheric emissivity from Satterlund exponential formula
4. WHEN the system calculates longwave radiation using Idso-Jackson method THEN the system SHALL compute atmospheric emissivity from air temperature only
5. WHEN the system calculates longwave radiation using Swinbank method THEN the system SHALL compute atmospheric emissivity from Swinbank formula
6. WHEN the system calculates longwave radiation using Koberg method THEN the system SHALL compute atmospheric emissivity using Koberg figure 34 interpolation
7. WHEN the system applies cloud cover correction to longwave radiation THEN the system SHALL use either Equation 1 or Equation 2 method as specified by user
8. WHEN the system applies cloud cover correction using Equation 1 THEN the system SHALL multiply clear-sky emissivity by factor with KCL3 and KCL4 parameters
9. WHEN the system applies cloud cover correction using Equation 2 THEN the system SHALL blend clear-sky and overcast emissivity using KCL3 and KCL4 parameters
10. WHEN the system calculates longwave atmospheric radiation THEN the system SHALL apply Stefan-Boltzmann law with air temperature in Kelvin
11. WHEN the system calculates longwave atmospheric radiation THEN the system SHALL reduce by surface reflection factor of 0.03
12. WHEN the system calculates longwave back radiation THEN the system SHALL apply Stefan-Boltzmann law with water temperature in Kelvin and water emissivity of 0.97

### Requirement 5

**User Story:** As a water quality modeler, I want multiple wind function methods available, so that I can accurately calculate evaporation and convection for different water body types and wind conditions.

#### Acceptance Criteria

1. WHEN the system calculates wind function using Brady-Graves-Geyer method THEN the system SHALL use formula with wind speed at 7 meter height
2. WHEN the system calculates wind function using Marciano-Harbeck method THEN the system SHALL use formula with wind speed at 7 meter height converted to miles per hour
3. WHEN the system calculates wind function using Ryan-Harleman method THEN the system SHALL use formula with wind speed at 2 meter height and virtual temperature difference
4. WHEN the system calculates wind function using East Mesa method THEN the system SHALL use formula combining virtual temperature and wind speed effects
5. WHEN the system calculates wind function using Helfrich method THEN the system SHALL use recalibrated Ryan-Harleman formula
6. WHEN the system adjusts wind speed for height THEN the system SHALL apply TVA exponential wind correction with exponent 0.15
7. WHEN the system adjusts wind speed for shelter THEN the system SHALL multiply by effective wind factor
8. WHEN the system calculates virtual temperature for wind functions THEN the system SHALL correct for vapor pressure effects

### Requirement 6

**User Story:** As a water quality modeler, I want comprehensive heat flux calculations, so that the model accurately represents all energy exchanges affecting water temperature.

#### Acceptance Criteria

1. WHEN the system calculates evaporation flux THEN the system SHALL compute as negative product of wind function and vapor pressure difference
2. WHEN the system calculates convection flux THEN the system SHALL compute as negative product of Bowen ratio, wind function, and temperature difference
3. WHEN the system calculates longwave back radiation THEN the system SHALL compute as negative Stefan-Boltzmann emission from water surface
4. WHEN the system calculates sediment conduction THEN the system SHALL compute heat flux based on temperature difference, thermal conductivity, and sediment thickness
5. WHEN the system calculates hyporheic exchange THEN the system SHALL compute heat flux based on temperature difference, water properties, and exchange rate
6. WHEN the system calculates groundwater flux THEN the system SHALL compute heat flux based on temperature difference, water properties, and groundwater inflow rate
7. WHEN the system sums heat fluxes THEN the system SHALL include solar, longwave atmospheric, longwave back, evaporation, convection, sediment conduction, hyporheic exchange, and groundwater fluxes
8. WHEN the system calculates temperature change THEN the system SHALL divide total heat flux by product of water density, specific heat, and water depth
9. WHEN the system calculates sediment temperature change THEN the system SHALL divide sediment heat flux by product of sediment density, specific heat, and sediment thickness

### Requirement 7

**User Story:** As a water quality modeler, I want proper unit conversions throughout the model, so that all calculations use consistent units and produce correct results.

#### Acceptance Criteria

1. WHEN the system converts solar radiation from watts per square meter to calories per square centimeter per day THEN the system SHALL divide by 4.183076 times 10000 divided by 86400
2. WHEN the system converts heat flux from calories per square centimeter per day to watts per square meter THEN the system SHALL multiply by 4.183076 times 10000 divided by 86400
3. WHEN the system converts water depth from meters to centimeters THEN the system SHALL multiply by 100
4. WHEN the system converts sediment thermal conductivity from watts per meter per degree Celsius to calories per second per centimeter per degree Celsius THEN the system SHALL divide by 4.183076 times 100
5. WHEN the system converts wind speed from meters per second to miles per hour THEN the system SHALL multiply by 3600 divided by 1609.344
6. WHEN the system converts temperature from Celsius to Kelvin THEN the system SHALL add 273.15
7. WHEN the system converts angles from degrees to radians THEN the system SHALL multiply by pi divided by 180
8. WHEN the system converts angles from radians to degrees THEN the system SHALL multiply by 180 divided by pi

### Requirement 8

**User Story:** As a water quality modeler, I want comprehensive input validation, so that the model detects invalid inputs and provides clear error messages.

#### Acceptance Criteria

1. WHEN water depth is less than or equal to zero THEN the system SHALL reject the input with error message
2. WHEN effective shade is less than zero or greater than one THEN the system SHALL reject the input with error message
3. WHEN wind height is less than or equal to zero THEN the system SHALL reject the input with error message
4. WHEN effective wind factor is less than zero THEN the system SHALL reject the input with error message
5. WHEN groundwater temperature is less than zero THEN the system SHALL reject the input with error message
6. WHEN groundwater inflow is negative THEN the system SHALL set to zero and issue warning
7. WHEN sediment thermal conductivity is negative THEN the system SHALL set to zero and issue warning
8. WHEN sediment thermal diffusivity is zero or negative THEN the system SHALL assume sediment properties equal to water and issue warning
9. WHEN sediment thermal thickness is zero or negative THEN the system SHALL set to 10 centimeters and issue warning
10. WHEN hyporheic exchange is negative THEN the system SHALL set to zero and issue warning
11. WHEN air temperature is missing (less than or equal to -999) THEN the system SHALL set to 20 degrees Celsius and issue warning
12. WHEN dewpoint temperature is missing (less than or equal to -999) THEN the system SHALL set to 10 degrees Celsius and issue warning
13. WHEN wind speed is negative THEN the system SHALL set to zero and issue warning
14. WHEN cloud cover is negative THEN the system SHALL set to zero and issue warning
15. WHEN cloud cover is greater than one THEN the system SHALL set to one and issue warning

### Requirement 9

**User Story:** As a water quality modeler, I want timestep validation and handling, so that the model detects data quality issues and handles variable timesteps correctly.

#### Acceptance Criteria

1. WHEN timestep between data points is greater than 2 hours THEN the system SHALL issue warning
2. WHEN timestep between data points is greater than 4 hours THEN the system SHALL reset water and sediment temperatures to midpoint of air and dewpoint temperatures and issue warning
3. WHEN timestep is zero indicating duplicate data THEN the system SHALL issue warning and skip temperature update
4. WHEN the system updates temperature THEN the system SHALL multiply temperature change rate by timestep in days
5. WHEN the system calculates temperature change rate THEN the system SHALL use current heat fluxes for next timestep

### Requirement 10

**User Story:** As a water quality modeler, I want model stability checking, so that the model detects numerical instability and alerts me to use smaller timesteps.

#### Acceptance Criteria

1. WHEN the system updates temperature THEN the system SHALL compare new temperature to previous timestep temperature
2. WHEN absolute temperature change exceeds stability criteria THEN the system SHALL halt execution with error message
3. WHEN stability error occurs THEN the system SHALL report the magnitude of temperature change
4. WHEN stability error occurs THEN the system SHALL recommend using smaller timestep or resampling meteorological data

### Requirement 11

**User Story:** As a water quality modeler, I want minimum temperature enforcement, so that calculated temperatures do not fall below physically realistic values.

#### Acceptance Criteria

1. WHEN calculated water temperature is less than minimum temperature THEN the system SHALL set water temperature to minimum temperature
2. WHEN calculated sediment temperature is less than minimum temperature THEN the system SHALL set sediment temperature to minimum temperature
3. WHEN the system enforces minimum temperature THEN the system SHALL apply constraint after each timestep update

### Requirement 12

**User Story:** As a water quality modeler, I want helper functions for atmospheric calculations, so that vapor pressure, humidity, and other atmospheric properties are calculated correctly.

#### Acceptance Criteria

1. WHEN the system calculates saturation vapor pressure THEN the system SHALL use Magnus formula with temperature in Celsius
2. WHEN the system calculates dewpoint from relative humidity THEN the system SHALL invert Magnus formula
3. WHEN the system calculates relative humidity from dewpoint THEN the system SHALL compute ratio of actual to saturation vapor pressure
4. WHEN the system calculates pressure from altitude THEN the system SHALL use US standard atmosphere formula
5. WHEN the system calculates saturated water vapor pressure THEN the system SHALL use Lowe polynomials for water or ice
6. WHEN the system converts Julian day THEN the system SHALL handle leap years correctly
7. WHEN the system calculates Koberg Brunt coefficient THEN the system SHALL interpolate from Koberg figure 34 using air temperature and clearness

### Requirement 13

**User Story:** As a water quality modeler, I want configurable model parameters, so that I can adapt the model to different water bodies and atmospheric conditions.

#### Acceptance Criteria

1. WHEN the system initializes THEN the system SHALL accept solar radiation method selection from Bras, Bird-Hulstrom, Ryan-Stolzenbach, or Iqbal
2. WHEN the system initializes THEN the system SHALL accept longwave radiation method selection from Brunt, Brutsaert, Satterlund, Idso-Jackson, Swinbank, or Koberg
3. WHEN the system initializes THEN the system SHALL accept wind function method selection from Brady-Graves-Geyer, Marciano-Harbeck, Ryan-Harleman, East Mesa, or Helfrich
4. WHEN the system initializes THEN the system SHALL accept atmospheric turbidity factor for Bras method
5. WHEN the system initializes THEN the system SHALL accept atmospheric transmission coefficient for Ryan-Stolzenbach method
6. WHEN the system initializes THEN the system SHALL accept cloud cover correction parameters KCL1 and KCL2 for solar radiation
7. WHEN the system initializes THEN the system SHALL accept cloud cover correction method selection for longwave radiation
8. WHEN the system initializes THEN the system SHALL accept cloud cover correction parameters KCL3 and KCL4 for longwave radiation
9. WHEN the system initializes THEN the system SHALL accept Brutsaert coefficient for Brutsaert longwave method
10. WHEN the system initializes THEN the system SHALL accept stability test criteria for temperature change checking

### Requirement 14

**User Story:** As a water quality modeler, I want optional diagnostic output, so that I can debug model behavior and understand intermediate calculations.

#### Acceptance Criteria

1. WHEN diagnostic output is enabled THEN the system SHALL output all site parameters for each timestep
2. WHEN diagnostic output is enabled THEN the system SHALL output all meteorological inputs for each timestep
3. WHEN diagnostic output is enabled THEN the system SHALL output solar position calculations for each timestep
4. WHEN diagnostic output is enabled THEN the system SHALL output all heat flux components for each timestep
5. WHEN diagnostic output is enabled THEN the system SHALL output temperature change rates for each timestep
6. WHEN diagnostic output is enabled THEN the system SHALL output intermediate solar radiation values before and after corrections
7. WHEN diagnostic output is enabled THEN the system SHALL output wind speed at multiple heights
8. WHEN diagnostic output is enabled THEN the system SHALL output vapor pressures and atmospheric emissivity

### Requirement 15

**User Story:** As a water quality modeler, I want the model to accept meteorological data in standard formats, so that I can easily prepare input data from various sources.

#### Acceptance Criteria

1. WHEN the system reads meteorological data THEN the system SHALL accept datetime objects or separate year, month, day, hour, minute fields
2. WHEN the system reads meteorological data THEN the system SHALL accept air temperature in degrees Celsius
3. WHEN the system reads meteorological data THEN the system SHALL accept dewpoint temperature in degrees Celsius
4. WHEN the system reads meteorological data THEN the system SHALL accept wind speed in meters per second
5. WHEN the system reads meteorological data THEN the system SHALL accept cloud cover as fraction from 0 to 1
6. WHEN the system reads meteorological data THEN the system SHALL optionally accept measured solar radiation in watts per square meter
7. WHEN the system reads meteorological data THEN the system SHALL optionally accept Bird-Hulstrom parameters: pressure, ozone, water vapor, aerosol optical depths, forward scattering, and albedo
8. WHEN the system reads meteorological data THEN the system SHALL optionally accept Iqbal parameters: visibility, ozone, and albedo
9. WHEN the system reads meteorological data THEN the system SHALL optionally accept time-varying water depth in meters
10. WHEN the system reads meteorological data THEN the system SHALL optionally accept time-varying effective shade as fraction

### Requirement 16

**User Story:** As a water quality modeler, I want the model to produce comprehensive output, so that I can analyze results and validate model performance.

#### Acceptance Criteria

1. WHEN the system produces output THEN the system SHALL include datetime for each timestep
2. WHEN the system produces output THEN the system SHALL include solar azimuth and elevation for each timestep
3. WHEN the system produces output THEN the system SHALL include potential solar radiation before corrections
4. WHEN the system produces output THEN the system SHALL include all heat flux components in watts per square meter
5. WHEN the system produces output THEN the system SHALL include calculated water temperature in degrees Celsius
6. WHEN the system produces output THEN the system SHALL include calculated sediment temperature in degrees Celsius
7. WHEN the system produces output THEN the system SHALL include air temperature and dewpoint temperature for reference
8. WHEN the system produces output THEN the system SHALL support export to pandas DataFrame
9. WHEN the system produces output THEN the system SHALL support export to CSV file
10. WHEN the system produces output THEN the system SHALL optionally include diagnostic information

### Requirement 17

**User Story:** As a water quality modeler, I want the model to handle edge cases gracefully, so that calculations remain stable under extreme conditions.

#### Acceptance Criteria

1. WHEN solar elevation is negative THEN the system SHALL set all solar radiation values to zero
2. WHEN solar zenith angle is greater than or equal to 89 degrees THEN the system SHALL set atmospheric transmittances to zero
3. WHEN vapor pressure difference is negative for evaporation THEN the system SHALL allow condensation (positive heat flux)
4. WHEN temperature difference is negative for convection THEN the system SHALL allow heat gain from air
5. WHEN sediment is warmer than water THEN the system SHALL allow heat flux from sediment to water
6. WHEN latitude is greater than 89.8 degrees THEN the system SHALL clamp to 89.8 degrees
7. WHEN latitude is less than -89.8 degrees THEN the system SHALL clamp to -89.8 degrees
8. WHEN true solar time exceeds 1440 minutes THEN the system SHALL apply modulo 1440 operation
9. WHEN hour angle is less than -180 degrees THEN the system SHALL add 360 degrees
10. WHEN cosine of zenith angle exceeds 1 THEN the system SHALL clamp to 1
11. WHEN cosine of zenith angle is less than -1 THEN the system SHALL clamp to -1

### Requirement 18

**User Story:** As a software developer, I want the Python implementation to follow best practices, so that the code is maintainable, testable, and well-documented.

#### Acceptance Criteria

1. WHEN the system is implemented THEN the system SHALL use type hints for all function parameters and return values
2. WHEN the system is implemented THEN the system SHALL include docstrings for all classes and public methods
3. WHEN the system is implemented THEN the system SHALL organize code into logical modules for solar, atmospheric, heat flux, and model components
4. WHEN the system is implemented THEN the system SHALL use numpy for numerical calculations where appropriate
5. WHEN the system is implemented THEN the system SHALL use pandas for data handling
6. WHEN the system is implemented THEN the system SHALL include unit tests for all calculation methods
7. WHEN the system is implemented THEN the system SHALL include integration tests comparing results to VBA implementation
8. WHEN the system is implemented THEN the system SHALL handle exceptions gracefully with informative error messages
9. WHEN the system is implemented THEN the system SHALL log warnings for data quality issues
10. WHEN the system is implemented THEN the system SHALL include example usage scripts

### Requirement 19

**User Story:** As a water quality modeler, I want the Python implementation to produce identical results to the VBA version, so that I can confidently transition from VBA to Python.

#### Acceptance Criteria

1. WHEN the system calculates solar position THEN the system SHALL match VBA results within 0.01 degrees for elevation and azimuth
2. WHEN the system calculates solar radiation THEN the system SHALL match VBA results within 0.1 watts per square meter
3. WHEN the system calculates heat fluxes THEN the system SHALL match VBA results within 0.1 watts per square meter for each component
4. WHEN the system calculates water temperature THEN the system SHALL match VBA results within 0.01 degrees Celsius
5. WHEN the system processes identical input data THEN the system SHALL produce identical output to VBA implementation within numerical precision limits
