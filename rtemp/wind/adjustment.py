"""
Wind speed height adjustment calculations.

This module implements wind speed adjustments for height using the TVA
exponential wind correction method and shelter factor application.
"""

from typing import Optional


class WindAdjustment:
    """
    Wind speed height adjustment using TVA exponential correction.

    This class provides methods to adjust wind speed measurements from one
    height to another using the Tennessee Valley Authority (TVA) exponential
    wind profile correction with an exponent of 0.15.
    """

    # TVA exponential wind correction exponent
    TVA_EXPONENT = 0.15

    @staticmethod
    def adjust_for_height(wind_speed: float, measured_height: float, target_height: float) -> float:
        """
        Adjust wind speed from measured height to target height.

        Uses the TVA exponential wind correction formula:
        wind_target = wind_measured * (target_height / measured_height)^0.15

        This method implements Requirement 5.6: WHEN the system adjusts wind
        speed for height THEN the system SHALL apply TVA exponential wind
        correction with exponent 0.15.

        Parameters
        ----------
        wind_speed : float
            Wind speed at measured height (m/s)
        measured_height : float
            Height at which wind speed was measured (m)
        target_height : float
            Height to which wind speed should be adjusted (m)

        Returns
        -------
        float
            Adjusted wind speed at target height (m/s)

        Examples
        --------
        >>> WindAdjustment.adjust_for_height(5.0, 10.0, 2.0)
        4.5534...

        >>> WindAdjustment.adjust_for_height(3.0, 2.0, 7.0)
        3.3766...
        """
        if measured_height <= 0:
            raise ValueError("Measured height must be greater than zero")
        if target_height <= 0:
            raise ValueError("Target height must be greater than zero")

        # TVA exponential wind correction
        height_ratio: float = target_height / measured_height
        adjusted_wind: float = wind_speed * (height_ratio**WindAdjustment.TVA_EXPONENT)

        return adjusted_wind

    @staticmethod
    def apply_shelter_factor(wind_speed: float, effective_wind_factor: float) -> float:
        """
        Apply shelter factor to wind speed.

        This method implements Requirement 5.7: WHEN the system adjusts wind
        speed for shelter THEN the system SHALL multiply by effective wind factor.

        The effective wind factor accounts for sheltering effects from vegetation,
        topography, or structures that reduce effective wind speed at the water
        surface. A factor of 1.0 indicates no sheltering, while lower values
        indicate increased sheltering.

        Parameters
        ----------
        wind_speed : float
            Wind speed before shelter adjustment (m/s)
        effective_wind_factor : float
            Effective wind factor (0-1), where 1.0 = no shelter, 0.0 = complete shelter

        Returns
        -------
        float
            Wind speed after shelter adjustment (m/s)

        Examples
        --------
        >>> WindAdjustment.apply_shelter_factor(5.0, 1.0)
        5.0

        >>> WindAdjustment.apply_shelter_factor(5.0, 0.8)
        4.0

        >>> WindAdjustment.apply_shelter_factor(5.0, 0.5)
        2.5
        """
        if effective_wind_factor < 0:
            raise ValueError("Effective wind factor must be non-negative")

        return wind_speed * effective_wind_factor

    @staticmethod
    def adjust_with_shelter(
        wind_speed: float,
        measured_height: float,
        target_height: float,
        effective_wind_factor: float,
    ) -> float:
        """
        Adjust wind speed for both height and shelter effects.

        This is a convenience method that combines height adjustment and
        shelter factor application in a single call.

        Parameters
        ----------
        wind_speed : float
            Wind speed at measured height (m/s)
        measured_height : float
            Height at which wind speed was measured (m)
        target_height : float
            Height to which wind speed should be adjusted (m)
        effective_wind_factor : float
            Effective wind factor (0-1) for shelter effects

        Returns
        -------
        float
            Wind speed adjusted for both height and shelter (m/s)

        Examples
        --------
        >>> WindAdjustment.adjust_with_shelter(5.0, 10.0, 2.0, 0.8)
        3.6427...
        """
        # First adjust for height
        height_adjusted = WindAdjustment.adjust_for_height(
            wind_speed, measured_height, target_height
        )

        # Then apply shelter factor
        final_wind = WindAdjustment.apply_shelter_factor(height_adjusted, effective_wind_factor)

        return final_wind
