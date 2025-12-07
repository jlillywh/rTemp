"""
Unit tests for longwave emissivity models.

This module contains unit tests for the various atmospheric emissivity
calculation methods used in longwave radiation modeling.
"""

import pytest
import math

from rtemp.atmospheric import (
    EmissivityBrunt,
    EmissivityBrutsaert,
    EmissivitySatterlund,
    EmissivityIdsoJackson,
    EmissivitySwinbank,
    EmissivityKoberg,
)


class TestEmissivityBrunt:
    """Unit tests for Brunt emissivity model."""

    def test_brunt_typical_conditions(self):
        """Test Brunt model under typical atmospheric conditions."""
        brunt = EmissivityBrunt()
        # Typical conditions: 20°C, 10 mmHg vapor pressure
        emissivity = brunt.calculate(air_temp_c=20.0, vapor_pressure_mmhg=10.0)

        # Expected: 0.52 + 0.065 * sqrt(10) ≈ 0.726
        expected = 0.52 + 0.065 * math.sqrt(10.0)
        assert abs(emissivity - expected) < 0.001
        assert 0.0 <= emissivity <= 1.0

    def test_brunt_low_humidity(self):
        """Test Brunt model with low humidity (low vapor pressure)."""
        brunt = EmissivityBrunt()
        emissivity = brunt.calculate(air_temp_c=20.0, vapor_pressure_mmhg=1.0)

        # Lower vapor pressure should give lower emissivity
        assert 0.5 < emissivity < 0.6
        assert 0.0 <= emissivity <= 1.0

    def test_brunt_high_humidity(self):
        """Test Brunt model with high humidity (high vapor pressure)."""
        brunt = EmissivityBrunt()
        emissivity = brunt.calculate(air_temp_c=30.0, vapor_pressure_mmhg=30.0)

        # Higher vapor pressure should give higher emissivity
        assert 0.8 < emissivity <= 1.0


class TestEmissivityBrutsaert:
    """Unit tests for Brutsaert emissivity model."""

    def test_brutsaert_default_coefficient(self):
        """Test Brutsaert model with default coefficient."""
        brutsaert = EmissivityBrutsaert()
        emissivity = brutsaert.calculate(air_temp_c=20.0, vapor_pressure_mmhg=10.0)

        assert 0.0 <= emissivity <= 1.0
        # Should be in reasonable range for typical conditions
        assert 0.6 < emissivity < 0.9

    def test_brutsaert_custom_coefficient(self):
        """Test Brutsaert model with custom coefficient."""
        brutsaert_low = EmissivityBrutsaert(coefficient=1.0)
        brutsaert_high = EmissivityBrutsaert(coefficient=1.5)

        emissivity_low = brutsaert_low.calculate(air_temp_c=20.0, vapor_pressure_mmhg=10.0)
        emissivity_high = brutsaert_high.calculate(air_temp_c=20.0, vapor_pressure_mmhg=10.0)

        # Higher coefficient should give higher emissivity
        assert emissivity_high > emissivity_low
        assert 0.0 <= emissivity_low <= 1.0
        assert 0.0 <= emissivity_high <= 1.0

    def test_brutsaert_temperature_effect(self):
        """Test that Brutsaert model responds to temperature changes."""
        brutsaert = EmissivityBrutsaert()

        emissivity_cold = brutsaert.calculate(air_temp_c=0.0, vapor_pressure_mmhg=5.0)
        emissivity_warm = brutsaert.calculate(air_temp_c=30.0, vapor_pressure_mmhg=5.0)

        # At same vapor pressure, colder air should have higher emissivity
        assert emissivity_cold > emissivity_warm


class TestEmissivitySatterlund:
    """Unit tests for Satterlund emissivity model."""

    def test_satterlund_typical_conditions(self):
        """Test Satterlund model under typical conditions."""
        satterlund = EmissivitySatterlund()
        emissivity = satterlund.calculate(air_temp_c=20.0, vapor_pressure_mmhg=10.0)

        assert 0.0 <= emissivity <= 1.0
        # Satterlund typically gives values in this range
        assert 0.7 < emissivity < 1.0

    def test_satterlund_low_vapor_pressure(self):
        """Test Satterlund model with low vapor pressure."""
        satterlund = EmissivitySatterlund()
        emissivity = satterlund.calculate(air_temp_c=20.0, vapor_pressure_mmhg=1.0)

        assert 0.0 <= emissivity <= 1.0
        # Lower vapor pressure should give lower emissivity
        assert emissivity < 0.9


class TestEmissivityIdsoJackson:
    """Unit tests for Idso-Jackson emissivity model."""

    def test_idso_jackson_typical_conditions(self):
        """Test Idso-Jackson model (temperature-only)."""
        idso = EmissivityIdsoJackson()
        emissivity = idso.calculate(air_temp_c=20.0, vapor_pressure_mmhg=10.0)

        assert 0.0 <= emissivity <= 1.0
        # Should be in reasonable range
        assert 0.7 < emissivity < 0.9

    def test_idso_jackson_ignores_vapor_pressure(self):
        """Test that Idso-Jackson doesn't depend on vapor pressure."""
        idso = EmissivityIdsoJackson()

        emissivity_low_vp = idso.calculate(air_temp_c=20.0, vapor_pressure_mmhg=1.0)
        emissivity_high_vp = idso.calculate(air_temp_c=20.0, vapor_pressure_mmhg=30.0)

        # Should be identical since model only uses temperature
        assert abs(emissivity_low_vp - emissivity_high_vp) < 1e-10

    def test_idso_jackson_temperature_effect(self):
        """Test that Idso-Jackson responds to temperature."""
        idso = EmissivityIdsoJackson()

        emissivity_cold = idso.calculate(air_temp_c=-10.0, vapor_pressure_mmhg=5.0)
        emissivity_warm = idso.calculate(air_temp_c=30.0, vapor_pressure_mmhg=5.0)

        # Both should be valid
        assert 0.0 <= emissivity_cold <= 1.0
        assert 0.0 <= emissivity_warm <= 1.0
        # Warmer should have higher emissivity
        assert emissivity_warm > emissivity_cold


class TestEmissivitySwinbank:
    """Unit tests for Swinbank emissivity model."""

    def test_swinbank_typical_conditions(self):
        """Test Swinbank model (temperature-only)."""
        swinbank = EmissivitySwinbank()
        emissivity = swinbank.calculate(air_temp_c=20.0, vapor_pressure_mmhg=10.0)

        assert 0.0 <= emissivity <= 1.0
        # Swinbank typically gives values in this range
        assert 0.7 < emissivity < 0.9

    def test_swinbank_ignores_vapor_pressure(self):
        """Test that Swinbank doesn't depend on vapor pressure."""
        swinbank = EmissivitySwinbank()

        emissivity_low_vp = swinbank.calculate(air_temp_c=20.0, vapor_pressure_mmhg=1.0)
        emissivity_high_vp = swinbank.calculate(air_temp_c=20.0, vapor_pressure_mmhg=30.0)

        # Should be identical since model only uses temperature
        assert abs(emissivity_low_vp - emissivity_high_vp) < 1e-10

    def test_swinbank_temperature_effect(self):
        """Test that Swinbank responds to temperature."""
        swinbank = EmissivitySwinbank()

        emissivity_cold = swinbank.calculate(air_temp_c=0.0, vapor_pressure_mmhg=5.0)
        emissivity_warm = swinbank.calculate(air_temp_c=30.0, vapor_pressure_mmhg=5.0)

        # Warmer should have higher emissivity (quadratic relationship)
        assert emissivity_warm > emissivity_cold
        assert 0.0 <= emissivity_cold <= 1.0
        assert 0.0 <= emissivity_warm <= 1.0


class TestEmissivityKoberg:
    """Unit tests for Koberg emissivity model."""

    def test_koberg_typical_conditions(self):
        """Test Koberg model under typical conditions."""
        koberg = EmissivityKoberg()
        emissivity = koberg.calculate(air_temp_c=20.0, vapor_pressure_mmhg=10.0, clearness=0.8)

        assert 0.0 <= emissivity <= 1.0
        # Should be in reasonable range
        assert 0.6 < emissivity < 0.9

    def test_koberg_clearness_effect(self):
        """Test that clearness affects Koberg emissivity."""
        koberg = EmissivityKoberg()

        emissivity_cloudy = koberg.calculate(
            air_temp_c=20.0, vapor_pressure_mmhg=10.0, clearness=0.2
        )
        emissivity_clear = koberg.calculate(
            air_temp_c=20.0, vapor_pressure_mmhg=10.0, clearness=1.0
        )

        # Higher clearness should give higher emissivity
        assert emissivity_clear > emissivity_cloudy
        assert 0.0 <= emissivity_cloudy <= 1.0
        assert 0.0 <= emissivity_clear <= 1.0

    def test_koberg_default_clearness(self):
        """Test Koberg with default clearness (clear sky)."""
        koberg = EmissivityKoberg()

        # Should work without specifying clearness
        emissivity = koberg.calculate(air_temp_c=20.0, vapor_pressure_mmhg=10.0)

        assert 0.0 <= emissivity <= 1.0

    def test_koberg_temperature_effect(self):
        """Test that temperature affects Koberg emissivity."""
        koberg = EmissivityKoberg()

        emissivity_cold = koberg.calculate(air_temp_c=0.0, vapor_pressure_mmhg=10.0, clearness=0.8)
        emissivity_warm = koberg.calculate(air_temp_c=30.0, vapor_pressure_mmhg=10.0, clearness=0.8)

        # Warmer should have higher emissivity
        assert emissivity_warm > emissivity_cold
        assert 0.0 <= emissivity_cold <= 1.0
        assert 0.0 <= emissivity_warm <= 1.0


class TestEmissivityComparison:
    """Compare different emissivity models under same conditions."""

    def test_all_models_produce_valid_emissivity(self):
        """Test that all models produce valid emissivity values."""
        air_temp = 20.0
        vapor_pressure = 10.0

        brunt = EmissivityBrunt()
        brutsaert = EmissivityBrutsaert()
        satterlund = EmissivitySatterlund()
        idso = EmissivityIdsoJackson()
        swinbank = EmissivitySwinbank()
        koberg = EmissivityKoberg()

        models = [
            ("Brunt", brunt),
            ("Brutsaert", brutsaert),
            ("Satterlund", satterlund),
            ("Idso-Jackson", idso),
            ("Swinbank", swinbank),
            ("Koberg", koberg),
        ]

        for name, model in models:
            emissivity = model.calculate(air_temp, vapor_pressure)
            assert 0.0 <= emissivity <= 1.0, f"{name} produced invalid emissivity: {emissivity}"

    def test_models_give_different_results(self):
        """Test that different models give different results (as expected)."""
        air_temp = 20.0
        vapor_pressure = 10.0

        brunt = EmissivityBrunt()
        brutsaert = EmissivityBrutsaert()
        satterlund = EmissivitySatterlund()

        e_brunt = brunt.calculate(air_temp, vapor_pressure)
        e_brutsaert = brutsaert.calculate(air_temp, vapor_pressure)
        e_satterlund = satterlund.calculate(air_temp, vapor_pressure)

        # Models should give different results (they use different formulas)
        # But all should be in reasonable range
        emissivities = [e_brunt, e_brutsaert, e_satterlund]
        assert len(set(emissivities)) > 1, "All models gave identical results"
        assert all(0.6 < e < 1.0 for e in emissivities), "Some emissivities out of expected range"
