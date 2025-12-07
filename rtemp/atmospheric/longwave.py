"""
Longwave radiation calculation module.

This module implements calculations for longwave atmospheric radiation
and longwave back radiation from the water surface. It uses emissivity
models to calculate atmospheric radiation and applies Stefan-Boltzmann
law for thermal radiation calculations.

References:
    - Stefan-Boltzmann law: L = ε * σ * T^4
    - Cloud correction methods from various sources
"""

from typing import Literal

from ..constants import (
    ATMOSPHERIC_REFLECTION,
    CELSIUS_TO_KELVIN,
    STEFAN_BOLTZMANN,
    WATER_EMISSIVITY,
)


class LongwaveRadiation:
    """
    Calculate longwave radiation components for heat budget.

    This class provides static methods for calculating:
    1. Atmospheric longwave radiation (downward)
    2. Water surface back radiation (upward)

    All calculations use the Stefan-Boltzmann law and account for
    atmospheric emissivity, cloud cover, and surface properties.
    """

    @staticmethod
    def calculate_atmospheric(
        emissivity: float,
        air_temp_c: float,
        cloud_cover: float,
        cloud_method: Literal["Eqn 1", "Eqn 2"] = "Eqn 1",
        kcl3: float = 1.0,
        kcl4: float = 2.0,
    ) -> float:
        """
        Calculate longwave atmospheric radiation with cloud corrections.

        This method calculates the downward longwave radiation from the
        atmosphere using the Stefan-Boltzmann law with atmospheric emissivity.
        Cloud cover corrections are applied using one of two methods:

        - Equation 1: Multiplicative correction to clear-sky emissivity
          ε_cloudy = ε_clear * (1 + kcl3 * cloud_cover^kcl4)

        - Equation 2: Blending between clear-sky and overcast emissivity
          ε_cloudy = ε_clear * (1 - cloud_cover) + 1.0 * cloud_cover
          with additional kcl3 and kcl4 parameters

        The radiation is then reduced by 3% to account for surface reflection.

        Args:
            emissivity: Clear-sky atmospheric emissivity (0-1)
            air_temp_c: Air temperature in degrees Celsius
            cloud_cover: Cloud cover fraction (0-1, where 0=clear, 1=overcast)
            cloud_method: Cloud correction method, either "Eqn 1" or "Eqn 2"
            kcl3: Cloud correction parameter 3 (default 1.0)
            kcl4: Cloud correction parameter 4 (default 2.0)

        Returns:
            Longwave atmospheric radiation in W/m²

        Example:
            >>> LongwaveRadiation.calculate_atmospheric(0.8, 20.0, 0.0)
            315.2...
        """
        # Convert temperature to Kelvin
        air_temp_k = air_temp_c + CELSIUS_TO_KELVIN

        # Apply cloud correction to emissivity
        if cloud_method == "Eqn 1":
            # Equation 1: Multiplicative correction
            # ε_cloudy = ε_clear * (1 + kcl3 * cloud_cover^kcl4)
            cloud_factor = 1.0 + kcl3 * (cloud_cover**kcl4)
            emissivity_cloudy = emissivity * cloud_factor
        else:  # "Eqn 2"
            # Equation 2: Blending between clear and overcast
            # ε_cloudy = ε_clear * (1 - cloud_cover) + ε_overcast * cloud_cover
            # where ε_overcast is typically close to 1.0
            # Additional parameters kcl3 and kcl4 can modify this
            emissivity_overcast = 1.0
            # Apply kcl3 and kcl4 as modifiers
            cloud_factor = (1.0 - cloud_cover) + emissivity_overcast * cloud_cover
            cloud_factor = cloud_factor * (1.0 + (kcl3 - 1.0) * (cloud_cover**kcl4))
            emissivity_cloudy = emissivity * cloud_factor

        # Clamp emissivity to valid range [0, 1]
        emissivity_cloudy = max(0.0, min(1.0, emissivity_cloudy))

        # Calculate longwave radiation using Stefan-Boltzmann law
        # L = ε * σ * T^4
        longwave_radiation: float = emissivity_cloudy * STEFAN_BOLTZMANN * (air_temp_k**4)

        # Reduce by surface reflection factor (3%)
        longwave_radiation = longwave_radiation * (1.0 - ATMOSPHERIC_REFLECTION)

        return longwave_radiation

    @staticmethod
    def calculate_back_radiation(water_temp_c: float) -> float:
        """
        Calculate longwave back radiation from water surface.

        This method calculates the upward longwave radiation emitted by
        the water surface using the Stefan-Boltzmann law. Water is treated
        as a near-perfect black body with emissivity of 0.97.

        The back radiation represents heat loss from the water body and
        is always negative in the heat budget (energy leaving the system).

        Args:
            water_temp_c: Water surface temperature in degrees Celsius

        Returns:
            Longwave back radiation in W/m² (positive value, but represents
            heat loss when used in heat budget calculations)

        Example:
            >>> LongwaveRadiation.calculate_back_radiation(20.0)
            418.6...
        """
        # Convert temperature to Kelvin
        water_temp_k = water_temp_c + CELSIUS_TO_KELVIN

        # Calculate longwave back radiation using Stefan-Boltzmann law
        # L = ε * σ * T^4
        back_radiation = WATER_EMISSIVITY * STEFAN_BOLTZMANN * (water_temp_k**4)

        return back_radiation
