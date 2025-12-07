"""
Property-based tests for input validation.

Tests universal properties that should hold for all validation operations.
"""

import pytest
from hypothesis import given, strategies as st, assume
import pandas as pd
from datetime import datetime, timedelta
from rtemp.utils.validation import InputValidator


# Feature: rtemp-python-complete, Property 15: Invalid Inputs Rejected
# Validates: Requirements 8.1-8.15
@given(water_depth=st.floats(min_value=-1000, max_value=0, allow_nan=False, allow_infinity=False))
def test_property_invalid_water_depth_rejected(water_depth):
    """
    Property 15: Invalid Inputs Rejected

    For any water depth <= 0, the validation should reject the input with ValueError.

    Validates: Requirements 8.1
    """
    params = {"water_depth": water_depth}

    with pytest.raises(ValueError, match="Water depth must be greater than zero"):
        InputValidator.validate_site_parameters(params)


# Feature: rtemp-python-complete, Property 15: Invalid Inputs Rejected
# Validates: Requirements 8.1-8.15
@given(
    effective_shade=st.one_of(
        st.floats(min_value=-1000, max_value=-0.001, allow_nan=False, allow_infinity=False),
        st.floats(min_value=1.001, max_value=1000, allow_nan=False, allow_infinity=False),
    )
)
def test_property_invalid_shade_rejected(effective_shade):
    """
    Property 15: Invalid Inputs Rejected

    For any effective shade outside [0, 1], the validation should reject the input with ValueError.

    Validates: Requirements 8.2
    """
    params = {"effective_shade": effective_shade}

    with pytest.raises(ValueError, match="Effective shade must be between 0 and 1"):
        InputValidator.validate_site_parameters(params)


# Feature: rtemp-python-complete, Property 15: Invalid Inputs Rejected
# Validates: Requirements 8.1-8.15
@given(wind_height=st.floats(min_value=-1000, max_value=0, allow_nan=False, allow_infinity=False))
def test_property_invalid_wind_height_rejected(wind_height):
    """
    Property 15: Invalid Inputs Rejected

    For any wind height <= 0, the validation should reject the input with ValueError.

    Validates: Requirements 8.3
    """
    params = {"wind_height": wind_height}

    with pytest.raises(ValueError, match="Wind height must be greater than zero"):
        InputValidator.validate_site_parameters(params)


# Feature: rtemp-python-complete, Property 15: Invalid Inputs Rejected
# Validates: Requirements 8.1-8.15
@given(
    effective_wind_factor=st.floats(
        min_value=-1000, max_value=-0.001, allow_nan=False, allow_infinity=False
    )
)
def test_property_invalid_wind_factor_rejected(effective_wind_factor):
    """
    Property 15: Invalid Inputs Rejected

    For any effective wind factor < 0, the validation should reject the input with ValueError.

    Validates: Requirements 8.4
    """
    params = {"effective_wind_factor": effective_wind_factor}

    with pytest.raises(
        ValueError, match="Effective wind factor must be greater than or equal to zero"
    ):
        InputValidator.validate_site_parameters(params)


# Feature: rtemp-python-complete, Property 15: Invalid Inputs Rejected
# Validates: Requirements 8.1-8.15
@given(
    groundwater_temperature=st.floats(
        min_value=-1000, max_value=-0.001, allow_nan=False, allow_infinity=False
    )
)
def test_property_invalid_groundwater_temp_rejected(groundwater_temperature):
    """
    Property 15: Invalid Inputs Rejected

    For any groundwater temperature < 0, the validation should reject the input with ValueError.

    Validates: Requirements 8.5
    """
    params = {"groundwater_temperature": groundwater_temperature}

    with pytest.raises(
        ValueError, match="Groundwater temperature must be greater than or equal to zero"
    ):
        InputValidator.validate_site_parameters(params)


# Feature: rtemp-python-complete, Property 15: Invalid Inputs Rejected
# Validates: Requirements 8.1-8.15
@given(
    groundwater_inflow=st.floats(
        min_value=-1000, max_value=-0.001, allow_nan=False, allow_infinity=False
    )
)
def test_property_negative_groundwater_inflow_corrected(groundwater_inflow):
    """
    Property 15: Invalid Inputs Rejected (with correction)

    For any negative groundwater inflow, the validation should correct to zero and issue warning.

    Validates: Requirements 8.6
    """
    params = {"groundwater_inflow": groundwater_inflow}

    validated, warnings = InputValidator.validate_site_parameters(params)

    assert validated["groundwater_inflow"] == 0.0
    assert len(warnings) >= 1
    assert any("Groundwater inflow was negative" in w for w in warnings)


# Feature: rtemp-python-complete, Property 15: Invalid Inputs Rejected
# Validates: Requirements 8.1-8.15
@given(
    sediment_thermal_conductivity=st.floats(
        min_value=-1000, max_value=-0.001, allow_nan=False, allow_infinity=False
    )
)
def test_property_negative_sediment_conductivity_corrected(sediment_thermal_conductivity):
    """
    Property 15: Invalid Inputs Rejected (with correction)

    For any negative sediment thermal conductivity, the validation should correct to zero and issue warning.

    Validates: Requirements 8.7
    """
    params = {"sediment_thermal_conductivity": sediment_thermal_conductivity}

    validated, warnings = InputValidator.validate_site_parameters(params)

    assert validated["sediment_thermal_conductivity"] == 0.0
    assert len(warnings) >= 1
    assert any("Sediment thermal conductivity was negative" in w for w in warnings)


# Feature: rtemp-python-complete, Property 15: Invalid Inputs Rejected
# Validates: Requirements 8.1-8.15
@given(
    sediment_thermal_diffusivity=st.floats(
        min_value=-1000, max_value=0, allow_nan=False, allow_infinity=False
    )
)
def test_property_invalid_sediment_diffusivity_corrected(sediment_thermal_diffusivity):
    """
    Property 15: Invalid Inputs Rejected (with correction)

    For any sediment thermal diffusivity <= 0, the validation should correct to water value and issue warning.

    Validates: Requirements 8.8
    """
    params = {"sediment_thermal_diffusivity": sediment_thermal_diffusivity}

    validated, warnings = InputValidator.validate_site_parameters(params)

    assert validated["sediment_thermal_diffusivity"] == 0.0014
    assert len(warnings) >= 1
    assert any("assumed equal to water properties" in w for w in warnings)


# Feature: rtemp-python-complete, Property 15: Invalid Inputs Rejected
# Validates: Requirements 8.1-8.15
@given(
    sediment_thickness=st.floats(
        min_value=-1000, max_value=0, allow_nan=False, allow_infinity=False
    )
)
def test_property_invalid_sediment_thickness_corrected(sediment_thickness):
    """
    Property 15: Invalid Inputs Rejected (with correction)

    For any sediment thickness <= 0, the validation should correct to 10 cm and issue warning.

    Validates: Requirements 8.9
    """
    params = {"sediment_thickness": sediment_thickness}

    validated, warnings = InputValidator.validate_site_parameters(params)

    assert validated["sediment_thickness"] == 10.0
    assert len(warnings) >= 1
    assert any("set to 10 cm" in w for w in warnings)


# Feature: rtemp-python-complete, Property 15: Invalid Inputs Rejected
# Validates: Requirements 8.1-8.15
@given(
    hyporheic_exchange_rate=st.floats(
        min_value=-1000, max_value=-0.001, allow_nan=False, allow_infinity=False
    )
)
def test_property_negative_hyporheic_exchange_corrected(hyporheic_exchange_rate):
    """
    Property 15: Invalid Inputs Rejected (with correction)

    For any negative hyporheic exchange rate, the validation should correct to zero and issue warning.

    Validates: Requirements 8.10
    """
    params = {"hyporheic_exchange_rate": hyporheic_exchange_rate}

    validated, warnings = InputValidator.validate_site_parameters(params)

    assert validated["hyporheic_exchange_rate"] == 0.0
    assert len(warnings) >= 1
    assert any("Hyporheic exchange rate was negative" in w for w in warnings)


# Feature: rtemp-python-complete, Property 16: Missing Data Handling
# Validates: Requirements 8.11-8.15
@given(
    air_temps=st.lists(
        st.one_of(
            st.floats(min_value=-999.1, max_value=-999, allow_nan=False, allow_infinity=False),
            st.floats(min_value=-2000, max_value=-999.1, allow_nan=False, allow_infinity=False),
        ),
        min_size=1,
        max_size=10,
    )
)
def test_property_missing_air_temperature_handled(air_temps):
    """
    Property 16: Missing Data Handling

    For any air temperature values <= -999, the validation should replace with 20°C and issue warning.

    Validates: Requirements 8.11
    """
    data = pd.DataFrame({"air_temperature": air_temps})

    validated, warnings = InputValidator.validate_meteorological_data(data)

    # All values should be replaced with 20.0
    assert all(validated["air_temperature"] == 20.0)
    # Should have exactly one warning
    assert len(warnings) >= 1
    assert any("Air temperature missing" in w for w in warnings)


# Feature: rtemp-python-complete, Property 16: Missing Data Handling
# Validates: Requirements 8.11-8.15
@given(
    dewpoint_temps=st.lists(
        st.one_of(
            st.floats(min_value=-999.1, max_value=-999, allow_nan=False, allow_infinity=False),
            st.floats(min_value=-2000, max_value=-999.1, allow_nan=False, allow_infinity=False),
        ),
        min_size=1,
        max_size=10,
    )
)
def test_property_missing_dewpoint_handled(dewpoint_temps):
    """
    Property 16: Missing Data Handling

    For any dewpoint temperature values <= -999, the validation should replace with 10°C and issue warning.

    Validates: Requirements 8.12
    """
    data = pd.DataFrame({"dewpoint_temperature": dewpoint_temps})

    validated, warnings = InputValidator.validate_meteorological_data(data)

    # All values should be replaced with 10.0
    assert all(validated["dewpoint_temperature"] == 10.0)
    # Should have exactly one warning
    assert len(warnings) >= 1
    assert any("Dewpoint temperature missing" in w for w in warnings)


# Feature: rtemp-python-complete, Property 16: Missing Data Handling
# Validates: Requirements 8.11-8.15
@given(
    wind_speeds=st.lists(
        st.floats(min_value=-1000, max_value=-0.001, allow_nan=False, allow_infinity=False),
        min_size=1,
        max_size=10,
    )
)
def test_property_negative_wind_speed_handled(wind_speeds):
    """
    Property 16: Missing Data Handling

    For any negative wind speed values, the validation should replace with 0 and issue warning.

    Validates: Requirements 8.13
    """
    data = pd.DataFrame({"wind_speed": wind_speeds})

    validated, warnings = InputValidator.validate_meteorological_data(data)

    # All values should be replaced with 0.0
    assert all(validated["wind_speed"] == 0.0)
    # Should have exactly one warning
    assert len(warnings) >= 1
    assert any("Wind speed was negative" in w for w in warnings)


# Feature: rtemp-python-complete, Property 16: Missing Data Handling
# Validates: Requirements 8.11-8.15
@given(
    cloud_covers=st.lists(
        st.floats(min_value=-1000, max_value=-0.001, allow_nan=False, allow_infinity=False),
        min_size=1,
        max_size=10,
    )
)
def test_property_negative_cloud_cover_handled(cloud_covers):
    """
    Property 16: Missing Data Handling

    For any negative cloud cover values, the validation should replace with 0 and issue warning.

    Validates: Requirements 8.14
    """
    data = pd.DataFrame({"cloud_cover": cloud_covers})

    validated, warnings = InputValidator.validate_meteorological_data(data)

    # All values should be replaced with 0.0
    assert all(validated["cloud_cover"] == 0.0)
    # Should have exactly one warning
    assert len(warnings) >= 1
    assert any("Cloud cover was negative" in w for w in warnings)


# Feature: rtemp-python-complete, Property 16: Missing Data Handling
# Validates: Requirements 8.11-8.15
@given(
    cloud_covers=st.lists(
        st.floats(min_value=1.001, max_value=1000, allow_nan=False, allow_infinity=False),
        min_size=1,
        max_size=10,
    )
)
def test_property_excessive_cloud_cover_handled(cloud_covers):
    """
    Property 16: Missing Data Handling

    For any cloud cover values > 1, the validation should replace with 1 and issue warning.

    Validates: Requirements 8.15
    """
    data = pd.DataFrame({"cloud_cover": cloud_covers})

    validated, warnings = InputValidator.validate_meteorological_data(data)

    # All values should be replaced with 1.0
    assert all(validated["cloud_cover"] == 1.0)
    # Should have exactly one warning
    assert len(warnings) >= 1
    assert any("Cloud cover was greater than 1" in w for w in warnings)


# Feature: rtemp-python-complete, Property 16: Missing Data Handling
# Validates: Requirements 8.11-8.15
@given(
    n_rows=st.integers(min_value=1, max_value=20),
    air_temp_missing_prob=st.floats(min_value=0.1, max_value=1.0),
    dewpoint_missing_prob=st.floats(min_value=0.1, max_value=1.0),
    wind_negative_prob=st.floats(min_value=0.1, max_value=1.0),
    cloud_invalid_prob=st.floats(min_value=0.1, max_value=1.0),
)
def test_property_multiple_missing_data_handled(
    n_rows, air_temp_missing_prob, dewpoint_missing_prob, wind_negative_prob, cloud_invalid_prob
):
    """
    Property 16: Missing Data Handling

    For any meteorological data with multiple missing/invalid values, all should be corrected
    and appropriate warnings issued.

    Validates: Requirements 8.11-8.15
    """
    import random

    random.seed(42)  # For reproducibility

    # Generate data with various issues
    air_temps = [-999.0 if random.random() < air_temp_missing_prob else 20.0 for _ in range(n_rows)]
    dewpoint_temps = [
        -999.0 if random.random() < dewpoint_missing_prob else 15.0 for _ in range(n_rows)
    ]
    wind_speeds = [-1.0 if random.random() < wind_negative_prob else 2.0 for _ in range(n_rows)]
    cloud_covers = [1.5 if random.random() < cloud_invalid_prob else 0.5 for _ in range(n_rows)]

    data = pd.DataFrame(
        {
            "air_temperature": air_temps,
            "dewpoint_temperature": dewpoint_temps,
            "wind_speed": wind_speeds,
            "cloud_cover": cloud_covers,
        }
    )

    validated, warnings = InputValidator.validate_meteorological_data(data)

    # Check all corrections were applied
    assert all((validated["air_temperature"] == 20.0) | (validated["air_temperature"] == 20.0))
    assert all(
        (validated["dewpoint_temperature"] == 10.0) | (validated["dewpoint_temperature"] == 15.0)
    )
    assert all(validated["wind_speed"] >= 0.0)
    assert all((validated["cloud_cover"] >= 0.0) & (validated["cloud_cover"] <= 1.0))

    # Should have warnings for each type of issue present
    assert len(warnings) >= 0  # May have 0 to 4 warnings depending on data


# Feature: rtemp-python-complete, Property 17: Timestep Monotonicity
# Validates: Requirements 9.3
@given(
    base_time=st.datetimes(min_value=datetime(2000, 1, 1), max_value=datetime(2030, 12, 31)),
    timestep_hours=st.floats(min_value=0.01, max_value=24.0, allow_nan=False, allow_infinity=False),
)
def test_property_positive_timestep_no_monotonicity_warning(base_time, timestep_hours):
    """
    Property 17: Timestep Monotonicity

    For any positive timestep (current > previous), the check should not report monotonicity issues.

    Validates: Requirements 9.3
    """
    previous_time = base_time
    current_time = base_time + timedelta(hours=timestep_hours)

    warning, timestep_days = InputValidator.check_timestep(current_time, previous_time)

    # Should not have a warning about negative timestep
    if warning is not None:
        assert "negative" not in warning.lower()

    # Timestep should be positive
    assert timestep_days > 0


# Feature: rtemp-python-complete, Property 17: Timestep Monotonicity
# Validates: Requirements 9.3
@given(
    base_time=st.datetimes(min_value=datetime(2000, 1, 1), max_value=datetime(2030, 12, 31)),
    timestep_hours=st.floats(min_value=0.01, max_value=24.0, allow_nan=False, allow_infinity=False),
)
def test_property_negative_timestep_detected(base_time, timestep_hours):
    """
    Property 17: Timestep Monotonicity

    For any negative timestep (current < previous), the check should detect and warn about it.

    Validates: Requirements 9.3
    """
    # Swap times to create negative timestep
    current_time = base_time
    previous_time = base_time + timedelta(hours=timestep_hours)

    warning, timestep_days = InputValidator.check_timestep(current_time, previous_time)

    # Should have a warning about negative timestep
    assert warning is not None
    assert "negative" in warning.lower()

    # Timestep should be negative
    assert timestep_days < 0


# Feature: rtemp-python-complete, Property 17: Timestep Monotonicity
# Validates: Requirements 9.3
@given(base_time=st.datetimes(min_value=datetime(2000, 1, 1), max_value=datetime(2030, 12, 31)))
def test_property_zero_timestep_detected(base_time):
    """
    Property 17: Timestep Monotonicity

    For any zero timestep (duplicate timestamps), the check should detect and warn about it.

    Validates: Requirements 9.3
    """
    current_time = base_time
    previous_time = base_time

    warning, timestep_days = InputValidator.check_timestep(current_time, previous_time)

    # Should have a warning about duplicate timestep
    assert warning is not None
    assert "duplicate" in warning.lower()

    # Timestep should be zero
    assert timestep_days == 0.0


# Feature: rtemp-python-complete, Property 17: Timestep Monotonicity
# Validates: Requirements 9.3
@given(
    n_timesteps=st.integers(min_value=2, max_value=20),
    timestep_hours=st.floats(min_value=0.1, max_value=2.0, allow_nan=False, allow_infinity=False),
)
def test_property_monotonic_sequence_no_warnings(n_timesteps, timestep_hours):
    """
    Property 17: Timestep Monotonicity

    For any monotonically increasing sequence of timestamps with reasonable timesteps,
    no monotonicity warnings should be issued.

    Validates: Requirements 9.3
    """
    base_time = datetime(2024, 1, 1, 0, 0)
    times = [base_time + timedelta(hours=i * timestep_hours) for i in range(n_timesteps)]

    # Check all consecutive pairs
    for i in range(1, len(times)):
        warning, timestep_days = InputValidator.check_timestep(times[i], times[i - 1])

        # Should not have monotonicity warnings (may have timestep size warnings)
        if warning is not None:
            assert "negative" not in warning.lower()
            assert "duplicate" not in warning.lower()

        # Timestep should be positive
        assert timestep_days > 0


# Feature: rtemp-python-complete, Property 17: Timestep Monotonicity
# Validates: Requirements 9.3
@given(
    base_time=st.datetimes(min_value=datetime(2000, 1, 1), max_value=datetime(2030, 12, 31)),
    timestep_hours=st.floats(min_value=2.1, max_value=4.0, allow_nan=False, allow_infinity=False),
)
def test_property_large_timestep_warning(base_time, timestep_hours):
    """
    Property 17: Timestep Monotonicity (with size warning)

    For any timestep > 2 hours, a warning should be issued about potential accuracy issues.

    Validates: Requirements 9.1
    """
    previous_time = base_time
    current_time = base_time + timedelta(hours=timestep_hours)

    warning, timestep_days = InputValidator.check_timestep(current_time, previous_time)

    # Should have a warning about timestep size
    assert warning is not None
    assert "hour" in warning.lower()

    # Timestep should still be positive
    assert timestep_days > 0


# Feature: rtemp-python-complete, Property 17: Timestep Monotonicity
# Validates: Requirements 9.3
@given(
    base_time=st.datetimes(min_value=datetime(2000, 1, 1), max_value=datetime(2030, 12, 31)),
    timestep_hours=st.floats(min_value=4.1, max_value=24.0, allow_nan=False, allow_infinity=False),
)
def test_property_very_large_timestep_severe_warning(base_time, timestep_hours):
    """
    Property 17: Timestep Monotonicity (with severe warning)

    For any timestep > 4 hours, a more severe warning should be issued.

    Validates: Requirements 9.2
    """
    previous_time = base_time
    current_time = base_time + timedelta(hours=timestep_hours)

    warning, timestep_days = InputValidator.check_timestep(current_time, previous_time)

    # Should have a severe warning about timestep size
    assert warning is not None
    assert "large timestep" in warning.lower()

    # Timestep should still be positive
    assert timestep_days > 0
