"""
Unit conversion utilities for the rTemp model.

This module provides static methods for converting between different units
used throughout the model calculations.
"""

from rtemp.constants import (
    CAL_CM2_DAY_TO_WATTS_M2,
    CELSIUS_TO_KELVIN,
    CM_TO_METERS,
    DEG_TO_RAD,
    M_S_TO_MPH,
    METERS_TO_CM,
    MPH_TO_M_S,
    RAD_TO_DEG,
    W_M_C_TO_CAL_S_CM_C,
    WATTS_M2_TO_CAL_CM2_DAY,
)


class UnitConversions:
    """
    Static methods for unit conversions used in rTemp calculations.
    
    All methods are static and can be called without instantiating the class.
    Conversions maintain numerical precision and handle edge cases appropriately.
    """

    @staticmethod
    def watts_m2_to_cal_cm2_day(watts_m2: float) -> float:
        """
        Convert heat flux from watts per square meter to calories per square centimeter per day.
        
        Args:
            watts_m2: Heat flux in W/m²
            
        Returns:
            Heat flux in cal/(cm²·day)
            
        Example:
            >>> UnitConversions.watts_m2_to_cal_cm2_day(100.0)
            206.56...
        """
        return watts_m2 * WATTS_M2_TO_CAL_CM2_DAY

    @staticmethod
    def cal_cm2_day_to_watts_m2(cal_cm2_day: float) -> float:
        """
        Convert heat flux from calories per square centimeter per day to watts per square meter.
        
        Args:
            cal_cm2_day: Heat flux in cal/(cm²·day)
            
        Returns:
            Heat flux in W/m²
            
        Example:
            >>> UnitConversions.cal_cm2_day_to_watts_m2(206.56)
            99.99...
        """
        return cal_cm2_day * CAL_CM2_DAY_TO_WATTS_M2

    @staticmethod
    def deg_to_rad(degrees: float) -> float:
        """
        Convert angle from degrees to radians.
        
        Args:
            degrees: Angle in degrees
            
        Returns:
            Angle in radians
            
        Example:
            >>> UnitConversions.deg_to_rad(180.0)
            3.141592...
        """
        return degrees * DEG_TO_RAD

    @staticmethod
    def rad_to_deg(radians: float) -> float:
        """
        Convert angle from radians to degrees.
        
        Args:
            radians: Angle in radians
            
        Returns:
            Angle in degrees
            
        Example:
            >>> UnitConversions.rad_to_deg(3.14159265359)
            180.0
        """
        return radians * RAD_TO_DEG

    @staticmethod
    def celsius_to_kelvin(celsius: float) -> float:
        """
        Convert temperature from Celsius to Kelvin.
        
        Args:
            celsius: Temperature in °C
            
        Returns:
            Temperature in K
            
        Example:
            >>> UnitConversions.celsius_to_kelvin(0.0)
            273.15
        """
        return celsius + CELSIUS_TO_KELVIN

    @staticmethod
    def kelvin_to_celsius(kelvin: float) -> float:
        """
        Convert temperature from Kelvin to Celsius.
        
        Args:
            kelvin: Temperature in K
            
        Returns:
            Temperature in °C
            
        Example:
            >>> UnitConversions.kelvin_to_celsius(273.15)
            0.0
        """
        return kelvin - CELSIUS_TO_KELVIN

    @staticmethod
    def meters_to_centimeters(meters: float) -> float:
        """
        Convert length from meters to centimeters.
        
        Args:
            meters: Length in meters
            
        Returns:
            Length in centimeters
            
        Example:
            >>> UnitConversions.meters_to_centimeters(1.0)
            100.0
        """
        return meters * METERS_TO_CM

    @staticmethod
    def centimeters_to_meters(centimeters: float) -> float:
        """
        Convert length from centimeters to meters.
        
        Args:
            centimeters: Length in centimeters
            
        Returns:
            Length in meters
            
        Example:
            >>> UnitConversions.centimeters_to_meters(100.0)
            1.0
        """
        return centimeters * CM_TO_METERS

    @staticmethod
    def m_s_to_mph(m_s: float) -> float:
        """
        Convert wind speed from meters per second to miles per hour.
        
        Args:
            m_s: Wind speed in m/s
            
        Returns:
            Wind speed in mph
            
        Example:
            >>> UnitConversions.m_s_to_mph(10.0)
            22.369...
        """
        return m_s * M_S_TO_MPH

    @staticmethod
    def mph_to_m_s(mph: float) -> float:
        """
        Convert wind speed from miles per hour to meters per second.
        
        Args:
            mph: Wind speed in mph
            
        Returns:
            Wind speed in m/s
            
        Example:
            >>> UnitConversions.mph_to_m_s(22.369)
            9.999...
        """
        return mph * MPH_TO_M_S

    @staticmethod
    def w_m_c_to_cal_s_cm_c(w_m_c: float) -> float:
        """
        Convert thermal conductivity from W/(m·°C) to cal/(s·cm·°C).
        
        Args:
            w_m_c: Thermal conductivity in W/(m·°C)
            
        Returns:
            Thermal conductivity in cal/(s·cm·°C)
            
        Example:
            >>> UnitConversions.w_m_c_to_cal_s_cm_c(0.6)
            0.001433...
        """
        return w_m_c * W_M_C_TO_CAL_S_CM_C

    @staticmethod
    def cal_s_cm_c_to_w_m_c(cal_s_cm_c: float) -> float:
        """
        Convert thermal conductivity from cal/(s·cm·°C) to W/(m·°C).
        
        Args:
            cal_s_cm_c: Thermal conductivity in cal/(s·cm·°C)
            
        Returns:
            Thermal conductivity in W/(m·°C)
            
        Example:
            >>> UnitConversions.cal_s_cm_c_to_w_m_c(0.001433)
            0.599...
        """
        return cal_s_cm_c / W_M_C_TO_CAL_S_CM_C
