"""
Demonstration of time-varying parameters in rTemp.

This example shows how to use time-varying water depth and
effective shade to model dynamic conditions.
"""

from datetime import datetime, timedelta

import pandas as pd
import numpy as np

from rtemp import ModelConfiguration, RTempModel


def main():
    """Demonstrate time-varying parameters."""
    
    print("=" * 70)
    print("rTemp Model - Time-Varying Parameters Demonstration")
    print("=" * 70)
    print()
    
    # Create model configuration
    config = ModelConfiguration(
        # Site parameters
        latitude=47.5,
        longitude=-122.0,
        elevation=100.0,
        timezone=8.0,
        daylight_savings=0,
        # Initial conditions
        initial_water_temp=15.0,
        initial_sediment_temp=15.0,
        minimum_temperature=0.0,
        # Water body parameters (these will be overridden by time-varying data)
        water_depth=2.0,  # meters (default)
        effective_shade=0.0,  # no shade (default)
        wind_height=2.0,
        effective_wind_factor=1.0,
        # Sediment parameters
        sediment_thermal_conductivity=1.0,
        sediment_thermal_diffusivity=0.005,
        sediment_thickness=15.0,
        hyporheic_exchange_rate=0.0,
        # Groundwater parameters
        groundwater_temperature=12.0,
        groundwater_inflow=0.0,
        # Method selections
        solar_method="Bras",
        longwave_method="Brunt",
        wind_function_method="Brady-Graves-Geyer",
        # Model parameters
        atmospheric_turbidity=2.0,
        atmospheric_transmission_coeff=0.8,
        brutsaert_coefficient=1.24,
        # Cloud correction parameters
        solar_cloud_kcl1=1.0,
        solar_cloud_kcl2=2.0,
        longwave_cloud_method="Eqn 1",
        longwave_cloud_kcl3=1.0,
        longwave_cloud_kcl4=2.0,
        # Stability checking
        stability_criteria=10.0,
        # Output options
        enable_diagnostics=False,
    )
    
    print("Model Configuration:")
    print(f"  Location: {config.latitude}°N, {config.longitude}°W")
    print(f"  Default water depth: {config.water_depth} m")
    print(f"  Default effective shade: {config.effective_shade}")
    print()
    
    # Scenario 1: Varying water depth (simulating tidal influence or flow changes)
    print("=" * 70)
    print("Scenario 1: Time-Varying Water Depth")
    print("=" * 70)
    print()
    print("Simulating tidal influence with sinusoidal depth variation")
    print()
    
    start_date = datetime(2024, 7, 15, 0, 0)
    hours = 48  # 2 days
    
    met_data_depth = []
    for hour in range(hours):
        dt = start_date + timedelta(hours=hour)
        
        # Meteorological conditions
        hour_of_day = hour % 24
        temp_variation = 10.0 * (1 - abs(hour_of_day - 15) / 12.0)
        air_temp = 15.0 + temp_variation
        dewpoint = air_temp - 5.0
        wind_speed = 2.5
        cloud_cover = 0.2
        
        # Time-varying water depth (tidal-like pattern, 12-hour period)
        # Depth varies between 1.5m and 2.5m
        depth = 2.0 + 0.5 * np.sin(2 * np.pi * hour / 12.0)
        
        met_data_depth.append({
            'datetime': dt,
            'air_temperature': air_temp,
            'dewpoint_temperature': dewpoint,
            'wind_speed': wind_speed,
            'cloud_cover': cloud_cover,
            'water_depth_override': depth,  # Time-varying depth
        })
    
    met_df_depth = pd.DataFrame(met_data_depth)
    
    print(f"Water depth variation:")
    print(f"  Minimum: {met_df_depth['water_depth_override'].min():.2f} m")
    print(f"  Maximum: {met_df_depth['water_depth_override'].max():.2f} m")
    print(f"  Mean:    {met_df_depth['water_depth_override'].mean():.2f} m")
    print()
    
    print("Running model with varying depth...")
    model_depth = RTempModel(config)
    results_depth = model_depth.run(met_df_depth)
    print(f"  Model completed successfully")
    print()
    
    print("Results:")
    print(f"  Final water temperature: {results_depth['water_temperature'].iloc[-1]:.2f}°C")
    print(f"  Temperature range: {results_depth['water_temperature'].min():.2f}°C to "
          f"{results_depth['water_temperature'].max():.2f}°C")
    print()
    
    # Show how depth affects temperature
    print("Depth vs Temperature correlation:")
    # Get depth from state (it's stored in the model during execution)
    # For display, we'll use the input depth
    depth_temp_corr = np.corrcoef(
        met_df_depth['water_depth_override'], 
        results_depth['water_temperature']
    )[0, 1]
    print(f"  Correlation coefficient: {depth_temp_corr:.3f}")
    print(f"  (Negative correlation expected: deeper water = slower temperature change)")
    print()
    
    # Export results
    import os
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)
    output_file_depth = os.path.join(output_dir, "rtemp_varying_depth_output.csv")
    model_depth.export_results(output_file_depth)
    print(f"Results exported to: {output_file_depth}")
    print()
    
    # Scenario 2: Varying effective shade (simulating tree canopy or cloud shadows)
    print("=" * 70)
    print("Scenario 2: Time-Varying Effective Shade")
    print("=" * 70)
    print()
    print("Simulating moving cloud shadows with varying shade")
    print()
    
    met_data_shade = []
    for hour in range(24):
        dt = start_date + timedelta(hours=hour)
        
        # Meteorological conditions
        hour_of_day = hour
        temp_variation = 10.0 * (1 - abs(hour_of_day - 15) / 12.0)
        air_temp = 15.0 + temp_variation
        dewpoint = air_temp - 5.0
        wind_speed = 2.5
        cloud_cover = 0.1  # Low cloud cover
        
        # Time-varying shade (simulating intermittent cloud shadows)
        # Shade varies between 0% and 60% with a 6-hour pattern
        if hour < 6 or hour > 18:
            shade = 0.0  # No shade at night
        else:
            shade = 0.3 + 0.3 * np.sin(2 * np.pi * (hour - 6) / 6.0)
        
        met_data_shade.append({
            'datetime': dt,
            'air_temperature': air_temp,
            'dewpoint_temperature': dewpoint,
            'wind_speed': wind_speed,
            'cloud_cover': cloud_cover,
            'effective_shade_override': shade,  # Time-varying shade
        })
    
    met_df_shade = pd.DataFrame(met_data_shade)
    
    print(f"Effective shade variation:")
    print(f"  Minimum: {met_df_shade['effective_shade_override'].min():.2%}")
    print(f"  Maximum: {met_df_shade['effective_shade_override'].max():.2%}")
    print(f"  Mean:    {met_df_shade['effective_shade_override'].mean():.2%}")
    print()
    
    print("Running model with varying shade...")
    model_shade = RTempModel(config)
    results_shade = model_shade.run(met_df_shade)
    print(f"  Model completed successfully")
    print()
    
    print("Results:")
    print(f"  Final water temperature: {results_shade['water_temperature'].iloc[-1]:.2f}°C")
    print(f"  Mean solar radiation: {results_shade['solar_radiation'].mean():.2f} W/m²")
    print()
    
    # Compare with no shade scenario
    print("Comparing with constant no-shade scenario...")
    met_df_no_shade = met_df_shade.copy()
    met_df_no_shade['effective_shade_override'] = 0.0
    
    model_no_shade = RTempModel(config)
    results_no_shade = model_no_shade.run(met_df_no_shade)
    
    print(f"  No shade - Final temp: {results_no_shade['water_temperature'].iloc[-1]:.2f}°C")
    print(f"  No shade - Mean solar: {results_no_shade['solar_radiation'].mean():.2f} W/m²")
    print(f"  Varying shade - Final temp: {results_shade['water_temperature'].iloc[-1]:.2f}°C")
    print(f"  Varying shade - Mean solar: {results_shade['solar_radiation'].mean():.2f} W/m²")
    print(f"  Temperature difference: "
          f"{results_no_shade['water_temperature'].iloc[-1] - results_shade['water_temperature'].iloc[-1]:.2f}°C")
    print(f"  Solar radiation difference: "
          f"{results_no_shade['solar_radiation'].mean() - results_shade['solar_radiation'].mean():.2f} W/m²")
    print()
    
    # Export results
    output_file_shade = os.path.join(output_dir, "rtemp_varying_shade_output.csv")
    model_shade.export_results(output_file_shade)
    print(f"Results exported to: {output_file_shade}")
    print()
    
    # Scenario 3: Combined varying depth and shade
    print("=" * 70)
    print("Scenario 3: Combined Time-Varying Depth and Shade")
    print("=" * 70)
    print()
    print("Simulating complex scenario with both depth and shade variations")
    print()
    
    met_data_combined = []
    for hour in range(24):
        dt = start_date + timedelta(hours=hour)
        
        # Meteorological conditions
        hour_of_day = hour
        temp_variation = 10.0 * (1 - abs(hour_of_day - 15) / 12.0)
        air_temp = 15.0 + temp_variation
        dewpoint = air_temp - 5.0
        wind_speed = 2.5 + 1.5 * np.sin(2 * np.pi * hour / 24.0)
        cloud_cover = 0.2 + 0.3 * np.sin(2 * np.pi * hour / 12.0)
        
        # Time-varying depth (8-hour tidal pattern)
        depth = 2.0 + 0.4 * np.sin(2 * np.pi * hour / 8.0)
        
        # Time-varying shade (riparian vegetation pattern)
        if hour < 8:
            shade = 0.6  # Morning shade from east
        elif hour < 12:
            shade = 0.3  # Partial shade
        elif hour < 16:
            shade = 0.1  # Minimal shade at midday
        elif hour < 20:
            shade = 0.4  # Afternoon shade from west
        else:
            shade = 0.0  # No shade at night
        
        met_data_combined.append({
            'datetime': dt,
            'air_temperature': air_temp,
            'dewpoint_temperature': dewpoint,
            'wind_speed': wind_speed,
            'cloud_cover': cloud_cover,
            'water_depth_override': depth,
            'effective_shade_override': shade,
        })
    
    met_df_combined = pd.DataFrame(met_data_combined)
    
    print(f"Combined variations:")
    print(f"  Depth:  {met_df_combined['water_depth_override'].min():.2f} m to "
          f"{met_df_combined['water_depth_override'].max():.2f} m")
    print(f"  Shade:  {met_df_combined['effective_shade_override'].min():.0%} to "
          f"{met_df_combined['effective_shade_override'].max():.0%}")
    print()
    
    print("Running model with combined variations...")
    model_combined = RTempModel(config)
    results_combined = model_combined.run(met_df_combined)
    print(f"  Model completed successfully")
    print()
    
    print("Results:")
    print(f"  Final water temperature: {results_combined['water_temperature'].iloc[-1]:.2f}°C")
    print(f"  Temperature range: {results_combined['water_temperature'].min():.2f}°C to "
          f"{results_combined['water_temperature'].max():.2f}°C")
    print(f"  Mean solar radiation: {results_combined['solar_radiation'].mean():.2f} W/m²")
    print()
    
    # Export results
    output_file_combined = os.path.join(output_dir, "rtemp_combined_varying_output.csv")
    model_combined.export_results(output_file_combined)
    print(f"Results exported to: {output_file_combined}")
    print()
    
    print("=" * 70)
    print("Key Insights:")
    print("=" * 70)
    print()
    print("1. Time-Varying Water Depth:")
    print("   - Deeper water has higher thermal inertia")
    print("   - Temperature changes more slowly in deeper water")
    print("   - Important for tidal systems and regulated flows")
    print()
    print("2. Time-Varying Effective Shade:")
    print("   - Shade significantly reduces solar radiation input")
    print("   - Can represent riparian vegetation, clouds, or structures")
    print("   - Important for stream temperature management")
    print()
    print("3. Combined Effects:")
    print("   - Multiple time-varying parameters can be used simultaneously")
    print("   - Allows modeling of complex, realistic scenarios")
    print("   - Essential for accurate predictions in dynamic systems")
    print()
    print("=" * 70)
    print("Demonstration complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
