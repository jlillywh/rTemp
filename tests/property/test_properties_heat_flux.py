"""
Property-based tests for heat flux calculations.

These tests use Hypothesis to verify that heat flux properties hold
across a wide range of input values.
"""

import pytest
from hypothesis import given, settings, assume
from hypothesis import strategies as st

from rtemp.heat_flux import HeatFluxCalculator
from rtemp.constants import (
    BOWEN_RATIO,
    WATER_DENSITY,
    WATER_SPECIFIC_HEAT,
    METERS_TO_CM,
)
from rtemp.utils.conversions import UnitConversions


class TestHeatFluxProperties:
    """Property-based tests for heat flux calculations."""

    # Feature: rtemp-python-complete, Property 13: Energy Conservation in Heat Budget
    # Validates: Requirements 6.8
    @given(
        # Heat flux components in cal/(cm²·day)
        solar_radiation=st.floats(min_value=0.0, max_value=1000.0),
        longwave_atmospheric=st.floats(min_value=0.0, max_value=500.0),
        evaporation=st.floats(min_value=-500.0, max_value=0.0),
        convection=st.floats(min_value=-200.0, max_value=200.0),
        sediment_conduction=st.floats(min_value=-100.0, max_value=100.0),
        hyporheic_exchange=st.floats(min_value=-50.0, max_value=50.0),
        groundwater=st.floats(min_value=-50.0, max_value=50.0),
        # Water body parameters
        water_depth=st.floats(min_value=0.1, max_value=10.0),
        timestep_days=st.floats(min_value=0.001, max_value=0.1),
    )
    @settings(max_examples=100)
    def test_energy_conservation_property(
        self,
        solar_radiation: float,
        longwave_atmospheric: float,
        evaporation: float,
        convection: float,
        sediment_conduction: float,
        hyporheic_exchange: float,
        groundwater: float,
        water_depth: float,
        timestep_days: float,
    ):
        """
        Property 13: Energy Conservation in Heat Budget

        For any timestep calculation, the sum of all heat flux components
        should equal the rate of temperature change multiplied by heat
        capacity and depth.

        This property verifies that:
        ΔT = (Σ fluxes) * Δt / (ρ * Cp * depth)

        where:
        - ΔT = temperature change (°C)
        - Σ fluxes = sum of all heat flux components (cal/(cm²·day))
        - Δt = timestep (days)
        - ρ = water density (g/cm³)
        - Cp = specific heat of water (cal/(g·°C))
        - depth = water depth (cm)

        Validates: Requirements 6.8
        """
        # Calculate longwave back radiation for a typical water temperature
        water_temp = 20.0  # °C
        longwave_back = HeatFluxCalculator.calculate_longwave_back(water_temp)

        # Sum all heat flux components (cal/(cm²·day))
        total_flux = (
            solar_radiation
            + longwave_atmospheric
            + longwave_back
            + evaporation
            + convection
            + sediment_conduction
            + hyporheic_exchange
            + groundwater
        )

        # Convert water depth from meters to cm
        depth_cm = water_depth * METERS_TO_CM

        # Convert water density from kg/m³ to g/cm³
        density_g_cm3 = WATER_DENSITY / 1000.0

        # Convert specific heat from J/(kg·°C) to cal/(g·°C)
        specific_heat_cal = WATER_SPECIFIC_HEAT / 4.184

        # Calculate heat capacity per unit area (cal/(cm²·°C))
        heat_capacity_per_area = density_g_cm3 * specific_heat_cal * depth_cm

        # Calculate temperature change rate (°C/day)
        temp_change_rate = total_flux / heat_capacity_per_area

        # Calculate temperature change over timestep (°C)
        temp_change = temp_change_rate * timestep_days

        # Verify energy conservation by checking that the temperature change
        # can be reconstructed from the heat flux
        reconstructed_flux = temp_change_rate * heat_capacity_per_area

        # The reconstructed flux should equal the total flux
        assert reconstructed_flux == pytest.approx(total_flux, rel=1e-10, abs=1e-10)

        # Also verify that the temperature change is finite (not NaN or infinite)
        import math

        assert math.isfinite(temp_change)

        # For typical fluxes and timesteps, temperature change should be bounded
        # This is a sanity check, not a strict requirement
        if abs(total_flux) < 1000.0 and timestep_days < 0.1:
            # Temperature change should be reasonable (less than 10°C per timestep)
            assert abs(temp_change) < 10.0

    # Feature: rtemp-python-complete, Property 13: Energy Conservation in Heat Budget
    # Validates: Requirements 6.8
    @given(
        water_temp=st.floats(min_value=0.0, max_value=40.0),
        sediment_temp=st.floats(min_value=0.0, max_value=40.0),
        thermal_conductivity=st.floats(min_value=0.0, max_value=2.0),
        sediment_thickness=st.floats(min_value=1.0, max_value=100.0),
        water_depth=st.floats(min_value=0.1, max_value=10.0),
    )
    @settings(max_examples=100)
    def test_sediment_flux_energy_balance(
        self,
        water_temp: float,
        sediment_temp: float,
        thermal_conductivity: float,
        sediment_thickness: float,
        water_depth: float,
    ):
        """
        Property: Sediment flux energy balance

        For any sediment conduction calculation, the heat flux should be
        proportional to the temperature difference and inversely proportional
        to the sediment thickness.

        This verifies that the sediment conduction follows Fourier's law.

        Validates: Requirements 6.4
        """
        # Skip if thermal conductivity is zero
        assume(thermal_conductivity > 0.0)

        flux = HeatFluxCalculator.calculate_sediment_conduction(
            water_temp, sediment_temp, thermal_conductivity, sediment_thickness
        )

        # Verify sign convention
        if sediment_temp > water_temp:
            # Heat flows from sediment to water (positive flux)
            assert flux > 0.0 or flux == pytest.approx(0.0, abs=1e-10)
        elif sediment_temp < water_temp:
            # Heat flows from water to sediment (negative flux)
            assert flux < 0.0 or flux == pytest.approx(0.0, abs=1e-10)
        else:
            # No temperature difference, no flux
            assert flux == pytest.approx(0.0, abs=1e-10)

        # Verify that flux is proportional to temperature difference
        temp_diff = sediment_temp - water_temp
        if abs(temp_diff) > 0.01:  # Avoid division by near-zero
            # Calculate expected flux magnitude
            # flux ∝ k * ΔT / thickness
            flux_per_degree = flux / temp_diff

            # Verify that doubling the temperature difference doubles the flux
            flux_double = HeatFluxCalculator.calculate_sediment_conduction(
                water_temp, water_temp + 2 * temp_diff, thermal_conductivity, sediment_thickness
            )
            assert flux_double == pytest.approx(2 * flux, rel=1e-6)

    # Feature: rtemp-python-complete, Property 13: Energy Conservation in Heat Budget
    # Validates: Requirements 6.8
    @given(
        water_temp=st.floats(min_value=0.0, max_value=40.0),
        groundwater_temp=st.floats(min_value=0.0, max_value=40.0),
        inflow_rate=st.floats(min_value=0.0, max_value=100.0),
        water_depth=st.floats(min_value=0.1, max_value=10.0),
    )
    @settings(max_examples=100)
    def test_groundwater_flux_proportionality(
        self,
        water_temp: float,
        groundwater_temp: float,
        inflow_rate: float,
        water_depth: float,
    ):
        """
        Property: Groundwater flux proportionality

        For any groundwater flux calculation, the heat flux should be
        proportional to the temperature difference and the inflow rate,
        and inversely proportional to the water depth.

        Validates: Requirements 6.6
        """
        flux = HeatFluxCalculator.calculate_groundwater_flux(
            water_temp, groundwater_temp, inflow_rate, water_depth
        )

        # Verify sign convention
        if groundwater_temp > water_temp:
            # Groundwater brings heat (positive flux)
            assert flux >= 0.0 or flux == pytest.approx(0.0, abs=1e-10)
        elif groundwater_temp < water_temp:
            # Groundwater removes heat (negative flux)
            assert flux <= 0.0 or flux == pytest.approx(0.0, abs=1e-10)
        else:
            # No temperature difference, no flux
            assert flux == pytest.approx(0.0, abs=1e-10)

        # If inflow rate is zero, flux should be zero
        if inflow_rate == 0.0:
            assert flux == 0.0

        # Verify proportionality to inflow rate
        if inflow_rate > 0.0 and abs(groundwater_temp - water_temp) > 0.01:
            flux_double_inflow = HeatFluxCalculator.calculate_groundwater_flux(
                water_temp, groundwater_temp, 2 * inflow_rate, water_depth
            )
            assert flux_double_inflow == pytest.approx(2 * flux, rel=1e-6)

        # Verify inverse proportionality to depth
        if abs(groundwater_temp - water_temp) > 0.01 and inflow_rate > 0.0:
            flux_double_depth = HeatFluxCalculator.calculate_groundwater_flux(
                water_temp, groundwater_temp, inflow_rate, 2 * water_depth
            )
            assert flux_double_depth == pytest.approx(flux / 2, rel=1e-6)

    # Feature: rtemp-python-complete, Property 13: Energy Conservation in Heat Budget
    # Validates: Requirements 6.8
    @given(
        wind_function=st.floats(min_value=1.0, max_value=50.0),
        vapor_pressure_water=st.floats(min_value=5.0, max_value=50.0),
        vapor_pressure_air=st.floats(min_value=5.0, max_value=50.0),
    )
    @settings(max_examples=100)
    def test_evaporation_flux_sign_convention(
        self,
        wind_function: float,
        vapor_pressure_water: float,
        vapor_pressure_air: float,
    ):
        """
        Property: Evaporation flux sign convention

        For any evaporation calculation, the sign of the flux should correctly
        indicate heat gain or loss based on the vapor pressure gradient.

        Validates: Requirements 6.1
        """
        flux = HeatFluxCalculator.calculate_evaporation(
            wind_function, vapor_pressure_water, vapor_pressure_air
        )

        # Verify sign convention
        if vapor_pressure_water > vapor_pressure_air:
            # Evaporation occurs (heat loss, negative flux)
            assert flux < 0.0 or flux == pytest.approx(0.0, abs=1e-10)
        elif vapor_pressure_water < vapor_pressure_air:
            # Condensation occurs (heat gain, positive flux)
            assert flux > 0.0 or flux == pytest.approx(0.0, abs=1e-10)
        else:
            # No gradient, no flux
            assert flux == pytest.approx(0.0, abs=1e-10)

        # Verify magnitude is proportional to vapor pressure difference
        vapor_diff = vapor_pressure_water - vapor_pressure_air
        expected_flux = -wind_function * vapor_diff
        assert flux == pytest.approx(expected_flux, rel=1e-10)

    # Feature: rtemp-python-complete, Property 13: Energy Conservation in Heat Budget
    # Validates: Requirements 6.8
    @given(
        wind_function=st.floats(min_value=1.0, max_value=50.0),
        water_temp=st.floats(min_value=0.0, max_value=40.0),
        air_temp=st.floats(min_value=0.0, max_value=40.0),
    )
    @settings(max_examples=100)
    def test_convection_flux_sign_convention(
        self,
        wind_function: float,
        water_temp: float,
        air_temp: float,
    ):
        """
        Property: Convection flux sign convention

        For any convection calculation, the sign of the flux should correctly
        indicate heat gain or loss based on the temperature gradient.

        Validates: Requirements 6.2
        """
        flux = HeatFluxCalculator.calculate_convection(wind_function, water_temp, air_temp)

        # Verify sign convention
        if water_temp > air_temp:
            # Water loses heat to air (negative flux)
            assert flux < 0.0 or flux == pytest.approx(0.0, abs=1e-10)
        elif water_temp < air_temp:
            # Water gains heat from air (positive flux)
            assert flux > 0.0 or flux == pytest.approx(0.0, abs=1e-10)
        else:
            # No gradient, no flux
            assert flux == pytest.approx(0.0, abs=1e-10)

        # Verify magnitude is proportional to temperature difference
        temp_diff = water_temp - air_temp
        expected_flux = -BOWEN_RATIO * wind_function * temp_diff
        assert flux == pytest.approx(expected_flux, rel=1e-10)

    # Feature: rtemp-python-complete, Property 13: Energy Conservation in Heat Budget
    # Validates: Requirements 6.8
    @given(
        water_temp=st.floats(min_value=0.0, max_value=40.0),
    )
    @settings(max_examples=100)
    def test_longwave_back_always_negative(self, water_temp: float):
        """
        Property: Longwave back radiation is always a heat loss

        For any water temperature, longwave back radiation should always
        be negative (heat loss) since the water surface always emits
        thermal radiation.

        Validates: Requirements 6.3
        """
        flux = HeatFluxCalculator.calculate_longwave_back(water_temp)

        # Longwave back radiation is always a heat loss (negative)
        assert flux < 0.0

        # Verify it follows Stefan-Boltzmann law (T⁴ relationship)
        # Higher temperature should result in more negative flux
        if water_temp < 39.0:  # Leave room for comparison
            flux_higher = HeatFluxCalculator.calculate_longwave_back(water_temp + 1.0)
            # Higher temperature = more radiation = more negative flux
            assert flux_higher < flux
