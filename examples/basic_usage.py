"""
Basic usage example for the rTemp water temperature model.

This example demonstrates how to set up and run the rTemp model
with default parameters for a simple scenario.
"""

from datetime import datetime, timedelta

import pandas as pd

from rtemp import ModelConfiguration, RTempModel


def main():
    """Run a basic rTemp model example."""

    print("=" * 70)
    print("rTemp Model - Basic Usage Example")
    print("=" * 70)
    print()

    # Create model configuration with default parameters
    config = ModelConfiguration(
        # Site parameters
        latitude=47.5,  # degrees north (Seattle area)
        longitude=-122.0,  # degrees (negative for west)
        elevation=100.0,  # meters
        timezone=8.0,  # hours from UTC (PST)
        daylight_savings=0,
        # Initial conditions
        initial_water_temp=15.0,  # °C
        initial_sediment_temp=15.0,  # °C
        minimum_temperature=0.0,  # °C
        # Water body parameters
        water_depth=2.0,  # meters
        effective_shade=0.0,  # no shade
        wind_height=2.0,  # meters
        effective_wind_factor=1.0,  # no wind reduction
        # Sediment parameters (defaults)
        sediment_thermal_conductivity=0.0,  # W/m/°C (use water properties)
        sediment_thermal_diffusivity=0.0,  # cm²/s (use water properties)
        sediment_thickness=10.0,  # cm
        hyporheic_exchange_rate=0.0,  # cm/day (no exchange)
        # Groundwater parameters
        groundwater_temperature=12.0,  # °C
        groundwater_inflow=0.0,  # cm/day (no inflow)
        # Method selections (defaults)
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
        stability_criteria=10.0,  # °C
        # Output options
        enable_diagnostics=False,
    )

    print("Model Configuration:")
    print(f"  Location: {config.latitude}°N, {config.longitude}°W")
    print(f"  Elevation: {config.elevation} m")
    print(f"  Water depth: {config.water_depth} m")
    print(f"  Solar method: {config.solar_method}")
    print(f"  Longwave method: {config.longwave_method}")
    print(f"  Wind function: {config.wind_function_method}")
    print()

    # Create sample meteorological data for one day (hourly)
    print("Creating sample meteorological data (24 hours)...")
    start_date = datetime(2024, 7, 15, 0, 0)  # July 15, 2024
    
    met_data = []
    for hour in range(24):
        dt = start_date + timedelta(hours=hour)
        
        # Simple diurnal patterns
        # Temperature peaks at 3 PM (hour 15)
        temp_variation = 10.0 * (1 - abs(hour - 15) / 12.0)
        air_temp = 15.0 + temp_variation
        dewpoint = air_temp - 5.0  # 5°C dewpoint depression
        
        # Wind speed varies slightly
        wind_speed = 2.0 + 1.0 * (hour % 6) / 6.0
        
        # Cloud cover varies
        cloud_cover = 0.2 + 0.3 * (hour % 12) / 12.0
        
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

    # Initialize and run the model
    print("Initializing model...")
    model = RTempModel(config)
    print("  Model initialized successfully")
    print()

    print("Running model...")
    results = model.run(met_df)
    print(f"  Model completed successfully")
    print(f"  Generated {len(results)} output records")
    print()

    # Display summary statistics
    print("=" * 70)
    print("Results Summary")
    print("=" * 70)
    print()
    print(f"Water Temperature:")
    print(f"  Initial: {config.initial_water_temp:.2f}°C")
    print(f"  Final:   {results['water_temperature'].iloc[-1]:.2f}°C")
    print(f"  Min:     {results['water_temperature'].min():.2f}°C")
    print(f"  Max:     {results['water_temperature'].max():.2f}°C")
    print(f"  Mean:    {results['water_temperature'].mean():.2f}°C")
    print()
    
    print(f"Heat Fluxes (W/m²):")
    print(f"  Solar radiation:        {results['solar_radiation'].mean():8.2f} (mean)")
    print(f"  Longwave atmospheric:   {results['longwave_atmospheric'].mean():8.2f} (mean)")
    print(f"  Longwave back:          {results['longwave_back'].mean():8.2f} (mean)")
    print(f"  Evaporation:            {results['evaporation'].mean():8.2f} (mean)")
    print(f"  Convection:             {results['convection'].mean():8.2f} (mean)")
    print(f"  Net flux:               {results['net_flux'].mean():8.2f} (mean)")
    print()

    # Display first few rows
    print("First 5 timesteps:")
    print(results[['datetime', 'water_temperature', 'air_temperature', 
                   'solar_radiation', 'net_flux']].head())
    print()

    # Export results
    import os
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "rtemp_basic_output.csv")
    model.export_results(output_file)
    print(f"Results exported to: {output_file}")
    print()
    
    print("=" * 70)
    print("Example complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
