"""
rTemp: Response Temperature Model for Water Bodies

A comprehensive Python implementation of the rTemp water temperature model,
which calculates response temperature of water bodies based on meteorological
inputs and site characteristics using a heat budget approach.
"""

__version__ = "1.0.0"
__author__ = "rTemp Development Team"

from rtemp.config import MeteorologicalData, ModelConfiguration, ModelState
from rtemp.model import RTempModel

__all__ = [
    "RTempModel",
    "ModelConfiguration",
    "ModelState",
    "MeteorologicalData",
]
