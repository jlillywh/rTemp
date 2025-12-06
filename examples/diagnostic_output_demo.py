"""
Demonstration of diagnostic output in rTemp.

This example shows how to enable and use diagnostic output
to understand model behavior and intermediate calculations.
"""

from datetime import datetime, timedelta

import pandas as pd

from rtemp import ModelConfiguration, RTempModel


def main():
    """Demonstrate diagnostic output capabilities."""
    
    print("=" * 70)
    print("rTemp Model - Diagnostic Output Demonstration")
    print("=" * 70)
    print()
    
    # Create model configuration with diagnostics enabled
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
        # Water body parameters
        water_depth=2.0,
        effective_shade=0.2,  # 20% shade
        wind_height=10.0,  # Wind measured at 10m
        effective_wind_factor=0.8,  # 20% wind reduction
        # Sediment parameters
        sediment_thermal_conductivity=1.5,  # W/m/°C
        sediment_thermal_diffusivity=0.005,  # cm²/s
        sediment_thickness=20.0,  # cm
        hyporheic_exchange_rate=5.0,  # cm/day
        # Groundwater parameters
        groundwater_temperature=12.0,
        groundwater_inflow=2.0,  # cm/day
        # Method selections
        solar_method="Bird",
        longwave_method="Brutsaert",
        wind_function_method="Ryan-Harleman",
        # Model parameters
        atmospheric_turbidity=2.5,
        atmospheric_transmission_coeff=0.8,
        brutsaert_coefficient=1.24,
        # Cloud correction parameters
        solar_cloud_kcl1=0.9,
        solar_cloud_kcl2=2.5,
        longwave_cloud_method="Eqn 2",
        longwave_cloud_kcl3=0.95,
        longwave_cloud_kcl4=2.0,
        # Stability checking
        stability_criteria=10.0,
        # Output options - ENABLE DIAGNOSTICS
        enable_diagnostics=True,
    )
    
    print("Model Configuration:")
    print(f"  Location: {config.latitude}°N, {config.longitude}°W")
    print(f"  Elevation: {config.elevation} m")
    print(f"  Water depth: {config.water_depth} m")
    print(f"  Effective shade: {config.effective_shade * 100:.0f}%")
    print(f"  Wind height: {config.wind_height} m")
    print(f"  Effective wind factor: {config.effective_wind_factor}")
    print(f"  Diagnostics: ENABLED")
    print()
    
    # Create sample meteorological data for 12 hours
    print("Creating sample meteorological data (12 hours)...")
    start_date = datetime(2024, 7, 15, 6, 0)  # Start at 6 AM
    
    met_data = []
    for hour in range(12):
        dt = start_date + timedelta(hours=hour)
        
        # Diurnal patterns
        hour_of_day = 6 + hour
        temp_variation = 10.0 * (1 - abs(hour_of_day - 15) / 12.0)
        air_temp = 15.0 + temp_variation
        dewpoint = air_temp - 5.0
        wind_speed = 3.0 + 2.0 * (hour % 6) / 6.0
        cloud_cover = 0.1 + 0.4 * (hour % 8) / 8.0
        
        met_data.append({
            'datetime': dt,
            'air_temperature': air_temp,
            'dewpoint_temperature': dewpoint,
            'wind_speed': wind_speed,
            'cloud_cover': cloud_cover,
        })
    
    met_df = pd.DataFrame(met_data)
    print(f"  Created {len(met_df)} hourly records")
    print()
    
    # Run model with diagnostics
    print("Running model with diagnostics enabled...")
    model = RTempModel(config)
    results = model.run(met_df)
    print(f"  Model completed successfully")
    print()
    
    # Display diagnostic information
    print("=" * 70)
    print("Diagnostic Output Analysis")
    print("=" * 70)
    print()
    
    # Check which diagnostic columns are available
    diagnostic_cols = [col for col in results.columns if col not in [
        'datetime', 'solar_azimuth', 'solar_elevation', 'solar_radiation',
        'longwave_atmospheric', 'longwave_back', 'evaporation', 'convection',
        'sediment_conduction', 'hyporheic_exchange', 'groundwater', 'net_flux',
        'water_temperature', 'sediment_temperature', 'air_temperature', 
        'dewpoint_temperature'
    ]]
    
    print(f"Available diagnostic fields: {', '.join(diagnostic_cols)}")
    print()
    
    # Display sample of diagnostic data
    print("Sample Diagnostic Data (first 3 timesteps):")
    print("-" * 70)
    
    display_cols = ['datetime', 'water_temperature', 'air_temperature']
    if diagnostic_cols:
        display_cols.extend(diagnostic_cols[:5])  # Show first 5 diagnostic columns
    
    print(results[display_cols].head(3).to_string(index=False))
    print()
    
    # Analyze vapor pressure
    if 'vapor_pressure_water' in results.columns:
        print("Vapor Pressure Analysis:")
        print(f"  Water vapor pressure:")
        print(f"    Mean: {results['vapor_pressure_water'].mean():.2f} mmHg")
        print(f"    Min:  {results['vapor_pressure_water'].min():.2f} mmHg")
        print(f"    Max:  {results['vapor_pressure_water'].max():.2f} mmHg")
        print(f"  Air vapor pressure:")
        print(f"    Mean: {results['vapor_pressure_air'].mean():.2f} mmHg")
        print(f"    Min:  {results['vapor_pressure_air'].min():.2f} mmHg")
        print(f"    Max:  {results['vapor_pressure_air'].max():.2f} mmHg")
        print(f"  Vapor pressure deficit:")
        vp_deficit = results['vapor_pressure_water'] - results['vapor_pressure_air']
        print(f"    Mean: {vp_deficit.mean():.2f} mmHg")
        print()
    
    # Analyze atmospheric emissivity
    if 'atmospheric_emissivity' in results.columns:
        print("Atmospheric Emissivity:")
        print(f"  Mean: {results['atmospheric_emissivity'].mean():.4f}")
        print(f"  Min:  {results['atmospheric_emissivity'].min():.4f}")
        print(f"  Max:  {results['atmospheric_emissivity'].max():.4f}")
        print()
    
    # Analyze wind speeds at different heights
    if 'wind_speed_2m' in results.columns and 'wind_speed_7m' in results.columns:
        print("Wind Speed Adjustment:")
        print(f"  Wind at 2m height:")
        print(f"    Mean: {results['wind_speed_2m'].mean():.2f} m/s")
        print(f"  Wind at 7m height:")
        print(f"    Mean: {results['wind_speed_7m'].mean():.2f} m/s")
        print(f"  Ratio (7m/2m): {(results['wind_speed_7m'].mean() / results['wind_speed_2m'].mean()):.2f}")
        print()
    
    # Analyze wind function
    if 'wind_function' in results.columns:
        print("Wind Function:")
        print(f"  Mean: {results['wind_function'].mean():.2f} cal/cm²/day/mmHg")
        print(f"  Min:  {results['wind_function'].min():.2f} cal/cm²/day/mmHg")
        print(f"  Max:  {results['wind_function'].max():.2f} cal/cm²/day/mmHg")
        print()
    
    # Analyze temperature change rates
    if 'water_temp_change_rate' in results.columns:
        print("Temperature Change Rates:")
        print(f"  Water temperature change rate:")
        print(f"    Mean: {results['water_temp_change_rate'].mean():.4f} °C/day")
        print(f"    Min:  {results['water_temp_change_rate'].min():.4f} °C/day")
        print(f"    Max:  {results['water_temp_change_rate'].max():.4f} °C/day")
        if 'sediment_temp_change_rate' in results.columns:
            print(f"  Sediment temperature change rate:")
            print(f"    Mean: {results['sediment_temp_change_rate'].mean():.4f} °C/day")
            print(f"    Min:  {results['sediment_temp_change_rate'].min():.4f} °C/day")
            print(f"    Max:  {results['sediment_temp_change_rate'].max():.4f} °C/day")
        print()
    
    # Display detailed timestep analysis
    print("=" * 70)
    print("Detailed Timestep Analysis (Noon - Hour 6)")
    print("=" * 70)
    print()
    
    noon_idx = 6  # 6 hours after 6 AM = noon
    if noon_idx < len(results):
        noon_data = results.iloc[noon_idx]
        
        print(f"Time: {noon_data['datetime']}")
        print()
        print("Meteorological Conditions:")
        print(f"  Air temperature:     {noon_data['air_temperature']:7.2f} °C")
        print(f"  Dewpoint:            {noon_data['dewpoint_temperature']:7.2f} °C")
        print()
        print("Solar Position:")
        print(f"  Azimuth:             {noon_data['solar_azimuth']:7.2f}°")
        print(f"  Elevation:           {noon_data['solar_elevation']:7.2f}°")
        print()
        print("Heat Fluxes:")
        print(f"  Solar radiation:     {noon_data['solar_radiation']:7.2f} W/m²")
        print(f"  Longwave atm:        {noon_data['longwave_atmospheric']:7.2f} W/m²")
        print(f"  Longwave back:       {noon_data['longwave_back']:7.2f} W/m²")
        print(f"  Evaporation:         {noon_data['evaporation']:7.2f} W/m²")
        print(f"  Convection:          {noon_data['convection']:7.2f} W/m²")
        print(f"  Sediment conduction: {noon_data['sediment_conduction']:7.2f} W/m²")
        print(f"  Hyporheic exchange:  {noon_data['hyporheic_exchange']:7.2f} W/m²")
        print(f"  Groundwater:         {noon_data['groundwater']:7.2f} W/m²")
        print(f"  Net flux:            {noon_data['net_flux']:7.2f} W/m²")
        print()
        print("Temperatures:")
        print(f"  Water temperature:   {noon_data['water_temperature']:7.2f} °C")
        print(f"  Sediment temperature:{noon_data['sediment_temperature']:7.2f} °C")
        print()
        
        if 'vapor_pressure_water' in noon_data:
            print("Diagnostic Details:")
            print(f"  Vapor pressure (water): {noon_data['vapor_pressure_water']:7.2f} mmHg")
            print(f"  Vapor pressure (air):   {noon_data['vapor_pressure_air']:7.2f} mmHg")
            if 'atmospheric_emissivity' in noon_data:
                print(f"  Atmospheric emissivity: {noon_data['atmospheric_emissivity']:7.4f}")
            if 'wind_function' in noon_data:
                print(f"  Wind function:          {noon_data['wind_function']:7.2f} cal/cm²/day/mmHg")
            if 'water_temp_change_rate' in noon_data:
                print(f"  Water temp change rate: {noon_data['water_temp_change_rate']:7.4f} °C/day")
            print()
    
    # Export results with diagnostics
    import os
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "rtemp_diagnostic_output.csv")
    model.export_results(output_file, include_diagnostics=True)
    print(f"Results with diagnostics exported to: {output_file}")
    print()
    
    print("=" * 70)
    print("Diagnostic Output Benefits:")
    print("=" * 70)
    print()
    print("1. Vapor Pressure Analysis:")
    print("   - Understand evaporation driving force")
    print("   - Validate humidity calculations")
    print()
    print("2. Atmospheric Emissivity:")
    print("   - See how longwave radiation is calculated")
    print("   - Compare different emissivity methods")
    print()
    print("3. Wind Speed Adjustment:")
    print("   - Verify wind height corrections")
    print("   - Understand wind function inputs")
    print()
    print("4. Temperature Change Rates:")
    print("   - Identify periods of rapid warming/cooling")
    print("   - Debug stability issues")
    print()
    print("=" * 70)
    print("Demonstration complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
