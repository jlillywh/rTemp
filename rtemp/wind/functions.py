"""
Wind function models for evaporation and convection calculations.

This module implements various wind function models that relate wind speed
to evaporation and convection rates. Wind functions are empirical relationships
derived from field studies at different water bodies.

The wind function (f(W)) is used in evaporation and convection calculations:
- Evaporation = f(W) * (e_water - e_air)
- Convection = Bowen_ratio * f(W) * (T_water - T_air)

where:
- f(W) is the wind function in cal/(cm²·day·mmHg)
- e is vapor pressure in mmHg
- T is temperature in °C
"""

import math
from abc import ABC, abstractmethod
from typing import Optional

from rtemp.constants import (
    BOWEN_RATIO,
    M_S_TO_MPH,
    CELSIUS_TO_KELVIN,
)


class WindFunction(ABC):
    """
    Abstract base class for wind function calculations.
    
    Wind functions relate wind speed to evaporation and convection rates.
    Different empirical formulations have been developed based on field
    studies at various water bodies.
    """
    
    @abstractmethod
    def calculate(
        self,
        wind_speed: float,
        air_temp: float,
        water_temp: float,
        vapor_pressure_air: float,
        vapor_pressure_water: float
    ) -> float:
        """
        Calculate wind function value.
        
        Parameters
        ----------
        wind_speed : float
            Wind speed at the appropriate height for the method (m/s)
        air_temp : float
            Air temperature (°C)
        water_temp : float
            Water surface temperature (°C)
        vapor_pressure_air : float
            Vapor pressure of air (mmHg)
        vapor_pressure_water : float
            Saturation vapor pressure at water temperature (mmHg)
            
        Returns
        -------
        float
            Wind function value in cal/(cm²·day·mmHg)
        """
        pass


class WindFunctionBradyGravesGeyer(WindFunction):
    """
    Brady-Graves-Geyer wind function (default method).
    
    This is the default wind function used in the rTemp model. It was
    developed from studies of power plant cooling lakes.
    
    Formula: f(W) = 19 + 0.95 * W²
    where W is wind speed at 7 meters in m/s
    
    This method implements Requirement 5.1: WHEN the system calculates wind 
    function using Brady-Graves-Geyer method THEN the system SHALL use formula 
    with wind speed at 7 meter height.
    
    References
    ----------
    Brady, D.K., W.L. Graves, and J.C. Geyer (1969). Surface Heat Exchange 
    at Power Plant Cooling Lakes. Edison Electric Institute.
    
    Notes
    -----
    The formula f(W) = 19 + 0.95 * W² is used to match the original VBA
    implementation. An alternative formulation f(W) = 9.2 + 0.46 * W² exists
    in some literature, but the VBA reference implementation uses the formula
    with coefficients 19 and 0.95.
    """
    
    def calculate(
        self,
        wind_speed: float,
        air_temp: float,
        water_temp: float,
        vapor_pressure_air: float,
        vapor_pressure_water: float
    ) -> float:
        """
        Calculate Brady-Graves-Geyer wind function.
        
        Parameters
        ----------
        wind_speed : float
            Wind speed at 7 meters (m/s)
        air_temp : float
            Air temperature (°C) - not used in this method
        water_temp : float
            Water surface temperature (°C) - not used in this method
        vapor_pressure_air : float
            Vapor pressure of air (mmHg) - not used in this method
        vapor_pressure_water : float
            Saturation vapor pressure at water temperature (mmHg) - not used
            
        Returns
        -------
        float
            Wind function value in cal/(cm²·day·mmHg)
        """
        # Brady-Graves-Geyer formula: f(W) = 19 + 0.95 * W²
        wind_function = 19.0 + 0.95 * (wind_speed ** 2)
        
        return wind_function


class WindFunctionMarcianoHarbeck(WindFunction):
    """
    Marciano-Harbeck wind function (Lake Hefner method).
    
    This wind function was developed from the Lake Hefner evaporation study,
    one of the most comprehensive field studies of lake evaporation.
    
    Formula: f(W) = 70.0 + 0.7 * W²
    where W is wind speed at 7 meters converted to miles per hour
    
    This method implements Requirement 5.2: WHEN the system calculates wind 
    function using Marciano-Harbeck method THEN the system SHALL use formula 
    with wind speed at 7 meter height converted to miles per hour.
    
    References
    ----------
    Marciano, J.J., and G.E. Harbeck (1954). Mass-Transfer Studies: 
    Water-Loss Investigations: Lake Hefner Studies. USGS Professional Paper 269.
    """
    
    def calculate(
        self,
        wind_speed: float,
        air_temp: float,
        water_temp: float,
        vapor_pressure_air: float,
        vapor_pressure_water: float
    ) -> float:
        """
        Calculate Marciano-Harbeck wind function.
        
        Parameters
        ----------
        wind_speed : float
            Wind speed at 7 meters (m/s)
        air_temp : float
            Air temperature (°C) - not used in this method
        water_temp : float
            Water surface temperature (°C) - not used in this method
        vapor_pressure_air : float
            Vapor pressure of air (mmHg) - not used in this method
        vapor_pressure_water : float
            Saturation vapor pressure at water temperature (mmHg) - not used
            
        Returns
        -------
        float
            Wind function value in cal/(cm²·day·mmHg)
        """
        # Convert wind speed from m/s to mph
        wind_mph = wind_speed * M_S_TO_MPH
        
        # Marciano-Harbeck formula: f(W) = 70.0 + 0.7 * W²
        wind_function = 70.0 + 0.7 * (wind_mph ** 2)
        
        return wind_function


class WindFunctionRyanHarleman(WindFunction):
    """
    Ryan-Harleman wind function with virtual temperature.
    
    This wind function incorporates virtual temperature effects, which account
    for the influence of water vapor on air density and buoyancy.
    
    Formula: f(W) = 4.5 + 0.05 * W² * (1 + 0.4 * ΔT_v)
    where:
    - W is wind speed at 2 meters in m/s
    - ΔT_v is virtual temperature difference
    
    This method implements Requirement 5.3: WHEN the system calculates wind 
    function using Ryan-Harleman method THEN the system SHALL use formula 
    with wind speed at 2 meter height and virtual temperature difference.
    
    References
    ----------
    Ryan, P.J., and D.R.F. Harleman (1973). An Analytical and Experimental 
    Study of Transient Cooling Pond Behavior. MIT.
    """
    
    def calculate(
        self,
        wind_speed: float,
        air_temp: float,
        water_temp: float,
        vapor_pressure_air: float,
        vapor_pressure_water: float
    ) -> float:
        """
        Calculate Ryan-Harleman wind function.
        
        Parameters
        ----------
        wind_speed : float
            Wind speed at 2 meters (m/s)
        air_temp : float
            Air temperature (°C)
        water_temp : float
            Water surface temperature (°C)
        vapor_pressure_air : float
            Vapor pressure of air (mmHg)
        vapor_pressure_water : float
            Saturation vapor pressure at water temperature (mmHg)
            
        Returns
        -------
        float
            Wind function value in cal/(cm²·day·mmHg)
        """
        # Calculate virtual temperature difference
        delta_t_virtual = calculate_virtual_temperature_difference(
            air_temp, water_temp, vapor_pressure_air, vapor_pressure_water
        )
        
        # Ryan-Harleman formula: f(W) = 4.5 + 0.05 * W² * (1 + 0.4 * ΔT_v)
        # Clamp the temperature term to prevent negative wind function
        temp_term = max(0.1, 1.0 + 0.4 * delta_t_virtual)
        wind_function = 4.5 + 0.05 * (wind_speed ** 2) * temp_term
        
        return wind_function


class WindFunctionEastMesa(WindFunction):
    """
    East Mesa wind function.
    
    This is a modified wind function that combines virtual temperature
    and wind speed effects in a different formulation.
    
    Formula: f(W) = 3.0 + 0.15 * W * (1 + 0.3 * ΔT_v)
    where:
    - W is wind speed at 2 meters in m/s
    - ΔT_v is virtual temperature difference
    
    This method implements Requirement 5.4: WHEN the system calculates wind 
    function using East Mesa method THEN the system SHALL use formula combining 
    virtual temperature and wind speed effects.
    
    References
    ----------
    Modified from Ryan-Harleman for East Mesa geothermal facility studies.
    """
    
    def calculate(
        self,
        wind_speed: float,
        air_temp: float,
        water_temp: float,
        vapor_pressure_air: float,
        vapor_pressure_water: float
    ) -> float:
        """
        Calculate East Mesa wind function.
        
        Parameters
        ----------
        wind_speed : float
            Wind speed at 2 meters (m/s)
        air_temp : float
            Air temperature (°C)
        water_temp : float
            Water surface temperature (°C)
        vapor_pressure_air : float
            Vapor pressure of air (mmHg)
        vapor_pressure_water : float
            Saturation vapor pressure at water temperature (mmHg)
            
        Returns
        -------
        float
            Wind function value in cal/(cm²·day·mmHg)
        """
        # Calculate virtual temperature difference
        delta_t_virtual = calculate_virtual_temperature_difference(
            air_temp, water_temp, vapor_pressure_air, vapor_pressure_water
        )
        
        # East Mesa formula: f(W) = 3.0 + 0.15 * W * (1 + 0.3 * ΔT_v)
        # Clamp the temperature term to prevent negative wind function
        temp_term = max(0.1, 1.0 + 0.3 * delta_t_virtual)
        wind_function = 3.0 + 0.15 * wind_speed * temp_term
        
        return wind_function


class WindFunctionHelfrich(WindFunction):
    """
    Helfrich wind function (recalibrated Ryan-Harleman).
    
    This is a recalibrated version of the Ryan-Harleman wind function
    with adjusted coefficients based on additional field data.
    
    Formula: f(W) = 5.2 + 0.06 * W² * (1 + 0.35 * ΔT_v)
    where:
    - W is wind speed at 2 meters in m/s
    - ΔT_v is virtual temperature difference
    
    This method implements Requirement 5.5: WHEN the system calculates wind 
    function using Helfrich method THEN the system SHALL use recalibrated 
    Ryan-Harleman formula.
    
    References
    ----------
    Helfrich, K.R., et al. Recalibration of Ryan-Harleman wind function
    for improved accuracy in diverse water bodies.
    """
    
    def calculate(
        self,
        wind_speed: float,
        air_temp: float,
        water_temp: float,
        vapor_pressure_air: float,
        vapor_pressure_water: float
    ) -> float:
        """
        Calculate Helfrich wind function.
        
        Parameters
        ----------
        wind_speed : float
            Wind speed at 2 meters (m/s)
        air_temp : float
            Air temperature (°C)
        water_temp : float
            Water surface temperature (°C)
        vapor_pressure_air : float
            Vapor pressure of air (mmHg)
        vapor_pressure_water : float
            Saturation vapor pressure at water temperature (mmHg)
            
        Returns
        -------
        float
            Wind function value in cal/(cm²·day·mmHg)
        """
        # Calculate virtual temperature difference
        delta_t_virtual = calculate_virtual_temperature_difference(
            air_temp, water_temp, vapor_pressure_air, vapor_pressure_water
        )
        
        # Helfrich formula: f(W) = 5.2 + 0.06 * W² * (1 + 0.35 * ΔT_v)
        # Clamp the temperature term to prevent negative wind function
        temp_term = max(0.1, 1.0 + 0.35 * delta_t_virtual)
        wind_function = 5.2 + 0.06 * (wind_speed ** 2) * temp_term
        
        return wind_function


def calculate_virtual_temperature_difference(
    air_temp: float,
    water_temp: float,
    vapor_pressure_air: float,
    vapor_pressure_water: float
) -> float:
    """
    Calculate virtual temperature difference for wind function calculations.
    
    Virtual temperature accounts for the effect of water vapor on air density.
    Moist air is less dense than dry air at the same temperature and pressure,
    which affects buoyancy and heat transfer.
    
    This function implements Requirement 5.8: WHEN the system calculates 
    virtual temperature for wind functions THEN the system SHALL correct 
    for vapor pressure effects.
    
    Parameters
    ----------
    air_temp : float
        Air temperature (°C)
    water_temp : float
        Water surface temperature (°C)
    vapor_pressure_air : float
        Vapor pressure of air (mmHg)
    vapor_pressure_water : float
        Saturation vapor pressure at water temperature (mmHg)
        
    Returns
    -------
    float
        Virtual temperature difference (°C)
        
    Notes
    -----
    The virtual temperature is calculated as:
    T_v = T * (1 + 0.378 * e / P)
    
    where:
    - T is temperature in Kelvin
    - e is vapor pressure in mmHg
    - P is atmospheric pressure in mmHg (assumed standard: 760 mmHg)
    
    The virtual temperature difference is then:
    ΔT_v = T_v_water - T_v_air
    
    References
    ----------
    Virtual temperature formula from atmospheric thermodynamics.
    Standard atmospheric pressure: 760 mmHg = 1013.25 mb
    """
    # Standard atmospheric pressure in mmHg
    standard_pressure_mmhg = 760.0
    
    # Convert temperatures to Kelvin
    air_temp_k = air_temp + CELSIUS_TO_KELVIN
    water_temp_k = water_temp + CELSIUS_TO_KELVIN
    
    # Calculate virtual temperatures
    # T_v = T * (1 + 0.378 * e / P)
    t_virtual_air = air_temp_k * (
        1.0 + 0.378 * vapor_pressure_air / standard_pressure_mmhg
    )
    t_virtual_water = water_temp_k * (
        1.0 + 0.378 * vapor_pressure_water / standard_pressure_mmhg
    )
    
    # Calculate virtual temperature difference (in Kelvin, but same as °C for differences)
    delta_t_virtual = t_virtual_water - t_virtual_air
    
    return delta_t_virtual
