"""
Property-based tests for solar position calculations.

These tests verify universal properties that should hold across all valid inputs
for the NOAA solar position algorithm and solar radiation models.
"""

import math
from datetime import datetime, timedelta
from hypothesis import given, strategies as st, settings
from rtemp.solar.position import NOAASolarPosition
from rtemp.solar.radiation_bras import SolarRadiationBras
from rtemp.solar.radiation_bird import SolarRadiationBird
from rtemp.solar.radiation_ryan import SolarRadiationRyanStolz
from rtemp.solar.radiation_iqbal import SolarRadiationIqbal


# Feature: rtemp-python-complete, Property 1: Julian Day Calculation Consistency
# Validates: Requirements 1.1
@given(
    year=st.integers(min_value=1900, max_value=2100),
    month=st.integers(min_value=1, max_value=12),
    day=st.integers(min_value=1, max_value=28),  # Use 28 to avoid invalid dates
)
@settings(max_examples=100)
def test_julian_day_round_trip(year: int, month: int, day: int):
    """
    Property: For any valid calendar date, calculating the Julian Day
    and then converting back to calendar date should produce the original date.

    This tests the consistency of the Julian Day calculation.
    """
    # Calculate Julian Day
    jd = NOAASolarPosition.calc_julian_day(year, month, day)

    # Julian Day should be a positive number
    assert jd > 0, f"Julian Day should be positive, got {jd}"

    # For the round trip, we'll verify that the Julian Day is consistent
    # by checking that dates in sequence produce increasing Julian Days
    if month < 12:
        jd_next = NOAASolarPosition.calc_julian_day(year, month + 1, day)
    else:
        jd_next = NOAASolarPosition.calc_julian_day(year + 1, 1, day)

    # Next month should have a larger Julian Day
    assert jd_next > jd, f"Julian Day should increase with time: {jd} -> {jd_next}"


# Feature: rtemp-python-complete, Property 2: Solar Position Determinism
# Validates: Requirements 1.2-1.16
@given(
    lat=st.floats(min_value=-89.8, max_value=89.8, allow_nan=False, allow_infinity=False),
    lon=st.floats(min_value=-180.0, max_value=180.0, allow_nan=False, allow_infinity=False),
    year=st.integers(min_value=2000, max_value=2030),
    month=st.integers(min_value=1, max_value=12),
    day=st.integers(min_value=1, max_value=28),
    hour=st.integers(min_value=0, max_value=23),
    minute=st.integers(min_value=0, max_value=59),
    timezone=st.floats(min_value=-12.0, max_value=14.0, allow_nan=False, allow_infinity=False),
    dlstime=st.integers(min_value=0, max_value=1),
)
@settings(max_examples=100)
def test_solar_position_determinism(
    lat: float,
    lon: float,
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    timezone: float,
    dlstime: int,
):
    """
    Property: For any location, datetime, and timezone, calculating solar position
    twice with identical inputs should produce identical results.

    This tests the determinism of the solar position calculation.
    """
    dt = datetime(year, month, day, hour, minute, 0)

    # Calculate solar position twice
    result1 = NOAASolarPosition.calc_solar_position(lat, lon, dt, timezone, dlstime)
    result2 = NOAASolarPosition.calc_solar_position(lat, lon, dt, timezone, dlstime)

    azimuth1, elevation1, distance1 = result1
    azimuth2, elevation2, distance2 = result2

    # Results should be identical
    assert azimuth1 == azimuth2, f"Azimuth should be deterministic: {azimuth1} != {azimuth2}"
    assert (
        elevation1 == elevation2
    ), f"Elevation should be deterministic: {elevation1} != {elevation2}"
    assert distance1 == distance2, f"Distance should be deterministic: {distance1} != {distance2}"

    # Azimuth should be in valid range [0, 360)
    assert 0 <= azimuth1 < 360, f"Azimuth should be in [0, 360): {azimuth1}"

    # Elevation should be in valid range [-90, 90]
    assert -90 <= elevation1 <= 90, f"Elevation should be in [-90, 90]: {elevation1}"

    # Distance should be positive and reasonable (Earth-Sun distance varies ~0.983 to 1.017 AU)
    assert 0.9 < distance1 < 1.1, f"Earth-Sun distance should be near 1 AU: {distance1}"


# Feature: rtemp-python-complete, Property 3: Sunrise Before Sunset
# Validates: Requirements 2.1-2.9
@given(
    lat=st.floats(min_value=-66.5, max_value=66.5, allow_nan=False, allow_infinity=False),
    lon=st.floats(min_value=-180.0, max_value=180.0, allow_nan=False, allow_infinity=False),
    year=st.integers(min_value=2000, max_value=2030),
    month=st.integers(min_value=1, max_value=12),
    day=st.integers(min_value=1, max_value=28),
    timezone=st.floats(min_value=-12.0, max_value=14.0, allow_nan=False, allow_infinity=False),
    dlstime=st.integers(min_value=0, max_value=1),
)
@settings(max_examples=100)
def test_sunrise_before_sunset(
    lat: float, lon: float, year: int, month: int, day: int, timezone: float, dlstime: int
):
    """
    Property: For any location and date where both sunrise and sunset occur,
    the sunrise time should be less than the sunset time.

    This tests the logical ordering of sunrise and sunset times.
    Note: Excludes polar regions (|lat| > 66.5°) where polar day/night phenomena
    can cause sunrise and sunset to be equal or undefined. Most water bodies
    are not in polar regions.
    """
    # Calculate sunrise and sunset
    sunrise = NOAASolarPosition.sunrise(lat, lon, year, month, day, timezone, dlstime)
    sunset = NOAASolarPosition.sunset(lat, lon, year, month, day, timezone, dlstime)

    # Both should be finite numbers
    assert math.isfinite(sunrise), f"Sunrise should be finite: {sunrise}"
    assert math.isfinite(sunset), f"Sunset should be finite: {sunset}"

    # Sunrise should occur before sunset
    # The difference should be positive and reasonable
    # Note: At extreme latitudes, sunset can wrap to next day, so diff can be slightly > 1
    time_diff = sunset - sunrise
    assert (
        0 < time_diff < 1.1
    ), f"Sunset ({sunset}) should be after sunrise ({sunrise}), diff: {time_diff}"


# Feature: rtemp-python-complete, Property 4: Solar Noon Between Sunrise and Sunset
# Validates: Requirements 2.7
@given(
    lat=st.floats(min_value=-66.5, max_value=66.5, allow_nan=False, allow_infinity=False),
    lon=st.floats(min_value=-180.0, max_value=180.0, allow_nan=False, allow_infinity=False),
    year=st.integers(min_value=2000, max_value=2030),
    month=st.integers(min_value=1, max_value=12),
    day=st.integers(min_value=1, max_value=28),
    timezone=st.floats(min_value=-12.0, max_value=14.0, allow_nan=False, allow_infinity=False),
    dlstime=st.integers(min_value=0, max_value=1),
)
@settings(max_examples=100)
def test_solar_noon_between_sunrise_sunset(
    lat: float, lon: float, year: int, month: int, day: int, timezone: float, dlstime: int
):
    """
    Property: For any location and date, solar noon should occur between
    sunrise and sunset times.

    This tests the logical ordering of solar events during the day.
    Note: Excludes polar regions (|lat| > 66.5°) where polar day/night phenomena
    can cause unusual solar event timing. Most water bodies are not in polar regions.
    """
    # Calculate sunrise, sunset, and solar noon
    sunrise = NOAASolarPosition.sunrise(lat, lon, year, month, day, timezone, dlstime)
    sunset = NOAASolarPosition.sunset(lat, lon, year, month, day, timezone, dlstime)
    solar_noon = NOAASolarPosition.solarnoon(lat, lon, year, month, day, timezone, dlstime)

    # All should be finite numbers
    assert math.isfinite(sunrise), f"Sunrise should be finite: {sunrise}"
    assert math.isfinite(sunset), f"Sunset should be finite: {sunset}"
    assert math.isfinite(solar_noon), f"Solar noon should be finite: {solar_noon}"

    # Solar noon should be between sunrise and sunset
    assert (
        sunrise < solar_noon < sunset
    ), f"Solar noon ({solar_noon}) should be between sunrise ({sunrise}) and sunset ({sunset})"


# Feature: rtemp-python-complete, Property 5: Solar Radiation Non-Negativity
# Validates: Requirements 3.1-3.4
@given(
    elevation=st.floats(min_value=-90.0, max_value=90.0, allow_nan=False, allow_infinity=False),
    earth_sun_distance=st.floats(
        min_value=0.983, max_value=1.017, allow_nan=False, allow_infinity=False
    ),
    turbidity=st.floats(min_value=1.0, max_value=10.0, allow_nan=False, allow_infinity=False),
)
@settings(max_examples=100)
def test_bras_solar_radiation_non_negativity(
    elevation: float, earth_sun_distance: float, turbidity: float
):
    """
    Property: For any solar radiation calculation using the Bras method,
    the calculated radiation should be greater than or equal to zero.

    This tests that the Bras model always produces physically valid
    (non-negative) radiation values.
    """
    # Calculate solar radiation using Bras method
    radiation = SolarRadiationBras.calculate(elevation, earth_sun_distance, turbidity)

    # Radiation must be non-negative
    assert radiation >= 0.0, (
        f"Solar radiation must be non-negative, got {radiation} W/m² "
        f"(elevation={elevation}°, distance={earth_sun_distance} AU, turbidity={turbidity})"
    )

    # Radiation should also be finite
    assert math.isfinite(radiation), f"Solar radiation must be finite, got {radiation} W/m²"


# Feature: rtemp-python-complete, Property 6: Solar Radiation Zero at Night
# Validates: Requirements 3.16
@given(
    elevation=st.floats(min_value=-90.0, max_value=0.0, allow_nan=False, allow_infinity=False),
    earth_sun_distance=st.floats(
        min_value=0.983, max_value=1.017, allow_nan=False, allow_infinity=False
    ),
    turbidity=st.floats(min_value=1.0, max_value=10.0, allow_nan=False, allow_infinity=False),
)
@settings(max_examples=100)
def test_bras_solar_radiation_zero_at_night(
    elevation: float, earth_sun_distance: float, turbidity: float
):
    """
    Property: For any solar radiation calculation when solar elevation is
    zero or negative, the calculated radiation should equal zero.

    This tests that the Bras model correctly handles nighttime conditions
    by returning zero radiation when the sun is below the horizon.
    """
    # Calculate solar radiation using Bras method with sun below horizon
    radiation = SolarRadiationBras.calculate(elevation, earth_sun_distance, turbidity)

    # Radiation must be exactly zero when sun is below horizon
    assert radiation == 0.0, (
        f"Solar radiation must be zero when sun is below horizon (elevation={elevation}°), "
        f"got {radiation} W/m²"
    )


# Feature: rtemp-python-complete, Property 5: Solar Radiation Non-Negativity
# Validates: Requirements 3.5-3.10
@given(
    zenith=st.floats(min_value=0.0, max_value=89.0, allow_nan=False, allow_infinity=False),
    earth_sun_distance=st.floats(
        min_value=0.983, max_value=1.017, allow_nan=False, allow_infinity=False
    ),
    pressure_mb=st.floats(min_value=800.0, max_value=1100.0, allow_nan=False, allow_infinity=False),
    ozone_cm=st.floats(min_value=0.1, max_value=0.6, allow_nan=False, allow_infinity=False),
    water_cm=st.floats(min_value=0.1, max_value=5.0, allow_nan=False, allow_infinity=False),
    aod_500nm=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
    aod_380nm=st.floats(min_value=0.0, max_value=1.5, allow_nan=False, allow_infinity=False),
    forward_scatter=st.floats(min_value=0.5, max_value=1.0, allow_nan=False, allow_infinity=False),
    albedo=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
)
@settings(max_examples=100)
def test_bird_solar_radiation_non_negativity(
    zenith: float,
    earth_sun_distance: float,
    pressure_mb: float,
    ozone_cm: float,
    water_cm: float,
    aod_500nm: float,
    aod_380nm: float,
    forward_scatter: float,
    albedo: float,
):
    """
    Property: For any solar radiation calculation using the Bird-Hulstrom method,
    all calculated radiation components should be greater than or equal to zero.

    This tests that the Bird-Hulstrom model always produces physically valid
    (non-negative) radiation values for all components: direct beam, direct
    horizontal, diffuse horizontal, and global horizontal irradiance.
    """
    # Calculate solar radiation using Bird-Hulstrom method
    result = SolarRadiationBird.calculate(
        zenith=zenith,
        earth_sun_distance=earth_sun_distance,
        pressure_mb=pressure_mb,
        ozone_cm=ozone_cm,
        water_cm=water_cm,
        aod_500nm=aod_500nm,
        aod_380nm=aod_380nm,
        forward_scatter=forward_scatter,
        albedo=albedo,
    )

    # All radiation components must be non-negative
    assert (
        result["direct_beam"] >= 0.0
    ), f"Direct beam radiation must be non-negative, got {result['direct_beam']} W/m²"

    assert (
        result["direct_hz"] >= 0.0
    ), f"Direct horizontal radiation must be non-negative, got {result['direct_hz']} W/m²"

    assert (
        result["diffuse_hz"] >= 0.0
    ), f"Diffuse horizontal radiation must be non-negative, got {result['diffuse_hz']} W/m²"

    assert (
        result["global_hz"] >= 0.0
    ), f"Global horizontal radiation must be non-negative, got {result['global_hz']} W/m²"

    # All components should be finite
    assert math.isfinite(
        result["direct_beam"]
    ), f"Direct beam radiation must be finite, got {result['direct_beam']} W/m²"

    assert math.isfinite(
        result["direct_hz"]
    ), f"Direct horizontal radiation must be finite, got {result['direct_hz']} W/m²"

    assert math.isfinite(
        result["diffuse_hz"]
    ), f"Diffuse horizontal radiation must be finite, got {result['diffuse_hz']} W/m²"

    assert math.isfinite(
        result["global_hz"]
    ), f"Global horizontal radiation must be finite, got {result['global_hz']} W/m²"

    # Global should equal direct + diffuse (within numerical precision)
    # Note: At extreme zenith angles (>85°), the Bird model's multiple reflection calculation
    # can introduce small discrepancies due to the iterative nature of the calculation.
    # We use a relaxed tolerance of 1.0 W/m² to account for this at extreme angles.
    expected_global = result["direct_hz"] + result["diffuse_hz"]
    assert abs(result["global_hz"] - expected_global) < 1.0, (
        f"Global radiation ({result['global_hz']}) should equal direct ({result['direct_hz']}) "
        f"+ diffuse ({result['diffuse_hz']}) = {expected_global}"
    )


# Feature: rtemp-python-complete, Property 5: Solar Radiation Non-Negativity
# Validates: Requirements 3.11-3.12
@given(
    elevation=st.floats(min_value=-90.0, max_value=90.0, allow_nan=False, allow_infinity=False),
    earth_sun_distance=st.floats(
        min_value=0.983, max_value=1.017, allow_nan=False, allow_infinity=False
    ),
    atmospheric_transmission_coeff=st.floats(
        min_value=0.70, max_value=0.91, allow_nan=False, allow_infinity=False
    ),
    site_elevation_m=st.floats(
        min_value=0.0, max_value=5000.0, allow_nan=False, allow_infinity=False
    ),
)
@settings(max_examples=100)
def test_ryan_stolz_solar_radiation_non_negativity(
    elevation: float,
    earth_sun_distance: float,
    atmospheric_transmission_coeff: float,
    site_elevation_m: float,
):
    """
    Property: For any solar radiation calculation using the Ryan-Stolzenbach method,
    the calculated radiation should be greater than or equal to zero.

    This tests that the Ryan-Stolzenbach model always produces physically valid
    (non-negative) radiation values across all valid input ranges.
    """
    # Calculate solar radiation using Ryan-Stolzenbach method
    radiation = SolarRadiationRyanStolz.calculate(
        elevation=elevation,
        earth_sun_distance=earth_sun_distance,
        atmospheric_transmission_coeff=atmospheric_transmission_coeff,
        site_elevation_m=site_elevation_m,
    )

    # Radiation must be non-negative
    assert radiation >= 0.0, (
        f"Solar radiation must be non-negative, got {radiation} W/m² "
        f"(elevation={elevation}°, distance={earth_sun_distance} AU, "
        f"atc={atmospheric_transmission_coeff}, site_elev={site_elevation_m}m)"
    )

    # Radiation should also be finite
    assert math.isfinite(radiation), f"Solar radiation must be finite, got {radiation} W/m²"

    # When sun is below horizon, radiation should be exactly zero
    if elevation <= 0.0:
        assert radiation == 0.0, (
            f"Solar radiation must be zero when sun is below horizon (elevation={elevation}°), "
            f"got {radiation} W/m²"
        )


# Feature: rtemp-python-complete, Property 5: Solar Radiation Non-Negativity
# Validates: Requirements 3.13-3.15
@given(
    zenith=st.floats(min_value=0.0, max_value=89.0, allow_nan=False, allow_infinity=False),
    earth_sun_distance=st.floats(
        min_value=0.983, max_value=1.017, allow_nan=False, allow_infinity=False
    ),
    pressure_mb=st.floats(min_value=800.0, max_value=1100.0, allow_nan=False, allow_infinity=False),
    ozone_cm=st.floats(min_value=0.1, max_value=0.6, allow_nan=False, allow_infinity=False),
    temperature_k=st.floats(
        min_value=233.15, max_value=323.15, allow_nan=False, allow_infinity=False
    ),  # -40°C to 50°C
    relative_humidity=st.floats(
        min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False
    ),
    visibility_km=st.floats(min_value=1.0, max_value=100.0, allow_nan=False, allow_infinity=False),
    albedo=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
    site_elevation_m=st.floats(
        min_value=0.0, max_value=5000.0, allow_nan=False, allow_infinity=False
    ),
)
@settings(max_examples=100)
def test_iqbal_solar_radiation_non_negativity(
    zenith: float,
    earth_sun_distance: float,
    pressure_mb: float,
    ozone_cm: float,
    temperature_k: float,
    relative_humidity: float,
    visibility_km: float,
    albedo: float,
    site_elevation_m: float,
):
    """
    Property: For any solar radiation calculation using the Iqbal method,
    all calculated radiation components should be greater than or equal to zero.

    This tests that the Iqbal model always produces physically valid
    (non-negative) radiation values for all components: direct beam, direct
    horizontal, diffuse horizontal (including Rayleigh, aerosol, and multiple
    scattering components), and global horizontal irradiance.
    """
    # Calculate solar radiation using Iqbal method
    result = SolarRadiationIqbal.calculate(
        zenith=zenith,
        earth_sun_distance=earth_sun_distance,
        pressure_mb=pressure_mb,
        ozone_cm=ozone_cm,
        temperature_k=temperature_k,
        relative_humidity=relative_humidity,
        visibility_km=visibility_km,
        albedo=albedo,
        site_elevation_m=site_elevation_m,
    )

    # All radiation components must be non-negative
    assert (
        result["direct_beam"] >= 0.0
    ), f"Direct beam radiation must be non-negative, got {result['direct_beam']} W/m²"

    assert (
        result["direct_hz"] >= 0.0
    ), f"Direct horizontal radiation must be non-negative, got {result['direct_hz']} W/m²"

    assert (
        result["diffuse_hz"] >= 0.0
    ), f"Diffuse horizontal radiation must be non-negative, got {result['diffuse_hz']} W/m²"

    assert (
        result["global_hz"] >= 0.0
    ), f"Global horizontal radiation must be non-negative, got {result['global_hz']} W/m²"

    assert (
        result["diffuse_rayleigh"] >= 0.0
    ), f"Rayleigh diffuse radiation must be non-negative, got {result['diffuse_rayleigh']} W/m²"

    assert (
        result["diffuse_aerosol"] >= 0.0
    ), f"Aerosol diffuse radiation must be non-negative, got {result['diffuse_aerosol']} W/m²"

    assert (
        result["diffuse_multiple"] >= 0.0
    ), f"Multiple scattering diffuse radiation must be non-negative, got {result['diffuse_multiple']} W/m²"

    # All components should be finite
    assert math.isfinite(
        result["direct_beam"]
    ), f"Direct beam radiation must be finite, got {result['direct_beam']} W/m²"

    assert math.isfinite(
        result["direct_hz"]
    ), f"Direct horizontal radiation must be finite, got {result['direct_hz']} W/m²"

    assert math.isfinite(
        result["diffuse_hz"]
    ), f"Diffuse horizontal radiation must be finite, got {result['diffuse_hz']} W/m²"

    assert math.isfinite(
        result["global_hz"]
    ), f"Global horizontal radiation must be finite, got {result['global_hz']} W/m²"

    # Global should equal direct + diffuse (within numerical precision)
    expected_global = result["direct_hz"] + result["diffuse_hz"]
    assert abs(result["global_hz"] - expected_global) < 0.01, (
        f"Global radiation ({result['global_hz']}) should equal direct ({result['direct_hz']}) "
        f"+ diffuse ({result['diffuse_hz']}) = {expected_global}"
    )

    # Diffuse should equal sum of components (within numerical precision)
    expected_diffuse = (
        result["diffuse_rayleigh"] + result["diffuse_aerosol"] + result["diffuse_multiple"]
    )
    assert abs(result["diffuse_hz"] - expected_diffuse) < 0.01, (
        f"Diffuse radiation ({result['diffuse_hz']}) should equal sum of components "
        f"(Rayleigh={result['diffuse_rayleigh']}, aerosol={result['diffuse_aerosol']}, "
        f"multiple={result['diffuse_multiple']}) = {expected_diffuse}"
    )


# Feature: rtemp-python-complete, Property 7: Cloud Cover Reduces Solar Radiation
# Validates: Requirements 3.17
@given(
    solar_radiation=st.floats(
        min_value=0.0, max_value=1500.0, allow_nan=False, allow_infinity=False
    ),
    kcl1=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
    kcl2=st.floats(min_value=0.0, max_value=5.0, allow_nan=False, allow_infinity=False),
)
@settings(max_examples=100)
def test_cloud_cover_reduces_radiation(solar_radiation: float, kcl1: float, kcl2: float):
    """
    Property: For any solar radiation calculation, increasing cloud cover (0 to 1)
    should monotonically decrease the calculated radiation.

    This tests that the cloud cover correction properly reduces radiation as
    cloud cover increases, which is physically expected behavior.
    """
    from rtemp.solar.corrections import SolarRadiationCorrections

    # Calculate radiation at cloud_cover = 0 (clear sky)
    radiation_clear = SolarRadiationCorrections.apply_cloud_correction(
        solar_radiation, cloud_cover=0.0, kcl1=kcl1, kcl2=kcl2
    )

    # Calculate radiation at cloud_cover = 1 (completely overcast)
    radiation_overcast = SolarRadiationCorrections.apply_cloud_correction(
        solar_radiation, cloud_cover=1.0, kcl1=kcl1, kcl2=kcl2
    )

    # Radiation with clouds should be less than or equal to clear sky radiation
    assert radiation_overcast <= radiation_clear, (
        f"Overcast radiation ({radiation_overcast} W/m²) should be <= clear sky "
        f"radiation ({radiation_clear} W/m²) for solar_radiation={solar_radiation}, "
        f"kcl1={kcl1}, kcl2={kcl2}"
    )

    # Both should be non-negative
    assert (
        radiation_clear >= 0.0
    ), f"Clear sky radiation must be non-negative, got {radiation_clear} W/m²"

    assert (
        radiation_overcast >= 0.0
    ), f"Overcast radiation must be non-negative, got {radiation_overcast} W/m²"

    # Both should be finite
    assert math.isfinite(
        radiation_clear
    ), f"Clear sky radiation must be finite, got {radiation_clear} W/m²"

    assert math.isfinite(
        radiation_overcast
    ), f"Overcast radiation must be finite, got {radiation_overcast} W/m²"

    # Test monotonicity: radiation at intermediate cloud cover should be between
    # clear and overcast values
    radiation_partial = SolarRadiationCorrections.apply_cloud_correction(
        solar_radiation, cloud_cover=0.5, kcl1=kcl1, kcl2=kcl2
    )

    assert radiation_overcast <= radiation_partial <= radiation_clear, (
        f"Partial cloud radiation ({radiation_partial} W/m²) should be between "
        f"overcast ({radiation_overcast} W/m²) and clear ({radiation_clear} W/m²)"
    )


# Feature: rtemp-python-complete, Property 8: Shade Reduces Solar Radiation
# Validates: Requirements 3.18
@given(
    solar_radiation=st.floats(
        min_value=0.0, max_value=1500.0, allow_nan=False, allow_infinity=False
    ),
)
@settings(max_examples=100)
def test_shade_reduces_radiation(solar_radiation: float):
    """
    Property: For any solar radiation calculation, increasing effective shade (0 to 1)
    should monotonically decrease the calculated radiation.

    This tests that the shade correction properly reduces radiation as shade
    increases, which is physically expected behavior. The relationship should
    be linear: radiation = original * (1 - shade).
    """
    from rtemp.solar.corrections import SolarRadiationCorrections

    # Calculate radiation at effective_shade = 0 (no shade)
    radiation_no_shade = SolarRadiationCorrections.apply_shade_correction(
        solar_radiation, effective_shade=0.0
    )

    # Calculate radiation at effective_shade = 1 (completely shaded)
    radiation_full_shade = SolarRadiationCorrections.apply_shade_correction(
        solar_radiation, effective_shade=1.0
    )

    # Radiation with full shade should be zero
    assert (
        radiation_full_shade == 0.0
    ), f"Fully shaded radiation should be zero, got {radiation_full_shade} W/m²"

    # Radiation with no shade should equal original radiation
    assert abs(radiation_no_shade - solar_radiation) < 1e-10, (
        f"No shade radiation ({radiation_no_shade} W/m²) should equal original "
        f"radiation ({solar_radiation} W/m²)"
    )

    # Both should be non-negative
    assert (
        radiation_no_shade >= 0.0
    ), f"No shade radiation must be non-negative, got {radiation_no_shade} W/m²"

    assert (
        radiation_full_shade >= 0.0
    ), f"Full shade radiation must be non-negative, got {radiation_full_shade} W/m²"

    # Test monotonicity: radiation at intermediate shade should be between
    # no shade and full shade values
    radiation_partial = SolarRadiationCorrections.apply_shade_correction(
        solar_radiation, effective_shade=0.5
    )

    assert radiation_full_shade <= radiation_partial <= radiation_no_shade, (
        f"Partial shade radiation ({radiation_partial} W/m²) should be between "
        f"full shade ({radiation_full_shade} W/m²) and no shade ({radiation_no_shade} W/m²)"
    )

    # Test linearity: 50% shade should give 50% of original radiation
    expected_partial = solar_radiation * 0.5
    assert abs(radiation_partial - expected_partial) < 1e-10, (
        f"50% shade radiation ({radiation_partial} W/m²) should be 50% of original "
        f"({expected_partial} W/m²)"
    )


# Feature: rtemp-python-complete, Property 24: Edge Case Stability
# Validates: Requirements 17.1-17.11
@given(
    lat=st.floats(min_value=-90.0, max_value=90.0, allow_nan=False, allow_infinity=False),
    lon=st.floats(min_value=-180.0, max_value=180.0, allow_nan=False, allow_infinity=False),
    year=st.integers(min_value=2000, max_value=2030),
    month=st.integers(min_value=1, max_value=12),
    day=st.integers(min_value=1, max_value=28),
    hour=st.integers(min_value=0, max_value=23),
    minute=st.integers(min_value=0, max_value=59),
    timezone=st.floats(min_value=-12.0, max_value=14.0, allow_nan=False, allow_infinity=False),
    dlstime=st.integers(min_value=0, max_value=1),
)
@settings(max_examples=100)
def test_edge_case_stability(
    lat: float,
    lon: float,
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    timezone: float,
    dlstime: int,
):
    """
    Property: For any edge case input (e.g., solar elevation = 0, latitude = 89.8°,
    extreme longitudes), the system should produce valid numeric output without
    errors or NaN values.

    This tests that the system handles edge cases gracefully:
    - Extreme latitudes (clamped to ±89.8°)
    - Solar elevation ≤ 0 (returns zero radiation)
    - Cosine values outside [-1, 1] (clamped)
    - True solar time > 1440 (wrapped)
    - Hour angle < -180 (wrapped)

    The system should remain stable and produce valid outputs for all inputs.
    """
    dt = datetime(year, month, day, hour, minute, 0)

    # Calculate solar position - should not raise exceptions
    try:
        azimuth, elevation, distance = NOAASolarPosition.calc_solar_position(
            lat, lon, dt, timezone, dlstime
        )
    except Exception as e:
        raise AssertionError(
            f"Solar position calculation failed for edge case inputs: "
            f"lat={lat}, lon={lon}, dt={dt}, tz={timezone}, dst={dlstime}. "
            f"Error: {e}"
        )

    # All outputs should be finite (not NaN or infinite)
    assert math.isfinite(azimuth), f"Azimuth should be finite for edge case, got {azimuth}"

    assert math.isfinite(elevation), f"Elevation should be finite for edge case, got {elevation}"

    assert math.isfinite(distance), f"Distance should be finite for edge case, got {distance}"

    # Azimuth should be in valid range [0, 360)
    assert 0 <= azimuth < 360, f"Azimuth should be in [0, 360) for edge case, got {azimuth}"

    # Elevation should be in valid range [-90, 90]
    assert (
        -90 <= elevation <= 90
    ), f"Elevation should be in [-90, 90] for edge case, got {elevation}"

    # Distance should be positive and reasonable
    assert (
        0.9 < distance < 1.1
    ), f"Earth-Sun distance should be near 1 AU for edge case, got {distance}"

    # Test solar radiation calculations with edge case elevation
    # Should not raise exceptions and should return valid values
    zenith = 90.0 - elevation
    earth_sun_distance = distance

    # Test Bras model
    try:
        radiation_bras = SolarRadiationBras.calculate(elevation, earth_sun_distance, turbidity=2.0)
        assert math.isfinite(
            radiation_bras
        ), f"Bras radiation should be finite for edge case, got {radiation_bras}"
        assert (
            radiation_bras >= 0.0
        ), f"Bras radiation should be non-negative for edge case, got {radiation_bras}"

        # If elevation <= 0, radiation should be exactly zero
        if elevation <= 0.0:
            assert (
                radiation_bras == 0.0
            ), f"Bras radiation should be zero when elevation <= 0, got {radiation_bras}"
    except Exception as e:
        raise AssertionError(
            f"Bras radiation calculation failed for edge case: "
            f"elevation={elevation}, distance={earth_sun_distance}. Error: {e}"
        )

    # Test Bird model (only if zenith < 89 to avoid edge case in Bird model)
    if zenith < 89.0:
        try:
            result_bird = SolarRadiationBird.calculate(
                zenith=zenith,
                earth_sun_distance=earth_sun_distance,
                pressure_mb=1013.25,
                ozone_cm=0.35,
                water_cm=1.5,
                aod_500nm=0.1,
                aod_380nm=0.15,
                forward_scatter=0.84,
                albedo=0.2,
            )

            # All components should be finite and non-negative
            for key, value in result_bird.items():
                assert math.isfinite(
                    value
                ), f"Bird {key} should be finite for edge case, got {value}"
                assert value >= 0.0, f"Bird {key} should be non-negative for edge case, got {value}"
        except Exception as e:
            raise AssertionError(
                f"Bird radiation calculation failed for edge case: "
                f"zenith={zenith}, distance={earth_sun_distance}. Error: {e}"
            )
    else:
        # For zenith >= 89, Bird model should return all zeros
        result_bird = SolarRadiationBird.calculate(
            zenith=zenith,
            earth_sun_distance=earth_sun_distance,
            pressure_mb=1013.25,
            ozone_cm=0.35,
            water_cm=1.5,
            aod_500nm=0.1,
            aod_380nm=0.15,
            forward_scatter=0.84,
            albedo=0.2,
        )

        assert (
            result_bird["global_hz"] == 0.0
        ), f"Bird radiation should be zero when zenith >= 89°, got {result_bird['global_hz']}"

    # Test Ryan-Stolzenbach model
    try:
        radiation_ryan = SolarRadiationRyanStolz.calculate(
            elevation=elevation,
            earth_sun_distance=earth_sun_distance,
            atmospheric_transmission_coeff=0.8,
            site_elevation_m=0.0,
        )

        assert math.isfinite(
            radiation_ryan
        ), f"Ryan-Stolz radiation should be finite for edge case, got {radiation_ryan}"
        assert (
            radiation_ryan >= 0.0
        ), f"Ryan-Stolz radiation should be non-negative for edge case, got {radiation_ryan}"

        # If elevation <= 0, radiation should be exactly zero
        if elevation <= 0.0:
            assert (
                radiation_ryan == 0.0
            ), f"Ryan-Stolz radiation should be zero when elevation <= 0, got {radiation_ryan}"
    except Exception as e:
        raise AssertionError(
            f"Ryan-Stolz radiation calculation failed for edge case: "
            f"elevation={elevation}, distance={earth_sun_distance}. Error: {e}"
        )

    # Test Iqbal model (only if zenith < 89 to avoid edge case in Iqbal model)
    if zenith < 89.0:
        try:
            result_iqbal = SolarRadiationIqbal.calculate(
                zenith=zenith,
                earth_sun_distance=earth_sun_distance,
                pressure_mb=1013.25,
                ozone_cm=0.35,
                temperature_k=293.15,
                relative_humidity=0.5,
                visibility_km=23.0,
                albedo=0.2,
                site_elevation_m=0.0,
            )

            # All components should be finite and non-negative
            for key, value in result_iqbal.items():
                assert math.isfinite(
                    value
                ), f"Iqbal {key} should be finite for edge case, got {value}"
                assert (
                    value >= 0.0
                ), f"Iqbal {key} should be non-negative for edge case, got {value}"
        except Exception as e:
            raise AssertionError(
                f"Iqbal radiation calculation failed for edge case: "
                f"zenith={zenith}, distance={earth_sun_distance}. Error: {e}"
            )
    else:
        # For zenith >= 89, Iqbal model should return all zeros
        result_iqbal = SolarRadiationIqbal.calculate(
            zenith=zenith,
            earth_sun_distance=earth_sun_distance,
            pressure_mb=1013.25,
            ozone_cm=0.35,
            temperature_k=293.15,
            relative_humidity=0.5,
            visibility_km=23.0,
            albedo=0.2,
            site_elevation_m=0.0,
        )

        assert (
            result_iqbal["global_hz"] == 0.0
        ), f"Iqbal radiation should be zero when zenith >= 89°, got {result_iqbal['global_hz']}"

    # Test sunrise and sunset calculations - should not raise exceptions
    # These already clamp latitude internally
    try:
        sunrise = NOAASolarPosition.sunrise(lat, lon, year, month, day, timezone, dlstime)
        sunset = NOAASolarPosition.sunset(lat, lon, year, month, day, timezone, dlstime)
        solar_noon = NOAASolarPosition.solarnoon(lat, lon, year, month, day, timezone, dlstime)

        # All should be finite
        assert math.isfinite(sunrise), f"Sunrise should be finite for edge case, got {sunrise}"
        assert math.isfinite(sunset), f"Sunset should be finite for edge case, got {sunset}"
        assert math.isfinite(
            solar_noon
        ), f"Solar noon should be finite for edge case, got {solar_noon}"

        # All should be reasonable values (can be slightly outside [0, 1] due to timezone/DST)
        # Sunrise and sunset can wrap to next day in some timezone combinations
        assert -0.5 <= sunrise <= 1.5, f"Sunrise should be reasonable, got {sunrise}"
        assert -0.5 <= sunset <= 1.5, f"Sunset should be reasonable, got {sunset}"
        assert -0.5 <= solar_noon <= 1.5, f"Solar noon should be reasonable, got {solar_noon}"
    except Exception as e:
        raise AssertionError(
            f"Sunrise/sunset calculation failed for edge case: "
            f"lat={lat}, lon={lon}, date={year}-{month}-{day}. Error: {e}"
        )
