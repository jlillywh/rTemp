"""
Test to verify the project infrastructure is set up correctly.
"""

import pytest


def test_import_rtemp():
    """Test that the rtemp package can be imported."""
    import rtemp

    assert rtemp.__version__ == "1.0.0"


def test_import_main_classes():
    """Test that main classes can be imported."""
    from rtemp import ModelConfiguration, ModelState, RTempModel

    assert ModelConfiguration is not None
    assert ModelState is not None
    assert RTempModel is not None


def test_import_constants():
    """Test that constants module can be imported."""
    from rtemp import constants

    assert constants.PI is not None
    assert constants.STEFAN_BOLTZMANN > 0
    assert constants.WATER_DENSITY > 0


def test_import_solar_position():
    """Test that solar position module can be imported."""
    from rtemp.solar import NOAASolarPosition

    assert NOAASolarPosition is not None


def test_hypothesis_available():
    """Test that hypothesis is available for property-based testing."""
    import hypothesis

    assert hypothesis is not None


def test_numpy_available():
    """Test that numpy is available."""
    import numpy as np

    assert np is not None


def test_pandas_available():
    """Test that pandas is available."""
    import pandas as pd

    assert pd is not None
