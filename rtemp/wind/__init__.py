"""
Wind function and adjustment modules.

This package contains implementations of various wind function models
and wind speed height adjustment calculations.
"""

from rtemp.wind.adjustment import WindAdjustment
from rtemp.wind.functions import (
    WindFunction,
    WindFunctionBradyGravesGeyer,
    WindFunctionMarcianoHarbeck,
    WindFunctionRyanHarleman,
    WindFunctionEastMesa,
    WindFunctionHelfrich,
    calculate_virtual_temperature_difference,
)

__all__ = [
    "WindAdjustment",
    "WindFunction",
    "WindFunctionBradyGravesGeyer",
    "WindFunctionMarcianoHarbeck",
    "WindFunctionRyanHarleman",
    "WindFunctionEastMesa",
    "WindFunctionHelfrich",
    "calculate_virtual_temperature_difference",
]
