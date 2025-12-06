"""
Demonstration of all calculation methods in rTemp.

This example shows how to use different solar radiation models,
longwave radiation methods, and wind functions.
"""

from datetime import datetime, timedelta

import pandas as pd

from rtemp import ModelConfiguration, RTempModel


def create_sample_data(hours: int = 24) -> pd.DataFrame:
    """Create sample meteorological data."""
    start_date = datetime(2024, 7, 15, 0, 0)
    
    met_data = []
    for hour in range(hours):
        dt = start_date + timedelta(hours=hour)
        
        # Simple diurnal patterns
        temp_variation = 10.0 * (1 - abs(hour - 15) / 12.0)
        air_temp = 15.0 + temp_variation
        dewpoint = air_temp - 5.0
        wind_speed = 2.0 + 1.0 * (hour % 6) / 6.0
        cloud_cover = 0.2 + 0.3 * (hour % 12) / 12.0
        
        met_data.append({
            'datetime': dt,
            'air_temperature': air_temp,
            'dewpoint_temperature': dewpoint,
            'wind_speed': wind_speed,
            'cloud_cover': cloud_cover,
        })
    
    return pd.DataFrame(met_data)


def run_with_methods(solar_method: str, longwave_method: str, 
                     wind_method: str, met_data: pd.DataFrame) -> dict:
    """Run model with specified methods and return summary."""
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
        effective_shade=0.0,
        wind_height=2.0,
        effective_wind_factor=1.0,
        # Sediment parameters
        sediment_thermal_conductivity=0.0,
        sediment_thermal_diffusivity=0.0,
        sediment_thickness=10.0,
        hyporheic_exchange_rate=0.0,
        # Groundwater parameters
        groundwater_temperature=12.0,
        groundwater_inflow=0.0,
        # Method selections
        solar_method=solar_method,
        longwave_method=longwave_method,
        wind_function_method=wind_method,
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
    
    model = RTempModel(config)
    results = model.run(met_data)
    
    return {
        'final_temp': results['water_temperature'].iloc[-1],
        'mean_temp': results['water_temperature'].mean(),
        'mean_solar': results['solar_radiation'].mean(),
        'mean_longwave': results['longwave_atmospheric'].mean(),
        'mean_evap': results['evaporation'].mean(),
        'mean_conv': results['convection'].mean(),
    }


def main():
    """Demonstrate all calculation methods."""
    
    print("=" * 70)
    print("rTemp Model - All Methods Demonstration")
    print("=" * 70)
    print()
    
    # Create sample data
    print("Creating sample meteorological data...")
    met_data = create_sample_data(hours=24)
    print(f"  Created {len(met_data)} hourly records")
    print()
    
    # Test all solar radiation methods
    print("=" * 70)
    print("Solar Radiation Methods Comparison")
    print("=" * 70)
    print()
    
    solar_methods = ["Bras", "Bird", "Ryan-Stolzenbach", "Iqbal"]
    solar_results = {}
    
    for method in solar_methods:
        print(f"Running with {method} solar method...")
        result = run_with_methods(
            solar_method=method,
            longwave_method="Brunt",
            wind_method="Brady-Graves-Geyer",
            met_data=met_data
        )
        solar_results[method] = result
        print(f"  Final water temp: {result['final_temp']:.2f}°C")
        print(f"  Mean solar radiation: {result['mean_solar']:.2f} W/m²")
        print()
    
    print("Solar Method Summary:")
    print(f"  {'Method':<20} {'Final Temp (°C)':<18} {'Mean Solar (W/m²)':<18}")
    print("  " + "-" * 56)
    for method, result in solar_results.items():
        print(f"  {method:<20} {result['final_temp']:>16.2f}  {result['mean_solar']:>16.2f}")
    print()
    
    # Test all longwave radiation methods
    print("=" * 70)
    print("Longwave Radiation Methods Comparison")
    print("=" * 70)
    print()
    
    longwave_methods = ["Brunt", "Brutsaert", "Satterlund", 
                        "Idso-Jackson", "Swinbank", "Koberg"]
    longwave_results = {}
    
    for method in longwave_methods:
        print(f"Running with {method} longwave method...")
        result = run_with_methods(
            solar_method="Bras",
            longwave_method=method,
            wind_method="Brady-Graves-Geyer",
            met_data=met_data
        )
        longwave_results[method] = result
        print(f"  Final water temp: {result['final_temp']:.2f}°C")
        print(f"  Mean longwave atmospheric: {result['mean_longwave']:.2f} W/m²")
        print()
    
    print("Longwave Method Summary:")
    print(f"  {'Method':<20} {'Final Temp (°C)':<18} {'Mean Longwave (W/m²)':<20}")
    print("  " + "-" * 60)
    for method, result in longwave_results.items():
        print(f"  {method:<20} {result['final_temp']:>16.2f}  {result['mean_longwave']:>18.2f}")
    print()
    
    # Test all wind function methods
    print("=" * 70)
    print("Wind Function Methods Comparison")
    print("=" * 70)
    print()
    
    wind_methods = ["Brady-Graves-Geyer", "Marciano-Harbeck", 
                    "Ryan-Harleman", "East Mesa", "Helfrich"]
    wind_results = {}
    
    for method in wind_methods:
        print(f"Running with {method} wind function...")
        result = run_with_methods(
            solar_method="Bras",
            longwave_method="Brunt",
            wind_method=method,
            met_data=met_data
        )
        wind_results[method] = result
        print(f"  Final water temp: {result['final_temp']:.2f}°C")
        print(f"  Mean evaporation: {result['mean_evap']:.2f} W/m²")
        print(f"  Mean convection: {result['mean_conv']:.2f} W/m²")
        print()
    
    print("Wind Function Summary:")
    print(f"  {'Method':<22} {'Final Temp (°C)':<18} {'Mean Evap (W/m²)':<18}")
    print("  " + "-" * 60)
    for method, result in wind_results.items():
        print(f"  {method:<22} {result['final_temp']:>16.2f}  {result['mean_evap']:>16.2f}")
    print()
    
    print("=" * 70)
    print("Key Observations:")
    print("=" * 70)
    print()
    print("1. Solar Methods:")
    print("   - Different methods account for atmospheric effects differently")
    print("   - Bird and Iqbal are more detailed, considering aerosols and gases")
    print("   - Bras and Ryan-Stolzenbach are simpler, using turbidity factors")
    print()
    print("2. Longwave Methods:")
    print("   - All methods estimate atmospheric emissivity")
    print("   - Methods differ in their dependence on vapor pressure and temperature")
    print("   - Koberg includes clearness factor from solar calculations")
    print()
    print("3. Wind Functions:")
    print("   - Different methods calibrated for different water body types")
    print("   - Ryan-Harleman and East Mesa use virtual temperature")
    print("   - Marciano-Harbeck calibrated for Lake Hefner")
    print()
    print("=" * 70)
    print("Demonstration complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
