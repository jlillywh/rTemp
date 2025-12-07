"""
Unit tests for solar radiation corrections.

These tests verify the correct behavior of cloud cover, shade, and albedo
corrections applied to solar radiation calculations.
"""

import pytest
import math
from rtemp.solar.corrections import SolarRadiationCorrections


class TestCloudCoverCorrection:
    """Tests for cloud cover correction."""

    def test_clear_sky_no_correction(self):
        """Test that clear sky (cloud_cover=0) applies no correction."""
        radiation = 1000.0
        result = SolarRadiationCorrections.apply_cloud_correction(
            radiation, cloud_cover=0.0, kcl1=1.0, kcl2=2.0
        )
        assert result == radiation

    def test_overcast_reduces_radiation(self):
        """Test that overcast conditions (cloud_cover=1) reduce radiation."""
        radiation = 1000.0
        result = SolarRadiationCorrections.apply_cloud_correction(
            radiation, cloud_cover=1.0, kcl1=1.0, kcl2=2.0
        )
        assert result < radiation
        assert result >= 0.0

    def test_partial_cloud_intermediate_reduction(self):
        """Test that partial cloud cover gives intermediate reduction."""
        radiation = 1000.0
        clear = SolarRadiationCorrections.apply_cloud_correction(
            radiation, cloud_cover=0.0, kcl1=1.0, kcl2=2.0
        )
        partial = SolarRadiationCorrections.apply_cloud_correction(
            radiation, cloud_cover=0.5, kcl1=1.0, kcl2=2.0
        )
        overcast = SolarRadiationCorrections.apply_cloud_correction(
            radiation, cloud_cover=1.0, kcl1=1.0, kcl2=2.0
        )

        assert overcast <= partial <= clear

    def test_kcl1_controls_magnitude(self):
        """Test that KCL1 parameter controls magnitude of cloud effect."""
        radiation = 1000.0
        cloud_cover = 0.5

        result_low = SolarRadiationCorrections.apply_cloud_correction(
            radiation, cloud_cover, kcl1=0.5, kcl2=2.0
        )
        result_high = SolarRadiationCorrections.apply_cloud_correction(
            radiation, cloud_cover, kcl1=1.0, kcl2=2.0
        )

        # Higher KCL1 should give more reduction
        assert result_high < result_low

    def test_kcl2_controls_shape(self):
        """Test that KCL2 parameter controls shape of cloud effect curve."""
        radiation = 1000.0
        cloud_cover = 0.5

        result_linear = SolarRadiationCorrections.apply_cloud_correction(
            radiation, cloud_cover, kcl1=1.0, kcl2=1.0
        )
        result_quadratic = SolarRadiationCorrections.apply_cloud_correction(
            radiation, cloud_cover, kcl1=1.0, kcl2=2.0
        )

        # Different KCL2 values should give different results
        assert result_linear != result_quadratic

    def test_negative_cloud_cover_clamped(self):
        """Test that negative cloud cover is clamped to zero."""
        radiation = 1000.0
        result = SolarRadiationCorrections.apply_cloud_correction(
            radiation, cloud_cover=-0.5, kcl1=1.0, kcl2=2.0
        )
        # Should behave as if cloud_cover=0
        assert result == radiation

    def test_excessive_cloud_cover_clamped(self):
        """Test that cloud cover > 1 is clamped to 1."""
        radiation = 1000.0
        result_1 = SolarRadiationCorrections.apply_cloud_correction(
            radiation, cloud_cover=1.0, kcl1=1.0, kcl2=2.0
        )
        result_2 = SolarRadiationCorrections.apply_cloud_correction(
            radiation, cloud_cover=1.5, kcl1=1.0, kcl2=2.0
        )
        # Should behave the same
        assert result_1 == result_2

    def test_zero_radiation_stays_zero(self):
        """Test that zero radiation stays zero regardless of cloud cover."""
        result = SolarRadiationCorrections.apply_cloud_correction(
            0.0, cloud_cover=0.5, kcl1=1.0, kcl2=2.0
        )
        assert result == 0.0


class TestShadeCorrection:
    """Tests for shade correction."""

    def test_no_shade_no_correction(self):
        """Test that no shade (effective_shade=0) applies no correction."""
        radiation = 1000.0
        result = SolarRadiationCorrections.apply_shade_correction(radiation, effective_shade=0.0)
        assert result == radiation

    def test_full_shade_zero_radiation(self):
        """Test that full shade (effective_shade=1) gives zero radiation."""
        radiation = 1000.0
        result = SolarRadiationCorrections.apply_shade_correction(radiation, effective_shade=1.0)
        assert result == 0.0

    def test_partial_shade_linear_reduction(self):
        """Test that shade correction is linear."""
        radiation = 1000.0

        result_25 = SolarRadiationCorrections.apply_shade_correction(
            radiation, effective_shade=0.25
        )
        result_50 = SolarRadiationCorrections.apply_shade_correction(radiation, effective_shade=0.5)
        result_75 = SolarRadiationCorrections.apply_shade_correction(
            radiation, effective_shade=0.75
        )

        # Should be linear: 75%, 50%, 25% of original
        assert abs(result_25 - 750.0) < 1e-10
        assert abs(result_50 - 500.0) < 1e-10
        assert abs(result_75 - 250.0) < 1e-10

    def test_negative_shade_clamped(self):
        """Test that negative shade is clamped to zero."""
        radiation = 1000.0
        result = SolarRadiationCorrections.apply_shade_correction(radiation, effective_shade=-0.5)
        # Should behave as if effective_shade=0
        assert result == radiation

    def test_excessive_shade_clamped(self):
        """Test that shade > 1 is clamped to 1."""
        radiation = 1000.0
        result = SolarRadiationCorrections.apply_shade_correction(radiation, effective_shade=1.5)
        # Should behave as if effective_shade=1
        assert result == 0.0

    def test_zero_radiation_stays_zero(self):
        """Test that zero radiation stays zero regardless of shade."""
        result = SolarRadiationCorrections.apply_shade_correction(0.0, effective_shade=0.5)
        assert result == 0.0


class TestAndersonAlbedo:
    """Tests for Anderson albedo calculation."""

    def test_high_sun_low_albedo(self):
        """Test that high sun (elevation >= 30°) gives low albedo."""
        albedo = SolarRadiationCorrections.calculate_anderson_albedo(
            cloud_cover=0.0, solar_elevation=60.0
        )
        assert albedo == pytest.approx(0.03, abs=0.01)

    def test_low_sun_high_albedo(self):
        """Test that low sun (elevation < 30°) gives higher albedo."""
        albedo_high = SolarRadiationCorrections.calculate_anderson_albedo(
            cloud_cover=0.0, solar_elevation=60.0
        )
        albedo_low = SolarRadiationCorrections.calculate_anderson_albedo(
            cloud_cover=0.0, solar_elevation=10.0
        )

        # Low sun should have higher albedo
        assert albedo_low > albedo_high

    def test_below_horizon_zero_albedo(self):
        """Test that sun below horizon gives zero albedo."""
        albedo = SolarRadiationCorrections.calculate_anderson_albedo(
            cloud_cover=0.0, solar_elevation=-10.0
        )
        assert albedo == 0.0

    def test_clouds_affect_albedo(self):
        """Test that cloud cover affects albedo calculation."""
        albedo_clear = SolarRadiationCorrections.calculate_anderson_albedo(
            cloud_cover=0.0, solar_elevation=10.0
        )
        albedo_overcast = SolarRadiationCorrections.calculate_anderson_albedo(
            cloud_cover=1.0, solar_elevation=10.0
        )

        # Albedo should be different with clouds
        assert albedo_clear != albedo_overcast

    def test_albedo_in_valid_range(self):
        """Test that albedo is always in valid range [0, 1]."""
        # Test various combinations
        for elevation in [0, 10, 30, 60, 90]:
            for cloud_cover in [0.0, 0.5, 1.0]:
                albedo = SolarRadiationCorrections.calculate_anderson_albedo(cloud_cover, elevation)
                assert (
                    0.0 <= albedo <= 1.0
                ), f"Albedo {albedo} out of range for elevation={elevation}, cloud={cloud_cover}"

    def test_negative_cloud_cover_clamped(self):
        """Test that negative cloud cover is clamped to zero."""
        albedo = SolarRadiationCorrections.calculate_anderson_albedo(
            cloud_cover=-0.5, solar_elevation=45.0
        )
        # Should behave as if cloud_cover=0
        albedo_zero = SolarRadiationCorrections.calculate_anderson_albedo(
            cloud_cover=0.0, solar_elevation=45.0
        )
        assert albedo == albedo_zero

    def test_excessive_cloud_cover_clamped(self):
        """Test that cloud cover > 1 is clamped to 1."""
        albedo = SolarRadiationCorrections.calculate_anderson_albedo(
            cloud_cover=1.5, solar_elevation=45.0
        )
        # Should behave as if cloud_cover=1
        albedo_one = SolarRadiationCorrections.calculate_anderson_albedo(
            cloud_cover=1.0, solar_elevation=45.0
        )
        assert albedo == albedo_one


class TestAlbedoCorrection:
    """Tests for albedo correction."""

    def test_zero_albedo_no_correction(self):
        """Test that zero albedo (no reflection) applies no correction."""
        radiation = 1000.0
        result = SolarRadiationCorrections.apply_albedo_correction(radiation, albedo=0.0)
        assert result == radiation

    def test_full_albedo_zero_absorption(self):
        """Test that full albedo (albedo=1) gives zero absorbed radiation."""
        radiation = 1000.0
        result = SolarRadiationCorrections.apply_albedo_correction(radiation, albedo=1.0)
        assert result == 0.0

    def test_partial_albedo_linear_reduction(self):
        """Test that albedo correction is linear."""
        radiation = 1000.0

        result_10 = SolarRadiationCorrections.apply_albedo_correction(radiation, albedo=0.1)
        result_50 = SolarRadiationCorrections.apply_albedo_correction(radiation, albedo=0.5)

        # Should be linear: 90% and 50% of original
        assert abs(result_10 - 900.0) < 1e-10
        assert abs(result_50 - 500.0) < 1e-10

    def test_negative_albedo_clamped(self):
        """Test that negative albedo is clamped to zero."""
        radiation = 1000.0
        result = SolarRadiationCorrections.apply_albedo_correction(radiation, albedo=-0.5)
        # Should behave as if albedo=0
        assert result == radiation

    def test_excessive_albedo_clamped(self):
        """Test that albedo > 1 is clamped to 1."""
        radiation = 1000.0
        result = SolarRadiationCorrections.apply_albedo_correction(radiation, albedo=1.5)
        # Should behave as if albedo=1
        assert result == 0.0

    def test_zero_radiation_stays_zero(self):
        """Test that zero radiation stays zero regardless of albedo."""
        result = SolarRadiationCorrections.apply_albedo_correction(0.0, albedo=0.5)
        assert result == 0.0


class TestAllCorrections:
    """Tests for applying all corrections together."""

    def test_all_corrections_sequence(self):
        """Test that all corrections are applied in proper sequence."""
        radiation = 1000.0
        result = SolarRadiationCorrections.apply_all_corrections(
            solar_radiation=radiation,
            cloud_cover=0.5,
            effective_shade=0.5,
            solar_elevation=45.0,
            kcl1=1.0,
            kcl2=2.0,
            use_anderson_albedo=True,
        )

        # Check that all keys are present
        assert "original" in result
        assert "after_cloud" in result
        assert "after_shade" in result
        assert "albedo" in result
        assert "final" in result

        # Check that original is preserved
        assert result["original"] == radiation

        # Check that corrections reduce radiation progressively
        assert result["after_cloud"] <= result["original"]
        assert result["after_shade"] <= result["after_cloud"]
        assert result["final"] <= result["after_shade"]

        # All values should be non-negative
        assert result["after_cloud"] >= 0.0
        assert result["after_shade"] >= 0.0
        assert result["final"] >= 0.0

        # Albedo should be in valid range
        assert 0.0 <= result["albedo"] <= 1.0

    def test_without_anderson_albedo(self):
        """Test that albedo correction can be disabled."""
        radiation = 1000.0
        result = SolarRadiationCorrections.apply_all_corrections(
            solar_radiation=radiation,
            cloud_cover=0.5,
            effective_shade=0.5,
            solar_elevation=45.0,
            kcl1=1.0,
            kcl2=2.0,
            use_anderson_albedo=False,
        )

        # Albedo should be zero
        assert result["albedo"] == 0.0

        # Final should equal after_shade (no albedo correction)
        assert result["final"] == result["after_shade"]

    def test_no_corrections_preserves_radiation(self):
        """Test that with no corrections, radiation is preserved."""
        radiation = 1000.0
        result = SolarRadiationCorrections.apply_all_corrections(
            solar_radiation=radiation,
            cloud_cover=0.0,
            effective_shade=0.0,
            solar_elevation=60.0,  # High sun = low albedo
            kcl1=1.0,
            kcl2=2.0,
            use_anderson_albedo=True,
        )

        # After cloud should equal original (no clouds)
        assert result["after_cloud"] == result["original"]

        # After shade should equal after_cloud (no shade)
        assert result["after_shade"] == result["after_cloud"]

        # Final should be slightly less due to albedo (even at high sun)
        assert result["final"] < result["after_shade"]

    def test_maximum_corrections_reduces_significantly(self):
        """Test that maximum corrections reduce radiation significantly."""
        radiation = 1000.0
        result = SolarRadiationCorrections.apply_all_corrections(
            solar_radiation=radiation,
            cloud_cover=1.0,
            effective_shade=0.5,
            solar_elevation=10.0,  # Low sun = high albedo
            kcl1=1.0,
            kcl2=2.0,
            use_anderson_albedo=True,
        )

        # Final should be much less than original
        assert result["final"] < 0.5 * radiation
