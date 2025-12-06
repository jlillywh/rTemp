"""
Input validation utilities for the rTemp model.

This module provides validation functions for site parameters, meteorological data,
and timestep checking to ensure data quality and catch common input errors.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd
import numpy as np


class InputValidator:
    """
    Validates input parameters and meteorological data for the rTemp model.
    
    Provides static methods for validating site parameters, meteorological data,
    and timestep sequences. Issues warnings for correctable issues and raises
    errors for invalid inputs that cannot be corrected.
    """
    
    @staticmethod
    def validate_site_parameters(params: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
        """
        Validate site parameters and return corrected values with warnings.
        
        Args:
            params: Dictionary of site parameters
            
        Returns:
            Tuple of (validated_params, warnings)
            
        Raises:
            ValueError: For invalid inputs that cannot be corrected
        """
        validated = params.copy()
        warnings = []
        
        # Requirement 8.1: Water depth must be > 0
        if 'water_depth' in params:
            if params['water_depth'] <= 0:
                raise ValueError("Water depth must be greater than zero")
        
        # Requirement 8.2: Effective shade must be between 0 and 1
        if 'effective_shade' in params:
            if params['effective_shade'] < 0 or params['effective_shade'] > 1:
                raise ValueError("Effective shade must be between 0 and 1")
        
        # Requirement 8.3: Wind height must be > 0
        if 'wind_height' in params:
            if params['wind_height'] <= 0:
                raise ValueError("Wind height must be greater than zero")
        
        # Requirement 8.4: Effective wind factor must be >= 0
        if 'effective_wind_factor' in params:
            if params['effective_wind_factor'] < 0:
                raise ValueError("Effective wind factor must be greater than or equal to zero")
        
        # Requirement 8.5: Groundwater temperature must be >= 0
        if 'groundwater_temperature' in params:
            if params['groundwater_temperature'] < 0:
                raise ValueError("Groundwater temperature must be greater than or equal to zero")
        
        # Requirement 8.6: Groundwater inflow - set to zero if negative
        if 'groundwater_inflow' in params:
            if params['groundwater_inflow'] < 0:
                validated['groundwater_inflow'] = 0.0
                warnings.append("Groundwater inflow was negative, set to zero")
        
        # Requirement 8.7: Sediment thermal conductivity - set to zero if negative
        if 'sediment_thermal_conductivity' in params:
            if params['sediment_thermal_conductivity'] < 0:
                validated['sediment_thermal_conductivity'] = 0.0
                warnings.append("Sediment thermal conductivity was negative, set to zero")
        
        # Requirement 8.8: Sediment thermal diffusivity - assume water properties if <= 0
        if 'sediment_thermal_diffusivity' in params:
            if params['sediment_thermal_diffusivity'] <= 0:
                # Water thermal diffusivity is approximately 0.0014 cm²/s
                validated['sediment_thermal_diffusivity'] = 0.0014
                warnings.append("Sediment thermal diffusivity was zero or negative, assumed equal to water properties")
        
        # Requirement 8.9: Sediment thermal thickness - set to 10 cm if <= 0
        if 'sediment_thickness' in params:
            if params['sediment_thickness'] <= 0:
                validated['sediment_thickness'] = 10.0
                warnings.append("Sediment thermal thickness was zero or negative, set to 10 cm")
        
        # Requirement 8.10: Hyporheic exchange - set to zero if negative
        if 'hyporheic_exchange_rate' in params:
            if params['hyporheic_exchange_rate'] < 0:
                validated['hyporheic_exchange_rate'] = 0.0
                warnings.append("Hyporheic exchange rate was negative, set to zero")
        
        return validated, warnings
    
    @staticmethod
    def validate_meteorological_data(data: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """
        Validate meteorological data and handle missing values.
        
        Args:
            data: DataFrame with meteorological data
            
        Returns:
            Tuple of (validated_data, warnings)
        """
        validated = data.copy()
        warnings = []
        
        # Requirement 8.11: Air temperature missing (≤ -999) - set to 20°C
        if 'air_temperature' in validated.columns:
            missing_air_temp = validated['air_temperature'] <= -999
            if missing_air_temp.any():
                validated.loc[missing_air_temp, 'air_temperature'] = 20.0
                count = missing_air_temp.sum()
                warnings.append(f"Air temperature missing for {count} timestep(s), set to 20°C")
        
        # Requirement 8.12: Dewpoint temperature missing (≤ -999) - set to 10°C
        if 'dewpoint_temperature' in validated.columns:
            missing_dewpoint = validated['dewpoint_temperature'] <= -999
            if missing_dewpoint.any():
                validated.loc[missing_dewpoint, 'dewpoint_temperature'] = 10.0
                count = missing_dewpoint.sum()
                warnings.append(f"Dewpoint temperature missing for {count} timestep(s), set to 10°C")
        
        # Requirement 8.13: Wind speed negative - set to zero
        if 'wind_speed' in validated.columns:
            negative_wind = validated['wind_speed'] < 0
            if negative_wind.any():
                validated.loc[negative_wind, 'wind_speed'] = 0.0
                count = negative_wind.sum()
                warnings.append(f"Wind speed was negative for {count} timestep(s), set to zero")
        
        # Requirement 8.14: Cloud cover negative - set to zero
        if 'cloud_cover' in validated.columns:
            negative_cloud = validated['cloud_cover'] < 0
            if negative_cloud.any():
                validated.loc[negative_cloud, 'cloud_cover'] = 0.0
                count = negative_cloud.sum()
                warnings.append(f"Cloud cover was negative for {count} timestep(s), set to zero")
        
        # Requirement 8.15: Cloud cover > 1 - set to 1
        if 'cloud_cover' in validated.columns:
            excessive_cloud = validated['cloud_cover'] > 1
            if excessive_cloud.any():
                validated.loc[excessive_cloud, 'cloud_cover'] = 1.0
                count = excessive_cloud.sum()
                warnings.append(f"Cloud cover was greater than 1 for {count} timestep(s), set to 1")
        
        return validated, warnings
    
    @staticmethod
    def check_timestep(current_time: datetime, previous_time: datetime) -> Tuple[Optional[str], float]:
        """
        Check timestep for issues and return warning if needed.
        
        Args:
            current_time: Current timestep datetime
            previous_time: Previous timestep datetime
            
        Returns:
            Tuple of (warning_message, timestep_days)
            warning_message is None if no issues detected
        """
        # Calculate timestep in days
        timestep_seconds = (current_time - previous_time).total_seconds()
        timestep_days = timestep_seconds / 86400.0
        
        # Requirement 9.3: Check for zero timestep (duplicate data)
        if timestep_days == 0:
            return ("Duplicate timestep detected (timestep = 0), skipping temperature update", timestep_days)
        
        # Check for negative timestep (time going backwards)
        if timestep_days < 0:
            return (f"Timestep is negative ({timestep_days:.4f} days), timestamps may not be monotonically increasing", timestep_days)
        
        # Requirement 9.1: Timestep > 2 hours warning
        timestep_hours = timestep_days * 24.0
        if timestep_hours > 2.0:
            if timestep_hours > 4.0:
                # Requirement 9.2: Timestep > 4 hours - more severe warning
                return (f"Large timestep detected ({timestep_hours:.2f} hours), consider resetting temperatures to midpoint of air and dewpoint", timestep_days)
            else:
                return (f"Timestep greater than 2 hours ({timestep_hours:.2f} hours), potential accuracy issues", timestep_days)
        
        return (None, timestep_days)
