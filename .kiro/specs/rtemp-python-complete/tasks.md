# Implementation Plan: rTemp Python Complete

- [x] 1. Set up project structure and core infrastructure





  - Create package directory structure with all modules
  - Set up pyproject.toml with dependencies
  - Configure pytest, hypothesis, mypy, black, flake8
  - Create constants.py with physical constants
  - _Requirements: 18.1-18.10_



- [x] 2. Implement data models and configuration


  - Create ModelConfiguration dataclass with all parameters
  - Create ModelState dataclass for runtime state
  - Create MeteorologicalData dataclass for inputs
  - Create HeatFluxComponents dataclass for outputs
  - Create SolarPositionResult dataclass
  - Create DiagnosticOutput dataclass
  - _Requirements: 13.1-13.10, 15.1-15.10, 16.1-16.10_

- [x] 3. Implement unit conversion utilities




  - Create UnitConversions class with all conversion methods
  - Implement watts_m2_to_cal_cm2_day and reverse
  - Implement angle conversions (deg/rad)
  - Implement temperature conversions (C/K)
  - Implement length conversions (m/cm)
  - _Requirements: 7.1-7.8_

- [x] 3.1 Write property test for unit conversions






  - **Property 14: Unit Conversion Round Trip**
  - **Validates: Requirements 7.1-7.8**


- [x] 4. Implement atmospheric helper functions




  - Create AtmosphericHelpers class
  - Implement saturation_vapor_pressure (Magnus formula)
  - Implement dewpoint_from_rh
  - Implement relative_humidity_from_dewpoint
  - Implement pressure_from_altitude (US standard atmosphere)
  - Implement water_vapor_saturation_lowe (Lowe polynomials)
  - _Requirements: 12.1-12.7_

- [x] 4.1 Write property test for vapor pressure monotonicity



  - **Property 19: Vapor Pressure Monotonicity**
  - **Validates: Requirements 12.1**



- [x] 4.2 Write property test for dewpoint-RH round trip



  - **Property 20: Dewpoint-RH Round Trip**
  - **Validates: Requirements 12.2-12.3**

- [x] 5. Implement NOAA solar position algorithm





  - Create NOAASolarPosition class
  - Implement calc_julian_day
  - Implement calc_time_julian_cent
  - Implement calc_geom_mean_long_sun
  - Implement calc_geom_mean_anomaly_sun
  - Implement calc_eccentricity_earth_orbit
  - Implement calc_sun_eq_of_center
  - Implement calc_sun_true_long and calc_sun_apparent_long
  - Implement calc_mean_obliquity_ecliptic and calc_obliquity_correction
  - Implement calc_sun_rt_ascension and calc_sun_declination
  - Implement calc_equation_of_time
  - Implement calc_sun_rad_vector
  - Implement calc_solar_position (main method returning azimuth, elevation, distance)
  - _Requirements: 1.1-1.19_

- [x] 5.1 Write property test for Julian Day round trip



  - **Property 1: Julian Day Calculation Consistency**
  - **Validates: Requirements 1.1**

- [x] 5.2 Write property test for solar position determinism



  - **Property 2: Solar Position Determinism**
  - **Validates: Requirements 1.2-1.16**

- [x] 5.3 Write unit tests for solar position against NOAA reference data



  - Test known dates/times/locations against NOAA calculator outputs
  - _Requirements: 1.1-1.19_


- [-] 6. Implement sunrise/sunset calculations


  - Implement calc_hour_angle_sunrise
  - Implement calc_hour_angle_sunset
  - Implement calc_sunrise_utc with iterative refinement
  - Implement calc_sunset_utc with iterative refinement
  - Implement calc_solar_noon_utc
  - Implement sunrise, sunset, solarnoon wrapper functions
  - _Requirements: 2.1-2.9_

- [x] 6.1 Write property test for sunrise before sunset



  - **Property 3: Sunrise Before Sunset**
  - **Validates: Requirements 2.1-2.9**


- [x] 6.2 Write property test for solar noon between sunrise and sunset


  - **Property 4: Solar Noon Between Sunrise and Sunset**
  - **Validates: Requirements 2.7**


- [x] 7. Implement Bras solar radiation model




  - Create SolarRadiationBras class
  - Implement calculate method with extraterrestrial radiation
  - Implement optical air mass calculation (Kasten-Young)
  - Implement molecular scattering coefficient
  - Implement clear-sky radiation with turbidity factor
  - _Requirements: 3.1-3.4_

- [x] 7.1 Write property test for solar radiation non-negativity (Bras)



  - **Property 5: Solar Radiation Non-Negativity**
  - **Validates: Requirements 3.1-3.4**

- [x] 7.2 Write property test for solar radiation zero at night (Bras)



  - **Property 6: Solar Radiation Zero at Night**
  - **Validates: Requirements 3.16**


- [x] 8. Implement Bird-Hulstrom solar radiation model




  - Create SolarRadiationBird class
  - Implement Rayleigh scattering transmittance
  - Implement ozone transmittance
  - Implement uniformly mixed gases transmittance
  - Implement water vapor transmittance
  - Implement aerosol transmittance
  - Implement direct beam, direct horizontal, diffuse, and global horizontal irradiance
  - _Requirements: 3.5-3.10_

- [x] 8.1 Write property test for Bird model non-negativity



  - **Property 5: Solar Radiation Non-Negativity**
  - **Validates: Requirements 3.5-3.10**


- [x] 9. Implement Ryan-Stolzenbach solar radiation model




  - Create SolarRadiationRyanStolz class
  - Implement atmospheric transmission with elevation correction
  - Implement relative air mass calculation
  - _Requirements: 3.11-3.12_

- [x] 9.1 Write property test for Ryan-Stolz model non-negativity



  - **Property 5: Solar Radiation Non-Negativity**
  - **Validates: Requirements 3.11-3.12**


- [x] 10. Implement Iqbal solar radiation model




  - Create SolarRadiationIqbal class
  - Implement atmospheric transmittances (Rayleigh, ozone, gases, water, aerosols)
  - Implement direct and diffuse irradiance components
  - Implement multiple scattering calculation
  - _Requirements: 3.13-3.15_

- [x] 10.1 Write property test for Iqbal model non-negativity



  - **Property 5: Solar Radiation Non-Negativity**
  - **Validates: Requirements 3.13-3.15**

- [x] 11. Implement solar radiation corrections





  - Implement Anderson albedo calculation (cloud-dependent)
  - Implement cloud cover correction with KCL1, KCL2 parameters
  - Implement shade correction
  - Implement albedo (reflection) correction
  - _Requirements: 3.17-3.19_

- [x] 11.1 Write property test for cloud cover reduces radiation



  - **Property 7: Cloud Cover Reduces Solar Radiation**
  - **Validates: Requirements 3.17**

- [x] 11.2 Write property test for shade reduces radiation



  - **Property 8: Shade Reduces Solar Radiation**
  - **Validates: Requirements 3.18**


- [x] 12. Implement longwave emissivity models




  - Create base LongwaveEmissivity abstract class
  - Implement EmissivityBrunt (Brunt 1932)
  - Implement EmissivityBrutsaert (Brutsaert 1982 with configurable coefficient)
  - Implement EmissivitySatterlund (Satterlund 1979)
  - Implement EmissivityIdsoJackson (Idso-Jackson 1969)
  - Implement EmissivitySwinbank (Swinbank 1963)
  - Implement EmissivityKoberg (Koberg 1964 with figure 34 interpolation)
  - _Requirements: 4.1-4.6_

- [x] 12.1 Write property test for emissivity bounds



  - **Property 9: Longwave Emissivity Bounds**
  - **Validates: Requirements 4.1-4.6**


- [x] 13. Implement longwave radiation calculations




  - Create LongwaveRadiation class
  - Implement calculate_atmospheric with cloud corrections (Equation 1 and 2)
  - Implement calculate_back_radiation
  - Implement Stefan-Boltzmann law applications
  - Implement surface reflection correction
  - _Requirements: 4.7-4.12_

- [x] 13.1 Write property test for longwave increases with temperature



  - **Property 10: Longwave Radiation Increases with Temperature**
  - **Validates: Requirements 4.10**


- [x] 14. Implement wind height adjustment




  - Create WindAdjustment class
  - Implement TVA exponential wind correction
  - Implement adjust_for_height method
  - Implement shelter factor application
  - _Requirements: 5.6-5.7_

- [x] 15. Implement wind function models





  - Create base WindFunction abstract class
  - Implement WindFunctionBradyGravesGeyer
  - Implement WindFunctionMarcianoHarbeck (Lake Hefner)
  - Implement WindFunctionRyanHarleman with virtual temperature
  - Implement WindFunctionEastMesa
  - Implement WindFunctionHelfrich (recalibrated Ryan-Harleman)
  - Implement virtual temperature calculation helper
  - _Requirements: 5.1-5.5, 5.8_

- [x] 15.1 Write property test for wind function positivity



  - **Property 11: Wind Function Positivity**
  - **Validates: Requirements 5.1-5.5**

- [x] 15.2 Write property test for wind function increases with wind speed


  - **Property 12: Wind Function Increases with Wind Speed**
  - **Validates: Requirements 5.1-5.5**


- [x] 16. Implement heat flux calculations




  - Create HeatFluxCalculator class
  - Implement calculate_evaporation
  - Implement calculate_convection
  - Implement calculate_sediment_conduction
  - Implement calculate_hyporheic_exchange
  - Implement calculate_groundwater_flux
  - Implement calculate_longwave_back
  - _Requirements: 6.1-6.7_

- [x] 16.1 Write property test for energy conservation



  - **Property 13: Energy Conservation in Heat Budget**
  - **Validates: Requirements 6.8**


- [x] 17. Implement input validation




  - Create InputValidator class
  - Implement validate_site_parameters with all checks
  - Implement validate_meteorological_data with missing data handling
  - Implement check_timestep for duplicate and large timesteps
  - Implement warning collection and reporting
  - _Requirements: 8.1-8.15, 9.1-9.5_

- [x] 17.1 Write property test for invalid inputs rejected



  - **Property 15: Invalid Inputs Rejected**
  - **Validates: Requirements 8.1-8.15**

- [x] 17.2 Write property test for missing data handling



  - **Property 16: Missing Data Handling**
  - **Validates: Requirements 8.11-8.15**

- [x] 17.3 Write property test for timestep monotonicity



  - **Property 17: Timestep Monotonicity**
  - **Validates: Requirements 9.3**


- [x] 18. Implement main RTempModel class




  - Create RTempModel class with __init__ accepting ModelConfiguration
  - Implement run method with main execution loop
  - Implement _calculate_timestep for single timestep calculation
  - Implement _check_stability for numerical stability checking
  - Implement _enforce_minimum_temperature
  - Implement state management (water temp, sediment temp)
  - Implement method selection logic (solar, longwave, wind)
  - _Requirements: 6.8-6.9, 10.1-10.4, 11.1-11.3_

- [x] 18.1 Write property test for temperature minimum enforcement



  - **Property 18: Temperature Minimum Enforcement**
  - **Validates: Requirements 11.1-11.3**


- [x] 19. Implement output formatting




  - Implement export_results method
  - Implement DataFrame output with all required columns
  - Implement CSV export
  - Implement diagnostic output when enabled
  - _Requirements: 16.1-16.10, 14.1-14.8_

- [x] 19.1 Write property test for output completeness



  - **Property 22: Output Completeness**
  - **Validates: Requirements 16.1-16.7**

- [x] 19.2 Write property test for diagnostic output completeness



  - **Property 23: Diagnostic Output Completeness**
  - **Validates: Requirements 14.1-14.8**


- [x] 20. Implement edge case handling




  - Implement clamping for extreme latitudes
  - Implement handling for solar elevation ≤ 0
  - Implement handling for cosine values outside [-1, 1]
  - Implement handling for true solar time > 1440
  - Implement handling for hour angle < -180
  - _Requirements: 17.1-17.11_

- [x] 20.1 Write property test for edge case stability



  - **Property 24: Edge Case Stability**
  - **Validates: Requirements 17.1-17.11**

- [x] 21. Checkpoint - Ensure all tests pass





  - Ensure all tests pass, ask the user if questions arise.


- [x] 22. Create example usage scripts




  - Create simple example with default parameters
  - Create example with all methods demonstrated
  - Create example with diagnostic output
  - Create example with time-varying parameters
  - _Requirements: 18.10_

- [x] 23. Write integration tests




  - Write test for simple single-day scenario
  - Write test for multi-day scenario
  - Write test for variable timestep handling
  - Write test for all method combinations
  - Write test for edge case integration
  - _Requirements: All_

- [x] 24. Create VBA comparison test suite





  - Create test dataset with known VBA outputs
  - Implement comparison tests for solar position (±0.01°)
  - Implement comparison tests for solar radiation (±0.1 W/m²)
  - Implement comparison tests for heat fluxes (±0.1 W/m²)
  - Implement comparison tests for temperature (±0.01°C)
  - Document any differences and their causes
  - _Requirements: 19.1-19.5_


- [x] 25. Write documentation




  - Write API documentation with docstrings
  - Write user guide with installation and quick start
  - Write configuration guide
  - Write method selection guide
  - Write troubleshooting section
  - Write developer guide
  - _Requirements: 18.1-18.3_



- [x] 26. Final checkpoint - Ensure all tests pass






  - Ensure all tests pass, ask the user if questions arise.
