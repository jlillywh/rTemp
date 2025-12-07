"""
Longwave atmospheric emissivity calculation models.

This module implements various empirical models for calculating atmospheric
emissivity, which is used to estimate longwave radiation from the atmosphere.
Different models are appropriate for different atmospheric conditions and
data availability.

References:
    - Brunt, D. (1932). Notes on radiation in the atmosphere.
    - Brutsaert, W. (1982). Evaporation into the Atmosphere.
    - Satterlund, D.R. (1979). An improved equation for estimating long-wave radiation.
    - Idso, S.B., and R.D. Jackson (1969). Thermal radiation from the atmosphere.
    - Swinbank, W.C. (1963). Long-wave radiation from clear skies.
    - Koberg, G.E. (1964). Methods to compute long-wave radiation from the atmosphere.
"""

from abc import ABC, abstractmethod
import math
from typing import Optional

from ..constants import CELSIUS_TO_KELVIN


class LongwaveEmissivity(ABC):
    """
    Abstract base class for longwave atmospheric emissivity calculations.

    Emissivity represents the effectiveness of the atmosphere in emitting
    longwave radiation. Values range from 0 (no emission) to 1 (perfect
    black body emission).
    """

    @abstractmethod
    def calculate(
        self, air_temp_c: float, vapor_pressure_mmhg: float, **kwargs: float
    ) -> float:
        """
        Calculate atmospheric emissivity.

        Args:
            air_temp_c: Air temperature in degrees Celsius
            vapor_pressure_mmhg: Vapor pressure in mmHg
            **kwargs: Additional parameters specific to each model

        Returns:
            Atmospheric emissivity (0-1)
        """
        pass


class EmissivityBrunt(LongwaveEmissivity):
    """
    Brunt (1932) emissivity model.

    One of the earliest empirical models relating atmospheric emissivity
    to vapor pressure. Simple and widely used.

    Formula: ε = 0.52 + 0.065 * sqrt(ea)
    where ea is vapor pressure in mmHg

    Reference:
        Brunt, D. (1932). Notes on radiation in the atmosphere.
        Quarterly Journal of the Royal Meteorological Society, 58, 389-420.
    """

    def calculate(
        self, air_temp_c: float, vapor_pressure_mmhg: float, **kwargs: float
    ) -> float:
        """
        Calculate emissivity using Brunt formula.

        Args:
            air_temp_c: Air temperature in degrees Celsius (not used in this model)
            vapor_pressure_mmhg: Vapor pressure in mmHg
            **kwargs: Not used

        Returns:
            Atmospheric emissivity (0-1)
        """
        emissivity: float = 0.52 + 0.065 * math.sqrt(vapor_pressure_mmhg)
        # Clamp to physically valid range [0, 1]
        return max(0.0, min(1.0, emissivity))


class EmissivityBrutsaert(LongwaveEmissivity):
    """
    Brutsaert (1982) emissivity model.

    Physically-based model with configurable coefficient. The default
    coefficient of 1.24 is for general use, but can be calibrated for
    specific locations.

    Formula: ε = coefficient * (ea/Ta)^(1/7)
    where ea is vapor pressure in mmHg converted to mb, Ta is air temp in K

    Reference:
        Brutsaert, W. (1982). Evaporation into the Atmosphere.
        D. Reidel Publishing Company.
    """

    def __init__(self, coefficient: float = 1.24):
        """
        Initialize Brutsaert model.

        Args:
            coefficient: Brutsaert coefficient (default 1.24)
        """
        self.coefficient = coefficient

    def calculate(
        self, air_temp_c: float, vapor_pressure_mmhg: float, **kwargs: float
    ) -> float:
        """
        Calculate emissivity using Brutsaert formula.

        Args:
            air_temp_c: Air temperature in degrees Celsius
            vapor_pressure_mmhg: Vapor pressure in mmHg
            **kwargs: Not used

        Returns:
            Atmospheric emissivity (0-1)
        """
        air_temp_k = air_temp_c + CELSIUS_TO_KELVIN
        # Convert mmHg to mb (1 mmHg = 1.33322 mb)
        vapor_pressure_mb = vapor_pressure_mmhg * 1.33322

        emissivity: float = self.coefficient * (vapor_pressure_mb / air_temp_k) ** (1.0 / 7.0)
        # Clamp to physically valid range [0, 1]
        return max(0.0, min(1.0, emissivity))


class EmissivitySatterlund(LongwaveEmissivity):
    """
    Satterlund (1979) emissivity model.

    Improved model that uses an exponential relationship with dewpoint
    temperature. Particularly accurate for clear sky conditions.

    Formula: ε = 1.08 * (1 - exp(-ea^(Ta/2016)))
    where ea is vapor pressure in mmHg converted to mb, Ta is air temp in K

    Reference:
        Satterlund, D.R. (1979). An improved equation for estimating
        long-wave radiation from the atmosphere. Water Resources Research,
        15(6), 1649-1650.
    """

    def calculate(
        self, air_temp_c: float, vapor_pressure_mmhg: float, **kwargs: float
    ) -> float:
        """
        Calculate emissivity using Satterlund formula.

        Args:
            air_temp_c: Air temperature in degrees Celsius
            vapor_pressure_mmhg: Vapor pressure in mmHg
            **kwargs: Not used

        Returns:
            Atmospheric emissivity (0-1)
        """
        air_temp_k = air_temp_c + CELSIUS_TO_KELVIN
        # Convert mmHg to mb (1 mmHg = 1.33322 mb)
        vapor_pressure_mb = vapor_pressure_mmhg * 1.33322

        exponent = vapor_pressure_mb ** (air_temp_k / 2016.0)
        emissivity: float = 1.08 * (1.0 - math.exp(-exponent))
        # Clamp to physically valid range [0, 1]
        return max(0.0, min(1.0, emissivity))


class EmissivityIdsoJackson(LongwaveEmissivity):
    """
    Idso-Jackson (1969) emissivity model.

    Simple model that depends only on air temperature, useful when
    humidity data is unavailable or unreliable.

    Formula: ε = 1 - 0.261 * exp(-0.000777 * Ta^2)
    where Ta is air temperature in Celsius

    Reference:
        Idso, S.B., and R.D. Jackson (1969). Thermal radiation from
        the atmosphere. Journal of Geophysical Research, 74(23), 5397-5403.
    """

    def calculate(
        self, air_temp_c: float, vapor_pressure_mmhg: float, **kwargs: float
    ) -> float:
        """
        Calculate emissivity using Idso-Jackson formula.

        Args:
            air_temp_c: Air temperature in degrees Celsius
            vapor_pressure_mmhg: Vapor pressure in mmHg (not used in this model)
            **kwargs: Not used

        Returns:
            Atmospheric emissivity (0-1)
        """
        emissivity: float = 1.0 - 0.261 * math.exp(-0.000777 * air_temp_c**2)
        # Clamp to physically valid range [0, 1]
        return max(0.0, min(1.0, emissivity))


class EmissivitySwinbank(LongwaveEmissivity):
    """
    Swinbank (1963) emissivity model.

    Another temperature-only model, useful for clear sky conditions
    when humidity data is not available.

    Formula: ε = 0.92e-5 * Ta^2
    where Ta is air temperature in Kelvin

    Reference:
        Swinbank, W.C. (1963). Long-wave radiation from clear skies.
        Quarterly Journal of the Royal Meteorological Society, 89, 339-348.
    """

    def calculate(
        self, air_temp_c: float, vapor_pressure_mmhg: float, **kwargs: float
    ) -> float:
        """
        Calculate emissivity using Swinbank formula.

        Args:
            air_temp_c: Air temperature in degrees Celsius
            vapor_pressure_mmhg: Vapor pressure in mmHg (not used in this model)
            **kwargs: Not used

        Returns:
            Atmospheric emissivity (0-1)
        """
        air_temp_k = air_temp_c + CELSIUS_TO_KELVIN
        emissivity: float = 0.92e-5 * air_temp_k**2
        # Clamp to physically valid range [0, 1]
        return max(0.0, min(1.0, emissivity))


class EmissivityKoberg(LongwaveEmissivity):
    """
    Koberg (1964) emissivity model.

    Uses interpolation from Koberg's Figure 34, which relates the Brunt
    coefficient to air temperature and atmospheric clearness. This model
    adapts the Brunt formula based on atmospheric conditions.

    The Brunt coefficient varies from approximately 0.04 to 0.08 depending
    on air temperature and clearness (inverse of cloud cover).

    Reference:
        Koberg, G.E. (1964). Methods to compute long-wave radiation from
        the atmosphere and reflected solar radiation from a water surface.
        U.S. Geological Survey Professional Paper 272-F.
    """

    def calculate(
        self,
        air_temp_c: float,
        vapor_pressure_mmhg: float,
        clearness: Optional[float] = None,
        **kwargs: float,
    ) -> float:
        """
        Calculate emissivity using Koberg method with Figure 34 interpolation.

        Args:
            air_temp_c: Air temperature in degrees Celsius
            vapor_pressure_mmhg: Vapor pressure in mmHg
            clearness: Atmospheric clearness (1 - cloud_cover), 0-1.
                      If None, assumes clear sky (clearness = 1.0)
            **kwargs: Not used

        Returns:
            Atmospheric emissivity (0-1)
        """
        if clearness is None:
            clearness = 1.0

        # Interpolate Brunt coefficient from Koberg Figure 34
        # Based on air temperature and clearness
        # These values are approximated from the figure

        # Temperature effect: coefficient increases with temperature
        # Range: approximately 0.04 to 0.08
        if air_temp_c <= 0:
            temp_factor = 0.04
        elif air_temp_c >= 30:
            temp_factor = 0.08
        else:
            # Linear interpolation between 0 and 30°C
            temp_factor = 0.04 + (0.08 - 0.04) * (air_temp_c / 30.0)

        # Clearness effect: coefficient increases with clearness
        # At low clearness (high clouds), use lower coefficient
        # At high clearness (clear sky), use higher coefficient
        clearness_factor = 0.5 + 0.5 * clearness

        brunt_coefficient = temp_factor * clearness_factor

        # Apply modified Brunt formula
        emissivity = 0.52 + brunt_coefficient * math.sqrt(vapor_pressure_mmhg)
        # Clamp to physically valid range [0, 1]
        return max(0.0, min(1.0, emissivity))
