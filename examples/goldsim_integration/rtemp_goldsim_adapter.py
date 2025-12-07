"""
GoldSim-rTemp Integration Adapter (Simplified - No Dewpoint Inputs)

This module provides the GSPy interface for integrating the rTemp water temperature
model into GoldSim simulations. It implements a Stateless Physics Engine architecture
where GoldSim manages state and this adapter performs thermal calculations.

The adapter receives daily meteorological data (min/max values), disaggregates them
to hourly resolution, executes rTemp for 24 hours, and returns final state values.

DEWPOINT ESTIMATION: Dewpoint is automatically estimated from air temperature using
typical dewpoint depression values. No dewpoint inputs are required from GoldSim.

Requirements: 1.1, 2.8, 2.9
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import traceback

# GSPy interface (will be available when called from GoldSim)
try:
    import gspy
except ImportError:
    # Fallback for testing outside GoldSim
    class MockGSPy:
        @staticmethod
        def log(message, level=2):
            print(f"[LOG {level}] {message}")
        
        @staticmethod
        def error(message):
            print(f"[ERROR] {message}")
            raise RuntimeError(message)
    
    gspy = MockGSPy()

from rtemp.model import RTempModel
from rtemp.config import ModelConfiguration
from rtemp.solar.position import NOAASolarPosition

# Configuration constants
DRY_BED_THRESHOLD = 0.01  # meters - water depth below this triggers dry-bed bypass

# Dewpoint depression parameters (typical values for different humidity conditions)
# These represent the difference between air temperature and dewpoint
# Adjust these values based on your climate:
#   Humid climates (coastal, tropical): MIN=1.0, MAX=5.0
#   Moderate climates (temperate): MIN=2.0, MAX=8.0
#   Dry climates (arid, desert): MIN=5.0, MAX=15.0
DEWPOINT_DEPRESSION_MIN = 2.0  # °C - for humid conditions (near Tmin, typically at night)
DEWPOINT_DEPRESSION_MAX = 8.0  # °C - for dry conditions (near Tmax, typically afternoon)

# IMPORTANT: Set this to match your GoldSim simulation start date
# This ensures correct solar geometry calculations for accurate solar radiation
# Example: If GoldSim starts on January 1, 2024, use datetime(2024, 1, 1)
REFERENCE_DATE = datetime(2024, 1, 1)


def estimate_dewpoint_from_air_temp(air_temp_min, air_temp_max):
    """
    Estimate dewpoint min/max from air temperature using typical dewpoint depression.
    
    This is a simple empirical approach suitable when dewpoint data is not available.
    The method assumes:
    - Higher relative humidity at night (near Tmin) -> smaller dewpoint depression
    - Lower relative humidity during day (near Tmax) -> larger dewpoint depression
    
    Args:
        air_temp_min (float): Daily minimum air temperature (°C)
        air_temp_max (float): Daily maximum air temperature (°C)
    
    Returns:
        tuple: (dewpoint_min, dewpoint_max) in °C
    
    Note:
        This is an approximation. For better accuracy, use actual dewpoint or
        relative humidity measurements if available.
    """
    # Dewpoint minimum occurs near air temperature minimum (nighttime, higher RH)
    # Use smaller depression for more humid nighttime conditions
    dewpoint_min = air_temp_min - DEWPOINT_DEPRESSION_MIN
    
    # Dewpoint maximum occurs during the day but with larger depression
    # Use larger depression for drier daytime conditions
    dewpoint_max = air_temp_max - DEWPOINT_DEPRESSION_MAX
    
    # Ensure dewpoint_max is not less than dewpoint_min
    if dewpoint_max < dewpoint_min:
        dewpoint_max = dewpoint_min + 1.0
    
    return dewpoint_min, dewpoint_max


def disaggregate_temperature(t_min, t_max, sunrise_frac):
    """
    Disaggregate daily min/max temperature to 24 hourly values.
    
    Uses sinusoidal pattern with minimum at sunrise and maximum at 2-3 PM local solar time.
    This implements Requirement 2.1 and 2.2 for temperature disaggregation.
    
    The diurnal temperature pattern is modeled using a sinusoidal wave where:
    - Minimum occurs at sunrise (when solar heating begins)
    - Maximum occurs at 14.5 hours (2:30 PM, typical afternoon peak)
    - The pattern repeats over a 24-hour cycle
    
    Args:
        t_min (float): Daily minimum temperature (°C)
        t_max (float): Daily maximum temperature (°C)
        sunrise_frac (float): Sunrise time as fraction of day (0-1)
    
    Returns:
        numpy.ndarray: Array of 24 hourly temperatures (°C)
    
    Requirements: 2.1, 2.2, 2.3
    """
    # Time of maximum temperature (14:30 = 14.5 hours)
    # This represents typical afternoon maximum (2-3 PM local solar time)
    tmax_hour = 14.5
    
    # Time of minimum temperature (at sunrise)
    tmin_hour = sunrise_frac * 24.0
    
    # Mean and amplitude for sinusoidal pattern
    t_mean = (t_min + t_max) / 2.0
    t_amp = (t_max - t_min) / 2.0
    
    # Generate hourly values using sinusoidal pattern
    # We use a sine wave with a 24-hour period, shifted so that:
    #   - Minimum (-1) occurs at tmin_hour (sunrise)
    # Note: With a 24-hour period, the maximum will occur ~12 hours after minimum
    # This is a reasonable approximation for diurnal temperature patterns
    
    hourly_temps = np.zeros(24)
    for hour in range(24):
        # Calculate hours since minimum (sunrise)
        hours_since_min = hour - tmin_hour
        if hours_since_min < 0:
            hours_since_min += 24.0
        
        # Use a 24-hour sinusoidal cycle
        # At hours_since_min = 0: angle = -π/2 (minimum, sin = -1)
        # At hours_since_min = 12: angle = π/2 (maximum, sin = +1)
        # At hours_since_min = 24: angle = 3π/2 (back to minimum, sin = -1)
        angle = -np.pi / 2.0 + 2 * np.pi * (hours_since_min / 24.0)
        
        # Sinusoidal pattern: mean + amplitude * sin(angle)
        hourly_temps[hour] = t_mean + t_amp * np.sin(angle)
    
    return hourly_temps


def process_data(*args):
    """
    GoldSim-rTemp adapter function (GSPy entry point).
    
    Receives daily inputs from GoldSim, disaggregates meteorological data to hourly
    resolution, executes rTemp for 24 hours, and returns final state and diagnostics.
    
    This function implements a Stateless Physics Engine pattern - it receives all
    necessary inputs, performs calculations, and returns results without retaining
    state between calls. GoldSim manages state persistence.
    
    Args (via *args tuple):
        args[0]: Current_Water_Temp (float, °C) - Water temperature at start of day
        args[1]: Current_Sediment_Temp (float, °C) - Sediment temperature at start of day
        args[2]: Water_Depth (float, meters) - Water depth (≤0.01 triggers dry-bed logic)
        args[3]: Latitude (float, degrees) - Site latitude (positive north, -90 to 90)
        args[4]: Longitude (float, degrees) - Site longitude (positive east, -180 to 180)
        args[5]: Elevation (float, meters) - Site elevation above sea level
        args[6]: Timezone (float, hours) - Hours from UTC (positive for west)
        args[7]: Air_Temp_Min (float, °C) - Daily minimum air temperature
        args[8]: Air_Temp_Max (float, °C) - Daily maximum air temperature
        args[9]: Wind_Speed_Avg (float, m/s) - Daily average wind speed
        args[10]: Cloud_Cover_Avg (float, fraction) - Daily average cloud cover (0-1)
        args[11]: Simulation_Date (float, days) - Elapsed days from simulation start
    
    Returns:
        tuple: (New_Water_Temp, New_Sediment_Temp, Daily_Avg_Net_Flux)
            - New_Water_Temp (float, °C): Water temperature at end of day
            - New_Sediment_Temp (float, °C): Sediment temperature at end of day
            - Daily_Avg_Net_Flux (float, W/m²): Mean net heat flux over 24 hours
    
    Raises:
        Calls gspy.error() for fatal errors (invalid inputs, numerical errors)
        Returns safe fallback tuple after logging error
    """
    try:
        # Unpack inputs from args tuple (12 inputs total)
        # State variables (managed by GoldSim, passed forward each timestep)
        current_water_temp = float(args[0])
        current_sediment_temp = float(args[1])
        
        # Hydraulic parameter
        water_depth = float(args[2])
        
        # Site parameters (typically constant but can vary)
        latitude = float(args[3])
        longitude = float(args[4])
        elevation = float(args[5])
        timezone = float(args[6])
        
        # Daily meteorological forcing (min/max values to be disaggregated)
        air_temp_min = float(args[7])
        air_temp_max = float(args[8])
        wind_speed_avg = float(args[9])
        cloud_cover_avg = float(args[10])
        
        # Temporal context (elapsed days from simulation start)
        simulation_date = float(args[11])
        
        # Estimate dewpoint from air temperature
        dewpoint_min, dewpoint_max = estimate_dewpoint_from_air_temp(
            air_temp_min, air_temp_max
        )
        
        # Log execution start (INFO level)
        gspy.log(
            f"Processing day {simulation_date:.1f}: "
            f"depth={water_depth:.3f}m, "
            f"T_air={air_temp_min:.1f}-{air_temp_max:.1f}°C, "
            f"Td_est={dewpoint_min:.1f}-{dewpoint_max:.1f}°C, "
            f"T_water={current_water_temp:.1f}°C",
            2
        )
        
        # Input validation (Task 2 - Requirements 6.3)
        # Validate water depth (must be >= 0)
        if water_depth < 0:
            gspy.log(
                f"Invalid Water_Depth: {water_depth:.4f} meters (must be >= 0). "
                f"Check hydraulic calculations in GoldSim model.",
                0
            )
            gspy.error(f"Invalid Water_Depth: {water_depth:.4f} meters (must be >= 0)")
            return (current_water_temp, current_sediment_temp, 0.0)
        
        # Validate latitude (must be -90 to 90)
        if not (-90 <= latitude <= 90):
            gspy.log(
                f"Invalid Latitude: {latitude:.4f} degrees (must be -90 to 90). "
                f"Check site parameters in GoldSim model.",
                0
            )
            gspy.error(f"Invalid Latitude: {latitude:.4f} degrees (must be -90 to 90)")
            return (current_water_temp, current_sediment_temp, 0.0)
        
        # Validate longitude (must be -180 to 180)
        if not (-180 <= longitude <= 180):
            gspy.log(
                f"Invalid Longitude: {longitude:.4f} degrees (must be -180 to 180). "
                f"Check site parameters in GoldSim model.",
                0
            )
            gspy.error(f"Invalid Longitude: {longitude:.4f} degrees (must be -180 to 180)")
            return (current_water_temp, current_sediment_temp, 0.0)
        
        # Dry-bed bypass logic (Task 3 - Requirements 4.1, 4.2, 4.3, 4.4)
        # When water depth is at or below threshold, skip rTemp calculation
        # and return safe fallback values to avoid numerical instability
        if water_depth <= DRY_BED_THRESHOLD:
            # Log warning message (WARNING level)
            gspy.log(
                f"Dry-bed condition detected (depth={water_depth:.4f}m <= {DRY_BED_THRESHOLD}m). "
                f"Bypassing rTemp calculation. Preserving water temperature, "
                f"setting sediment temperature to mean air temperature.",
                1
            )
            
            # Temperature preservation: return current water temp unchanged
            # Sediment temperature: set to mean of daily air temperature range
            mean_air_temp = (air_temp_min + air_temp_max) / 2.0
            
            # Daily average net flux: set to zero (no heat exchange in dry bed)
            return (current_water_temp, mean_air_temp, 0.0)
        
        # Datetime stamp construction (Task 4 - Requirements 1.2, 11.1, 11.2, 11.3)
        # Calculate the start datetime for this day by adding elapsed days to reference date
        # REFERENCE_DATE must match GoldSim simulation start date for accurate solar geometry
        start_datetime = REFERENCE_DATE + timedelta(days=simulation_date)
        
        # Generate 24 hourly datetime stamps (one for each hour of the day)
        # These will be used by rTemp for solar position calculations and DataFrame indexing
        datetime_stamps = [start_datetime + timedelta(hours=i) for i in range(24)]
        
        # Meteorological DataFrame construction (Task 5 - Requirements 1.2, 2.1-2.6)
        # Step 1: Calculate solar position to get sunrise time for temperature disaggregation
        # This implements Requirement 2.3 - using solar position for timing of temperature extremes
        sunrise_frac = NOAASolarPosition.calc_sunrise(
            latitude, longitude, start_datetime.year, start_datetime.month, 
            start_datetime.day, timezone, 0
        )
        
        # Step 2: Disaggregate daily min/max temperatures to hourly values
        # Uses sinusoidal pattern with minimum at sunrise and maximum at 2-3 PM
        # Requirements 2.1, 2.2
        air_temp_array = disaggregate_temperature(air_temp_min, air_temp_max, sunrise_frac)
        dewpoint_array = disaggregate_temperature(dewpoint_min, dewpoint_max, sunrise_frac)
        
        # Step 3: Create constant hourly arrays for wind speed and cloud cover
        # Requirements 2.4, 2.5
        wind_speed_array = np.full(24, wind_speed_avg)
        cloud_cover_array = np.full(24, cloud_cover_avg)
        
        # Step 4: Construct pandas DataFrame with all meteorological data
        # This DataFrame will be passed to rTemp for thermal calculations
        # Requirement 1.2
        met_data = pd.DataFrame({
            'datetime': datetime_stamps,
            'air_temperature': air_temp_array,
            'dewpoint_temperature': dewpoint_array,
            'wind_speed': wind_speed_array,
            'cloud_cover': cloud_cover_array
        })
        
        # Verify DataFrame has exactly 24 rows (one per hour)
        # This is a critical requirement for rTemp execution
        if len(met_data) != 24:
            gspy.log(
                f"DataFrame construction error: Expected 24 rows, got {len(met_data)}. "
                f"This indicates a bug in datetime stamp generation.",
                0
            )
            gspy.error(f"DataFrame has {len(met_data)} rows, expected 24")
            return (current_water_temp, current_sediment_temp, 0.0)
        
        # rTemp model initialization (Task 6 - Requirements 3.1, 8.1, 8.2, 8.4, 8.5)
        # Create ModelConfiguration with dynamic parameters from GoldSim
        # and static parameters hardcoded for consistent behavior
        config = ModelConfiguration(
            # Dynamic parameters (passed from GoldSim each timestep)
            latitude=latitude,
            longitude=longitude,
            elevation=elevation,
            timezone=timezone,
            initial_water_temp=current_water_temp,
            initial_sediment_temp=current_sediment_temp,
            water_depth=water_depth,
            
            # Static parameters (hardcoded for consistent model behavior)
            # These can be modified in the adapter script if needed
            solar_method="Bras",  # Solar radiation calculation method
            longwave_method="Brunt",  # Longwave radiation calculation method
            wind_function_method="Brady-Graves-Geyer",  # Wind function for heat transfer
            
            # Additional static parameters with default values
            effective_shade=0.0,  # No shade (0-1 fraction)
            wind_height=2.0,  # Wind measurement height (meters)
            effective_wind_factor=1.0,  # Wind adjustment factor (dimensionless)
            sediment_thermal_conductivity=0.0,  # W/(m·°C) - no sediment heat exchange
            sediment_thermal_diffusivity=0.0,  # cm²/s
            sediment_thickness=10.0,  # cm
            hyporheic_exchange_rate=0.0,  # cm/day - no hyporheic exchange
            groundwater_temperature=15.0,  # °C - not used if inflow is 0
            groundwater_inflow=0.0,  # cm/day - no groundwater inflow
            enable_diagnostics=False  # Disable for performance (reduces output columns)
        )
        
        # Create rTemp model instance with the configuration
        # This initializes the model but does not execute calculations yet
        model = RTempModel(config)
        
        # Task 7: rTemp execution and results extraction (Requirements 1.3, 1.4)
        # Execute rTemp model for 24 hours using the meteorological DataFrame
        # The model will internally manage sub-stepping at its configured timestep
        results = model.run(met_data)
        
        # Extract final state from the last row of results DataFrame
        # This represents the end-of-day state after 24 hours of simulation
        # Requirement 1.4: Extract final state values from last row
        final_row = results.iloc[-1]
        
        # Extract water temperature and sediment temperature from final row
        # Convert to float type to ensure compatibility with GSPy return tuple
        # Requirement 1.4: Extract water_temperature and sediment_temperature
        new_water_temp = float(final_row['water_temperature'])
        new_sediment_temp = float(final_row['sediment_temperature'])
        
        # Task 8: Implement diagnostic output calculation (Requirements 7.1, 7.2)
        # Extract net_flux column from results DataFrame
        # Calculate mean of net_flux using NumPy for numerical stability
        # Convert to float type for GSPy return tuple
        daily_avg_net_flux = float(np.mean(results['net_flux']))
        
        # Log execution completion (INFO level)
        gspy.log(
            f"rTemp complete: "
            f"T_water={new_water_temp:.2f}°C, "
            f"T_sed={new_sediment_temp:.2f}°C, "
            f"Q_net={daily_avg_net_flux:.1f}W/m²",
            2
        )
        
        # Return results as tuple (order must match JSON outputs array)
        return (new_water_temp, new_sediment_temp, daily_avg_net_flux)
        
    except Exception as e:
        # Log full traceback at ERROR level
        gspy.log(traceback.format_exc(), 0)
        
        # Signal fatal error to GoldSim (stops simulation)
        gspy.error(f"rTemp adapter error: {str(e)}")
        
        # Return safe fallback values (required but not used after error)
        # Use current state to avoid introducing discontinuities
        return (current_water_temp, current_sediment_temp, 0.0)
