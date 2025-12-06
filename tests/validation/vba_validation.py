"""
VBA Validation Script - Compare Python rTemp with Original VBA Implementation

This script reads the sample data from the original VBA program and runs
the Python implementation with the same inputs to validate results.
"""

from datetime import datetime
import pandas as pd
import numpy as np

from rtemp import ModelConfiguration, RTempModel


def parse_vba_sample_file(filepath):
    """Parse the VBA sample data file to extract configuration and data."""
    
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    # Parse configuration parameters
    config_params = {}
    
    # Map line indices to parameter names (based on file structure)
    config_params['latitude'] = float(lines[1].split('\t')[1])
    config_params['longitude'] = float(lines[2].split('\t')[1])
    config_params['elevation'] = float(lines[3].split('\t')[1])
    config_params['timezone'] = float(lines[4].split('\t')[1])
    
    daylight_savings = lines[5].split('\t')[1].strip()
    config_params['daylight_savings'] = 1 if daylight_savings.lower() == 'yes' else 0
    
    config_params['initial_water_temp'] = float(lines[6].split('\t')[1])
    config_params['minimum_temperature'] = float(lines[7].split('\t')[1])
    config_params['water_depth'] = float(lines[8].split('\t')[1])
    config_params['effective_shade'] = float(lines[9].split('\t')[1])
    config_params['wind_height'] = float(lines[10].split('\t')[1])
    config_params['effective_wind_factor'] = float(lines[11].split('\t')[1])
    config_params['groundwater_temperature'] = float(lines[12].split('\t')[1])
    config_params['groundwater_inflow'] = float(lines[13].split('\t')[1])
    config_params['sediment_thermal_conductivity'] = float(lines[14].split('\t')[1])
    config_params['sediment_thermal_diffusivity'] = float(lines[15].split('\t')[1])
    config_params['sediment_thickness'] = float(lines[16].split('\t')[1])
    config_params['hyporheic_exchange_rate'] = float(lines[17].split('\t')[1])
    config_params['solar_method'] = lines[18].split('\t')[1].strip()
    config_params['atmospheric_turbidity'] = float(lines[19].split('\t')[1])
    config_params['atmospheric_transmission_coeff'] = float(lines[20].split('\t')[1])
    config_params['solar_cloud_kcl1'] = float(lines[21].split('\t')[1])
    config_params['solar_cloud_kcl2'] = float(lines[22].split('\t')[1])
    config_params['longwave_method'] = lines[23].split('\t')[1].strip()
    config_params['brutsaert_coefficient'] = float(lines[24].split('\t')[1])
    config_params['longwave_cloud_method'] = lines[25].split('\t')[1].strip()
    config_params['longwave_cloud_kcl3'] = float(lines[26].split('\t')[1])
    config_params['longwave_cloud_kcl4'] = float(lines[27].split('\t')[1])
    config_params['wind_function_method'] = lines[28].split('\t')[1].strip()
    config_params['stability_criteria'] = float(lines[29].split('\t')[1])
    
    # Find where meteorological data starts
    met_start_idx = None
    for i, line in enumerate(lines):
        if 'year\tmonth\tday\thour\tminute' in line:
            met_start_idx = i + 1
            break
    
    # Parse meteorological data
    met_data = []
    for i in range(met_start_idx, len(lines)):
        line = lines[i].strip()
        if not line or line.startswith('Input of water temperature') or line.startswith('station'):
            break
        
        parts = line.split('\t')
        if len(parts) >= 9:
            try:
                year = int(parts[0])
                month = int(parts[1])
                day = int(parts[2])
                hour = int(parts[3])
                minute = int(parts[4])
                air_temp = float(parts[5])
                dewpoint = float(parts[6])
                wind_speed = float(parts[7])
                cloud_cover = float(parts[8])
                
                dt = datetime(year, month, day, hour, minute)
                
                met_data.append({
                    'datetime': dt,
                    'air_temperature': air_temp,
                    'dewpoint_temperature': dewpoint,
                    'wind_speed': wind_speed,
                    'cloud_cover': cloud_cover,
                })
            except (ValueError, IndexError):
                continue
    
    # Find where VBA output starts
    vba_output_start = None
    for i, line in enumerate(lines):
        if 'date-time\tsolar azimuth' in line:
            vba_output_start = i + 1
            break
    
    # Parse VBA output for comparison
    vba_output = []
    if vba_output_start:
        for i in range(vba_output_start, len(lines)):
            line = lines[i].strip()
            if not line:
                break
            
            parts = line.split('\t')
            if len(parts) >= 15:
                try:
                    vba_output.append({
                        'datetime': parts[0],
                        'solar_azimuth': float(parts[1]),
                        'solar_elevation': float(parts[2]),
                        'potential_solar': float(parts[3]),
                        'solar_radiation': float(parts[4]),
                        'longwave_atmospheric': float(parts[5]),
                        'longwave_back': float(parts[6]),
                        'convection': float(parts[7]),
                        'evaporation': float(parts[8]),
                        'sediment_conduction': float(parts[9]),
                        'hyporheic_exchange': float(parts[10]),
                        'groundwater': float(parts[11]),
                        'air_temperature': float(parts[12]),
                        'dewpoint_temperature': float(parts[13]),
                        'water_temperature': float(parts[14]),
                        'sediment_temperature': float(parts[15]),
                    })
                except (ValueError, IndexError):
                    continue
    
    return config_params, pd.DataFrame(met_data), pd.DataFrame(vba_output)


def main():
    """Run validation against VBA sample data."""
    
    print("=" * 80)
    print("VBA Validation - Comparing Python rTemp with Original VBA Implementation")
    print("=" * 80)
    print()
    
    # Parse the VBA sample file
    print("Reading VBA sample data file...")
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sample_file = os.path.join(script_dir, '..', 'fixtures', 'vba_sample_data.txt')
    config_params, met_data, vba_output = parse_vba_sample_file(sample_file)
    print(f"  Configuration parameters: {len(config_params)}")
    print(f"  Meteorological records: {len(met_data)}")
    print(f"  VBA output records: {len(vba_output)}")
    print()
    
    # Display configuration
    print("Configuration from VBA file:")
    print(f"  Location: {config_params['latitude']}°N, {config_params['longitude']}°W")
    print(f"  Elevation: {config_params['elevation']} m")
    print(f"  Water depth: {config_params['water_depth']} m")
    print(f"  Effective shade: {config_params['effective_shade']}")
    print(f"  Solar method: {config_params['solar_method']}")
    print(f"  Longwave method: {config_params['longwave_method']}")
    print(f"  Wind function: {config_params['wind_function_method']}")
    print(f"  Brutsaert coefficient: {config_params['brutsaert_coefficient']}")
    print(f"  Solar KCL1: {config_params['solar_cloud_kcl1']}")
    print(f"  Solar KCL2: {config_params['solar_cloud_kcl2']}")
    print(f"  Longwave cloud method: {config_params['longwave_cloud_method']}")
    print(f"  Longwave KCL3: {config_params['longwave_cloud_kcl3']}")
    print(f"  Longwave KCL4: {config_params['longwave_cloud_kcl4']}")
    print()
    
    # Create model configuration
    config = ModelConfiguration(
        latitude=config_params['latitude'],
        longitude=config_params['longitude'],
        elevation=config_params['elevation'],
        timezone=config_params['timezone'],
        daylight_savings=config_params['daylight_savings'],
        initial_water_temp=config_params['initial_water_temp'],
        initial_sediment_temp=config_params['initial_water_temp'],  # VBA uses same initial temp
        minimum_temperature=config_params['minimum_temperature'],
        water_depth=config_params['water_depth'],
        effective_shade=config_params['effective_shade'],
        wind_height=config_params['wind_height'],
        effective_wind_factor=config_params['effective_wind_factor'],
        sediment_thermal_conductivity=config_params['sediment_thermal_conductivity'],
        sediment_thermal_diffusivity=config_params['sediment_thermal_diffusivity'],
        sediment_thickness=config_params['sediment_thickness'],
        hyporheic_exchange_rate=config_params['hyporheic_exchange_rate'],
        groundwater_temperature=config_params['groundwater_temperature'],
        groundwater_inflow=config_params['groundwater_inflow'],
        solar_method=config_params['solar_method'],
        longwave_method=config_params['longwave_method'],
        wind_function_method=config_params['wind_function_method'],
        atmospheric_turbidity=config_params['atmospheric_turbidity'],
        atmospheric_transmission_coeff=config_params['atmospheric_transmission_coeff'],
        brutsaert_coefficient=config_params['brutsaert_coefficient'],
        solar_cloud_kcl1=config_params['solar_cloud_kcl1'],
        solar_cloud_kcl2=config_params['solar_cloud_kcl2'],
        longwave_cloud_method=config_params['longwave_cloud_method'],
        longwave_cloud_kcl3=config_params['longwave_cloud_kcl3'],
        longwave_cloud_kcl4=config_params['longwave_cloud_kcl4'],
        stability_criteria=config_params['stability_criteria'],
        enable_diagnostics=False,
    )
    
    # Run Python model
    print("Running Python rTemp model...")
    model = RTempModel(config)
    print(f"  Model config KCL3: {model.config.longwave_cloud_kcl3}")
    print(f"  Model config KCL4: {model.config.longwave_cloud_kcl4}")
    python_results = model.run(met_data)
    print(f"  Generated {len(python_results)} output records")
    print()
    
    # Python and VBA both store longwave_back as negative (heat loss)
    # No adjustment needed
    python_results_adjusted = python_results.copy()
    
    # Compare results
    print("=" * 80)
    print("COMPARISON: Python vs VBA")
    print("=" * 80)
    print()
    print("Note: Python and VBA use same sign conventions (longwave_back is negative)")
    print()
    
    if len(vba_output) > 0:
        # Compare key outputs
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
        
        print(f"Comparing first {min(len(vba_output), len(python_results))} timesteps:")
        print()
        
        for field, label in comparison_fields:
            vba_vals = vba_output[field].values[:len(python_results_adjusted)]
            python_vals = python_results_adjusted[field].values[:len(vba_output)]
            
            # Calculate differences
            diff = python_vals - vba_vals
            abs_diff = np.abs(diff)
            rel_diff = np.abs(diff / (vba_vals + 1e-10)) * 100  # Avoid division by zero
            
            print(f"{label}:")
            print(f"  VBA mean:    {np.mean(vba_vals):10.4f}")
            print(f"  Python mean: {np.mean(python_vals):10.4f}")
            print(f"  Max abs diff: {np.max(abs_diff):9.4f}")
            print(f"  Mean abs diff: {np.mean(abs_diff):8.4f}")
            print(f"  Max rel diff: {np.max(rel_diff):9.2f}%")
            print()
        
        # Detailed comparison table for first few timesteps
        print("=" * 80)
        print("DETAILED COMPARISON - First 3 Timesteps")
        print("=" * 80)
        print()
        
        for i in range(min(3, len(vba_output), len(python_results_adjusted))):
            print(f"Timestep {i+1}: {vba_output['datetime'].iloc[i]}")
            print("-" * 80)
            
            for field, label in comparison_fields:
                vba_val = vba_output[field].iloc[i]
                python_val = python_results_adjusted[field].iloc[i]
                diff = python_val - vba_val
                
                print(f"  {label:30s}  VBA: {vba_val:10.4f}  Python: {python_val:10.4f}  Diff: {diff:10.4f}")
            print()
    
    # Export results
    output_file = os.path.join(script_dir, "vba_validation_output.csv")
    model.export_results(output_file)
    print(f"Python results exported to: {output_file}")
    print()
    
    print("=" * 80)
    print("Validation Complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
