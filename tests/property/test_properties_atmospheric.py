"""
Property-based tests for atmospheric helper functions.

This module contains property-based tests using Hypothesis to verify
correctness properties of atmospheric calculations including vapor pressure,
humidity, and pressure calculations.
"""

import pytest
from hypothesis import given, settings, strategies as st

from rtemp.utils.atmospheric import AtmosphericHelpers
from rtemp.atmospheric import (
    EmissivityBrunt,
    EmissivityBrutsaert,
    EmissivitySatterlund,
    EmissivityIdsoJackson,
    EmissivitySwinbank,
    EmissivityKoberg,
)


class TestAtmosphericProperties:
    """Property-based tests for atmospheric helper functions."""

    @given(
        temp1=st.floats(min_value=-50.0, max_value=50.0),
        temp2=st.floats(min_value=-50.0, max_value=50.0),
    )
    @settings(max_examples=100)
    def test_vapor_pressure_monotonicity(self, temp1: float, temp2: float):
        """
        Feature: rtemp-python-complete, Property 19: Vapor Pressure Monotonicity
        Validates: Requirements 12.1

        Property: For any two temperatures T1 < T2, saturation vapor pressure
        at T1 should be less than saturation vapor pressure at T2.

        This tests that vapor pressure increases monotonically with temperature.
        """
        # Skip if temperatures are equal (within floating point tolerance)
        if abs(temp1 - temp2) < 1e-6:
            return

        # Ensure temp1 < temp2
        if temp1 > temp2:
            temp1, temp2 = temp2, temp1

        # Calculate vapor pressures
        vp1 = AtmosphericHelpers.saturation_vapor_pressure(temp1)
        vp2 = AtmosphericHelpers.saturation_vapor_pressure(temp2)

        # Assert monotonicity: VP(T1) < VP(T2) when T1 < T2
        assert vp1 < vp2, (
            f"Vapor pressure should increase with temperature: "
            f"VP({temp1}°C) = {vp1} mmHg should be < VP({temp2}°C) = {vp2} mmHg"
        )

        # Also verify both are positive
        assert vp1 > 0, f"Vapor pressure at {temp1}°C should be positive"
        assert vp2 > 0, f"Vapor pressure at {temp2}°C should be positive"

    @given(
        air_temp=st.floats(min_value=-20.0, max_value=50.0),
        rh=st.floats(min_value=0.01, max_value=1.0),
    )
    @settings(max_examples=100)
    def test_dewpoint_rh_round_trip(self, air_temp: float, rh: float):
        """
        Feature: rtemp-python-complete, Property 20: Dewpoint-RH Round Trip
        Validates: Requirements 12.2-12.3

        Property: For any air temperature and relative humidity, calculating
        dewpoint from RH and then calculating RH from that dewpoint should
        produce the original RH within numerical precision.

        This tests the consistency of dewpoint_from_rh and
        relative_humidity_from_dewpoint functions.
        """
        # Calculate dewpoint from air temperature and RH
        dewpoint = AtmosphericHelpers.dewpoint_from_rh(air_temp, rh)

        # Calculate RH back from air temperature and dewpoint
        rh_recovered = AtmosphericHelpers.relative_humidity_from_dewpoint(air_temp, dewpoint)

        # Assert round trip consistency within tolerance
        # Use relative tolerance for better handling of small values
        tolerance = 0.01  # 1% tolerance
        assert abs(rh_recovered - rh) < tolerance, (
            f"Round trip failed: RH {rh} -> dewpoint {dewpoint}°C -> "
            f"RH {rh_recovered}. Difference: {abs(rh_recovered - rh)}"
        )

        # Verify dewpoint is less than or equal to air temperature (with small tolerance for floating point)
        assert (
            dewpoint <= air_temp + 1e-10
        ), f"Dewpoint ({dewpoint}°C) should not exceed air temperature ({air_temp}°C)"


class TestLongwaveEmissivityProperties:
    """Property-based tests for longwave emissivity models."""

    @given(
        air_temp=st.floats(min_value=-40.0, max_value=50.0),
        vapor_pressure=st.floats(min_value=0.1, max_value=50.0),
        clearness=st.floats(min_value=0.0, max_value=1.0),
        brutsaert_coeff=st.floats(min_value=1.0, max_value=1.5),
    )
    @settings(max_examples=100)
    def test_emissivity_bounds(
        self,
        air_temp: float,
        vapor_pressure: float,
        clearness: float,
        brutsaert_coeff: float,
    ):
        """
        Feature: rtemp-python-complete, Property 9: Longwave Emissivity Bounds
        Validates: Requirements 4.1-4.6

        Property: For any longwave radiation emissivity calculation method and
        inputs, the calculated emissivity should be between 0 and 1 inclusive.

        This tests that all emissivity models produce physically valid results
        (emissivity must be between 0 for no emission and 1 for perfect blackbody).
        """
        # Test Brunt model
        brunt = EmissivityBrunt()
        emissivity_brunt = brunt.calculate(air_temp, vapor_pressure)
        assert 0.0 <= emissivity_brunt <= 1.0, (
            f"Brunt emissivity {emissivity_brunt} out of bounds [0, 1] "
            f"for T={air_temp}°C, VP={vapor_pressure} mmHg"
        )

        # Test Brutsaert model
        brutsaert = EmissivityBrutsaert(coefficient=brutsaert_coeff)
        emissivity_brutsaert = brutsaert.calculate(air_temp, vapor_pressure)
        assert 0.0 <= emissivity_brutsaert <= 1.0, (
            f"Brutsaert emissivity {emissivity_brutsaert} out of bounds [0, 1] "
            f"for T={air_temp}°C, VP={vapor_pressure} mmHg, coeff={brutsaert_coeff}"
        )

        # Test Satterlund model
        satterlund = EmissivitySatterlund()
        emissivity_satterlund = satterlund.calculate(air_temp, vapor_pressure)
        assert 0.0 <= emissivity_satterlund <= 1.0, (
            f"Satterlund emissivity {emissivity_satterlund} out of bounds [0, 1] "
            f"for T={air_temp}°C, VP={vapor_pressure} mmHg"
        )

        # Test Idso-Jackson model
        idso_jackson = EmissivityIdsoJackson()
        emissivity_idso = idso_jackson.calculate(air_temp, vapor_pressure)
        assert 0.0 <= emissivity_idso <= 1.0, (
            f"Idso-Jackson emissivity {emissivity_idso} out of bounds [0, 1] " f"for T={air_temp}°C"
        )

        # Test Swinbank model
        swinbank = EmissivitySwinbank()
        emissivity_swinbank = swinbank.calculate(air_temp, vapor_pressure)
        assert 0.0 <= emissivity_swinbank <= 1.0, (
            f"Swinbank emissivity {emissivity_swinbank} out of bounds [0, 1] " f"for T={air_temp}°C"
        )

        # Test Koberg model
        koberg = EmissivityKoberg()
        emissivity_koberg = koberg.calculate(air_temp, vapor_pressure, clearness=clearness)
        assert 0.0 <= emissivity_koberg <= 1.0, (
            f"Koberg emissivity {emissivity_koberg} out of bounds [0, 1] "
            f"for T={air_temp}°C, VP={vapor_pressure} mmHg, clearness={clearness}"
        )


class TestLongwaveRadiationProperties:
    """Property-based tests for longwave radiation calculations."""

    @given(
        emissivity=st.floats(min_value=0.5, max_value=1.0),
        temp1=st.floats(min_value=-20.0, max_value=40.0),
        temp2=st.floats(min_value=-20.0, max_value=40.0),
        cloud_cover=st.floats(min_value=0.0, max_value=1.0),
        kcl3=st.floats(min_value=0.5, max_value=1.5),
        kcl4=st.floats(min_value=1.0, max_value=3.0),
    )
    @settings(max_examples=100)
    def test_longwave_increases_with_temperature(
        self,
        emissivity: float,
        temp1: float,
        temp2: float,
        cloud_cover: float,
        kcl3: float,
        kcl4: float,
    ):
        """
        Feature: rtemp-python-complete, Property 10: Longwave Radiation Increases with Temperature
        Validates: Requirements 4.10

        Property: For any longwave radiation calculation method, increasing air
        temperature should monotonically increase atmospheric longwave radiation.

        This tests that longwave radiation follows the Stefan-Boltzmann law's
        T^4 dependence, ensuring that warmer air produces more longwave radiation.
        """
        from rtemp.atmospheric import LongwaveRadiation

        # Skip if temperatures are equal (within floating point tolerance)
        if abs(temp1 - temp2) < 1e-6:
            return

        # Ensure temp1 < temp2
        if temp1 > temp2:
            temp1, temp2 = temp2, temp1

        # Test with Equation 1 cloud correction
        longwave1_eqn1 = LongwaveRadiation.calculate_atmospheric(
            emissivity, temp1, cloud_cover, cloud_method="Eqn 1", kcl3=kcl3, kcl4=kcl4
        )
        longwave2_eqn1 = LongwaveRadiation.calculate_atmospheric(
            emissivity, temp2, cloud_cover, cloud_method="Eqn 1", kcl3=kcl3, kcl4=kcl4
        )

        # Assert monotonicity: L(T1) < L(T2) when T1 < T2
        assert longwave1_eqn1 < longwave2_eqn1, (
            f"Longwave radiation (Eqn 1) should increase with temperature: "
            f"L({temp1}°C) = {longwave1_eqn1} W/m² should be < "
            f"L({temp2}°C) = {longwave2_eqn1} W/m² "
            f"(emissivity={emissivity}, cloud_cover={cloud_cover})"
        )

        # Test with Equation 2 cloud correction
        longwave1_eqn2 = LongwaveRadiation.calculate_atmospheric(
            emissivity, temp1, cloud_cover, cloud_method="Eqn 2", kcl3=kcl3, kcl4=kcl4
        )
        longwave2_eqn2 = LongwaveRadiation.calculate_atmospheric(
            emissivity, temp2, cloud_cover, cloud_method="Eqn 2", kcl3=kcl3, kcl4=kcl4
        )

        # Assert monotonicity for Equation 2 as well
        assert longwave1_eqn2 < longwave2_eqn2, (
            f"Longwave radiation (Eqn 2) should increase with temperature: "
            f"L({temp1}°C) = {longwave1_eqn2} W/m² should be < "
            f"L({temp2}°C) = {longwave2_eqn2} W/m² "
            f"(emissivity={emissivity}, cloud_cover={cloud_cover})"
        )

        # Verify both values are positive
        assert longwave1_eqn1 > 0, "Longwave radiation should be positive"
        assert longwave2_eqn1 > 0, "Longwave radiation should be positive"
        assert longwave1_eqn2 > 0, "Longwave radiation should be positive"
        assert longwave2_eqn2 > 0, "Longwave radiation should be positive"
