"""
Long-term validation script comparing Python rTemp with VBA time series output.

This script reads the VBA input time series and parameters, runs the Python model,
and compares the results with the VBA output time series.
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os

from rtemp import ModelConfiguration, RTempModel


def parse_vba_params(filepath):
    """Parse VBA parameter CSV file."""
    import re
    
    def extract_number(value_str):
        """Extract first number from a string."""
        match = re.search(r'-?\d+\.?\d*', value_str)
        if match:
            return float(match.group())
        return None
    
    params = {}
    
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    # Skip header lines and parse parameters
    for line in lines[2:]:  # Skip first 2 lines
        parts = line.strip().split(',')
        if len(parts) >= 2 and parts[1]:
            key = parts[0].strip()
            value = parts[1].strip()
            
            # Map parameter names to values
            if 'latitude' in key.lower():
                params['latitude'] = extract_number(value)
            elif 'longitude' in key.lower():
                params['longitude'] = extract_number(value)
            elif 'elevation' in key.lower():
                params['elevation'] = extract_number(value)
            elif 'time zone' in key.lower():
                params['timezone'] = extract_number(value)
            elif 'daylight savings' in key.lower():
                params['daylight_savings'] = 1 if 'yes' in value.lower() else 0
            elif 'initial response temperature' in key.lower():
                params['initial_water_temp'] = extract_number(value)
            elif 'minimum response temperature' in key.lower():
                params['minimum_temperature'] = extract_number(value)
            elif 'water depth' in key.lower():
                params['water_depth'] = extract_number(value)
            elif 'effective shade' in key.lower():
                params['effective_shade'] = extract_number(value)
            elif 'height of wind speed' in key.lower():
                params['wind_height'] = extract_number(value)
            elif 'effective windspeed' in key.lower():
                params['effective_wind_factor'] = extract_number(value)
            elif 'groundwater temperature' in key.lower():
                params['groundwater_temperature'] = extract_number(value)
            elif 'groundwater inflow' in key.lower():
                params['groundwater_inflow'] = extract_number(value)
            elif 'sediment thermal conductivity' in key.lower():
                params['sediment_thermal_conductivity'] = extract_number(value)
            elif 'sediment thermal diffusivity' in key.lower():
                params['sediment_thermal_diffusivity'] = extract_number(value)
            elif 'sediment thermal thickness' in key.lower():
                params['sediment_thickness'] = extract_number(value)
            elif 'hyporheic exchange' in key.lower():
                params['hyporheic_exchange_rate'] = extract_number(value)
            elif 'solar shortwave radiation model' in key.lower():
                params['solar_method'] = value
            elif 'bras atmospheric turbidity' in key.lower():
                params['atmospheric_turbidity'] = extract_number(value)
            elif 'ryan-stolzenbach atmospheric transmission' in key.lower():
                params['atmospheric_transmission_coeff'] = extract_number(value)
            elif 'coefficient (KCL1)' in key:
                params['solar_cloud_kcl1'] = extract_number(value)
            elif 'exponent (KCL2)' in key:
                params['solar_cloud_kcl2'] = extract_number(value)
            elif 'atmospheric longwave radiation model' in key.lower():
                params['longwave_method'] = value
            elif 'parameter for atmospheric longwave emissivity' in key.lower():
                params['brutsaert_coefficient'] = extract_number(value)
            elif 'model equation for cloud adjustment' in key.lower():
                params['longwave_cloud_method'] = value
            elif 'coefficient (KCL3)' in key:
                params['longwave_cloud_kcl3'] = extract_number(value)
            elif 'exponent (KCL4)' in key:
                params['longwave_cloud_kcl4'] = extract_number(value)
            elif 'wind speed function' in key.lower():
                params['wind_function_method'] = value
            elif 'maximum temperature change' in key.lower():
                params['stability_criteria'] = extract_number(value)
    
    return params


def load_vba_input_ts(filepath):
    """Load VBA input time series."""
    # Read CSV, skipping first row (header description)
    df = pd.read_csv(filepath, skiprows=1)
    
    # Create datetime column
    df['datetime'] = pd.to_datetime(
        df[['year', 'month', 'day', 'hour', 'minute']].rename(columns={
            'year': 'year', 'month': 'month', 'day': 'day',
            'hour': 'hour', 'minute': 'minute'
        })
    )
    
    # Rename columns to match Python model
    df = df.rename(columns={
        'air temperature (deg C)': 'air_temperature',
        'dewpoint temperature (deg C)': 'dewpoint_temperature',
        'wind speed (m/s)': 'wind_speed',
        'cloud cover (fraction)': 'cloud_cover',
        'shortwave solar radiation before shade and reflection (W/m^2)': 'solar_radiation',
    })
    
    # Select only needed columns (including measured solar radiation)
    met_data = df[['datetime', 'air_temperature', 'dewpoint_temperature', 
                    'wind_speed', 'cloud_cover', 'solar_radiation']].copy()
    
    return met_data


def load_vba_output_ts(filepath):
    """Load VBA output time series."""
    # Read CSV, skipping first row (header description)
    df = pd.read_csv(filepath, skiprows=1)
    
    # Parse datetime
    df['datetime'] = pd.to_datetime(df['date-time'])
    
    # Rename columns for easier comparison
    df = df.rename(columns={
        'solar azimuth (deg)': 'solar_azimuth',
        'solar elevation (deg)': 'solar_elevation',
        'solar radiation entering the water after shade and reflection (W/m^2)': 'solar_radiation',
        'longwave atmospheric radiation (W/m^2)': 'longwave_atmospheric',
        'longwave back radiation from water (W/m^2)': 'longwave_back',
        'convection (W/m^2)': 'convection',
        'evaporation (W/m^2)': 'evaporation',
        'sediment conduction heat flux to the surface water (W/m^2)': 'sediment_conduction',
        'hyporheic heat flux to the surface water (W/m^2)': 'hyporheic_exchange',
        'groundwater heat flux to the surface water (W/m^2)': 'groundwater',
        'air temperature (deg C)': 'air_temperature',
        'dewpoint temperature (deg C)': 'dewpoint_temperature',
        'response water temperature (deg C)': 'water_temperature',
        'response sediment temperature (deg C)': 'sediment_temperature',
    })
    
    return df


def main():
    """Run long-term validation."""
    
    print("=" * 80)
    print("LONG-TERM VBA VALIDATION")
    print("=" * 80)
    print()
    
    # Get file paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    fixtures_dir = os.path.join(script_dir, '..', 'fixtures')
    
    params_file = os.path.join(fixtures_dir, 'vba_params.csv')
    input_file = os.path.join(fixtures_dir, 'vba_ts_input.csv')
    output_file = os.path.join(fixtures_dir, 'vba_ts_output.csv')
    
    # Load data
    print("Loading VBA data...")
    params = parse_vba_params(params_file)
    met_data = load_vba_input_ts(input_file)
    vba_output = load_vba_output_ts(output_file)
    
    print(f"  Parameters: {len(params)} loaded")
    print(f"  Input time series: {len(met_data)} records")
    print(f"  VBA output time series: {len(vba_output)} records")
    print()
    
    # Display configuration
    print("Configuration:")
    print(f"  Location: {params['latitude']}°N, {params['longitude']}°W")
    print(f"  Elevation: {params['elevation']} m")
    print(f"  Water depth: {params['water_depth']} m")
    print(f"  Time period: {met_data['datetime'].iloc[0]} to {met_data['datetime'].iloc[-1]}")
    print(f"  Duration: {len(met_data)} timesteps ({len(met_data) * 15 / 60:.1f} hours)")
    print()
    
    # Create model configuration
    config = ModelConfiguration(
        latitude=params['latitude'],
        longitude=params['longitude'],
        elevation=params['elevation'],
        timezone=params['timezone'],
        daylight_savings=params['daylight_savings'],
        initial_water_temp=params['initial_water_temp'],
        initial_sediment_temp=params['initial_water_temp'],
        minimum_temperature=params['minimum_temperature'],
        water_depth=params['water_depth'],
        effective_shade=params['effective_shade'],
        wind_height=params['wind_height'],
        effective_wind_factor=params['effective_wind_factor'],
        sediment_thermal_conductivity=params['sediment_thermal_conductivity'],
        sediment_thermal_diffusivity=params['sediment_thermal_diffusivity'],
        sediment_thickness=params['sediment_thickness'],
        hyporheic_exchange_rate=params['hyporheic_exchange_rate'],
        groundwater_temperature=params['groundwater_temperature'],
        groundwater_inflow=params['groundwater_inflow'],
        solar_method=params['solar_method'],
        longwave_method=params['longwave_method'],
        wind_function_method=params['wind_function_method'],
        atmospheric_turbidity=params['atmospheric_turbidity'],
        atmospheric_transmission_coeff=params['atmospheric_transmission_coeff'],
        brutsaert_coefficient=params['brutsaert_coefficient'],
        solar_cloud_kcl1=params['solar_cloud_kcl1'],
        solar_cloud_kcl2=params['solar_cloud_kcl2'],
        longwave_cloud_method=params['longwave_cloud_method'],
        longwave_cloud_kcl3=params['longwave_cloud_kcl3'],
        longwave_cloud_kcl4=params['longwave_cloud_kcl4'],
        stability_criteria=params['stability_criteria'],
        enable_diagnostics=False,
    )
    
    # Run Python model
    print("Running Python rTemp model...")
    model = RTempModel(config)
    python_results = model.run(met_data)
    print(f"  Generated {len(python_results)} output records")
    print()
    
    # Export Python results
    output_csv = os.path.join(script_dir, 'long_term_python_output.csv')
    model.export_results(output_csv)
    print(f"Python results exported to: {output_csv}")
    print()
    
    # Compare results
    print("=" * 80)
    print("COMPARISON: Python vs VBA")
    print("=" * 80)
    print()
    
    # Key fields to compare
    comparison_fields = [
        ('solar_azimuth', 'Solar Azimuth (deg)'),
        ('solar_elevation', 'Solar Elevation (deg)'),
        ('solar_radiation', 'Solar Radiation (W/m²)'),
        ('longwave_atmospheric', 'Longwave Atmospheric (W/m²)'),
        ('longwave_back', 'Longwave Back (W/m²)'),
        ('convection', 'Convection (W/m²)'),
        ('evaporation', 'Evaporation (W/m²)'),
        ('sediment_conduction', 'Sediment Conduction (W/m²)'),
        ('water_temperature', 'Water Temperature (°C)'),
        ('sediment_temperature', 'Sediment Temperature (°C)'),
    ]
    
    print(f"Comparing {len(python_results)} timesteps:")
    print()
    
    # Calculate statistics for each field
    stats = []
    for field, label in comparison_fields:
        vba_vals = vba_output[field].values[:len(python_results)]
        python_vals = python_results[field].values[:len(vba_output)]
        
        diff = python_vals - vba_vals
        abs_diff = np.abs(diff)
        rel_diff = np.abs(diff / (vba_vals + 1e-10)) * 100
        
        stats.append({
            'field': label,
            'vba_mean': np.mean(vba_vals),
            'python_mean': np.mean(python_vals),
            'max_abs_diff': np.max(abs_diff),
            'mean_abs_diff': np.mean(abs_diff),
            'rmse': np.sqrt(np.mean(diff**2)),
            'max_rel_diff': np.max(rel_diff),
        })
        
        print(f"{label}:")
        print(f"  VBA mean:      {np.mean(vba_vals):10.4f}")
        print(f"  Python mean:   {np.mean(python_vals):10.4f}")
        print(f"  Max abs diff:  {np.max(abs_diff):10.4f}")
        print(f"  Mean abs diff: {np.mean(abs_diff):10.4f}")
        print(f"  RMSE:          {np.sqrt(np.mean(diff**2)):10.4f}")
        print(f"  Max rel diff:  {np.max(rel_diff):10.2f}%")
        print()
    
    # Summary table
    print("=" * 80)
    print("SUMMARY TABLE")
    print("=" * 80)
    print()
    print(f"{'Parameter':<30} {'Max Diff':>12} {'Mean Diff':>12} {'RMSE':>12} {'Max %':>10}")
    print("-" * 80)
    for s in stats:
        print(f"{s['field']:<30} {s['max_abs_diff']:12.4f} {s['mean_abs_diff']:12.4f} "
              f"{s['rmse']:12.4f} {s['max_rel_diff']:9.2f}%")
    print()
    
    # Time series plots data (for external plotting)
    print("=" * 80)
    print("KEY TIMESTEPS COMPARISON")
    print("=" * 80)
    print()
    
    # Show first, middle, and last timesteps
    key_indices = [0, len(python_results) // 2, len(python_results) - 1]
    
    for idx in key_indices:
        print(f"Timestep {idx + 1}: {python_results['datetime'].iloc[idx]}")
        print("-" * 80)
        for field, label in comparison_fields:
            vba_val = vba_output[field].iloc[idx]
            python_val = python_results[field].iloc[idx]
            diff = python_val - vba_val
            print(f"  {label:30s}  VBA: {vba_val:10.4f}  Python: {python_val:10.4f}  Diff: {diff:10.4f}")
        print()
    
    print("=" * 80)
    print("Validation Complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
