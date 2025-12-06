"""
Detailed investigation of solar radiation differences between Python and VBA.
Compares step-by-step calculations at key times.
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime

from rtemp.solar.position import NOAASolarPosition
from rtemp.solar.radiation_bras import SolarRadiationBras
from rtemp.solar.corrections import SolarRadiationCorrections


def investigate_timestep(dt, vba_data, met_data, config_params):
    """Investigate a single timestep in detail."""
    
    print("=" * 80)
    print(f"TIMESTEP: {dt}")
    print("=" * 80)
    print()
    
    # VBA values
    vba_elevation = vba_data['solar elevation (deg)']
    vba_potential = vba_data['potential solar radiation at the ground surface before shade and reflection (W/m^2)']
    vba_final = vba_data['solar radiation entering the water after shade and reflection (W/m^2)']
    cloud_cover = met_data['cloud cover (fraction)']
    
    print(f"VBA Values:")
    print(f"  Solar Elevation: {vba_elevation:.2f}°")
    print(f"  Potential Solar: {vba_potential:.2f} W/m²")
    print(f"  Final Solar (after corrections): {vba_final:.2f} W/m²")
    print(f"  Cloud Cover: {cloud_cover:.2f}")
    print()
    
    # Python solar position
    azimuth, elevation, distance = NOAASolarPosition.calc_solar_position(
        lat=config_params['latitude'],
        lon=config_params['longitude'],
        dt=dt,
        timezone=config_params['timezone'],
        dlstime=config_params['daylight_savings']
    )
    
    print(f"Python Solar Position:")
    print(f"  Elevation: {elevation:.2f}°")
    print(f"  Distance: {distance:.6f} AU")
    print(f"  Elevation difference from VBA: {elevation - vba_elevation:.2f}°")
    print()
    
    if elevation <= 0:
        print("Sun below horizon - no solar radiation")
        print()
        return
    
    # Python potential solar (Bras method)
    potential_solar = SolarRadiationBras.calculate(
        elevation=elevation,
        earth_sun_distance=distance,
        turbidity=config_params['atmospheric_turbidity']
    )
    
    print(f"Python Potential Solar (Bras):")
    print(f"  Calculated: {potential_solar:.2f} W/m²")
    print(f"  Difference from VBA: {potential_solar - vba_potential:.2f} W/m² ({(potential_solar - vba_potential) / vba_potential * 100:.1f}%)")
    print()
    
    # Apply corrections step by step
    print("Python Corrections:")
    
    # 1. Cloud correction
    solar_after_cloud = SolarRadiationCorrections.apply_cloud_correction(
        potential_solar, cloud_cover, 
        kcl1=config_params['solar_cloud_kcl1'], 
        kcl2=config_params['solar_cloud_kcl2']
    )
    cloud_factor = solar_after_cloud / potential_solar if potential_solar > 0 else 0
    print(f"  1. Cloud correction (cover={cloud_cover:.2f}):")
    print(f"     Factor: {cloud_factor:.4f}")
    print(f"     Result: {solar_after_cloud:.2f} W/m²")
    
    # 2. Shade correction
    solar_after_shade = SolarRadiationCorrections.apply_shade_correction(
        solar_after_cloud, 
        effective_shade=config_params['effective_shade']
    )
    shade_factor = solar_after_shade / solar_after_cloud if solar_after_cloud > 0 else 0
    print(f"  2. Shade correction (shade={config_params['effective_shade']:.2f}):")
    print(f"     Factor: {shade_factor:.4f}")
    print(f"     Result: {solar_after_shade:.2f} W/m²")
    
    # 3. Albedo correction
    albedo = SolarRadiationCorrections.calculate_anderson_albedo(elevation, cloud_cover)
    solar_final = SolarRadiationCorrections.apply_albedo_correction(solar_after_shade, albedo)
    albedo_factor = solar_final / solar_after_shade if solar_after_shade > 0 else 0
    print(f"  3. Albedo correction:")
    print(f"     Albedo: {albedo:.4f}")
    print(f"     Factor: {albedo_factor:.4f}")
    print(f"     Result: {solar_final:.2f} W/m²")
    print()
    
    # Calculate VBA correction factors
    if vba_potential > 0:
        vba_total_factor = vba_final / vba_potential
        print(f"VBA Total Correction Factor: {vba_total_factor:.4f}")
        print(f"Python Total Correction Factor: {solar_final / potential_solar:.4f}")
        print()
    
    # Final comparison
    print("FINAL COMPARISON:")
    print(f"  VBA Final:    {vba_final:.2f} W/m²")
    print(f"  Python Final: {solar_final:.2f} W/m²")
    print(f"  Difference:   {solar_final - vba_final:.2f} W/m² ({(solar_final - vba_final) / vba_final * 100 if vba_final > 0 else 0:.1f}%)")
    print()
    
    # Diagnose the issue
    print("DIAGNOSIS:")
    if abs(potential_solar - vba_potential) > 50:
        print(f"  ⚠️  POTENTIAL SOLAR MISMATCH: {potential_solar - vba_potential:.2f} W/m²")
        print(f"      Python Bras formula may be incorrect")
    
    if vba_potential > 0:
        python_factor = solar_final / potential_solar
        vba_factor = vba_final / vba_potential
        if abs(python_factor - vba_factor) > 0.1:
            print(f"  ⚠️  CORRECTION FACTOR MISMATCH:")
            print(f"      VBA applies {vba_factor:.4f} total correction")
            print(f"      Python applies {python_factor:.4f} total correction")
    
    print()


def main():
    """Run detailed solar radiation investigation."""
    
    print("=" * 80)
    print("SOLAR RADIATION INVESTIGATION")
    print("=" * 80)
    print()
    
    # Load data
    script_dir = os.path.dirname(os.path.abspath(__file__))
    fixtures_dir = os.path.join(script_dir, '..', 'fixtures')
    
    vba_output = pd.read_csv(os.path.join(fixtures_dir, 'vba_ts_output.csv'), skiprows=1)
    vba_output['datetime'] = pd.to_datetime(vba_output['date-time'])
    
    vba_input = pd.read_csv(os.path.join(fixtures_dir, 'vba_ts_input.csv'), skiprows=1)
    vba_input['datetime'] = pd.to_datetime(
        vba_input[['year', 'month', 'day', 'hour', 'minute']].rename(columns={
            'year': 'year', 'month': 'month', 'day': 'day',
            'hour': 'hour', 'minute': 'minute'
        })
    )
    
    # Configuration
    config_params = {
        'latitude': 48.45,
        'longitude': -122.33,
        'timezone': -8.0,
        'daylight_savings': 0,
        'effective_shade': 0.15,
        'atmospheric_turbidity': 2.0,
        'solar_cloud_kcl1': 0.65,
        'solar_cloud_kcl2': 2.0,
    }
    
    # Key times to investigate
    times_to_check = [
        datetime(2003, 10, 1, 9, 15),   # Morning - Python too high
        datetime(2003, 10, 1, 12, 0),   # Noon - moderate difference
        datetime(2003, 10, 1, 15, 0),   # Afternoon - Python too low (max diff)
        datetime(2003, 10, 1, 18, 0),   # Sunset - Python cuts off
    ]
    
    for dt in times_to_check:
        vba_row = vba_output[vba_output['datetime'] == dt].iloc[0]
        met_row = vba_input[vba_input['datetime'] == dt].iloc[0]
        
        investigate_timestep(dt, vba_row, met_row, config_params)
    
    # Summary analysis
    print("=" * 80)
    print("SUMMARY ANALYSIS")
    print("=" * 80)
    print()
    
    # Filter to daytime only
    daytime_mask = vba_output['solar radiation entering the water after shade and reflection (W/m^2)'] > 0
    vba_daytime = vba_output[daytime_mask].head(20)  # First 20 daytime timesteps
    
    print("Analyzing first 20 daytime timesteps...")
    print()
    
    potential_diffs = []
    final_diffs = []
    
    for idx, row in vba_daytime.iterrows():
        dt = row['datetime']
        vba_potential = row['potential solar radiation at the ground surface before shade and reflection (W/m^2)']
        vba_final = row['solar radiation entering the water after shade and reflection (W/m^2)']
        
        # Calculate Python values
        azimuth, elevation, distance = NOAASolarPosition.calc_solar_position(
            lat=48.45, lon=-122.33, dt=dt, timezone=-8.0, dlstime=0
        )
        
        if elevation > 0:
            python_potential = SolarRadiationBras.calculate(elevation, distance, turbidity=2.0)
            
            # Apply all corrections
            met_row = vba_input[vba_input['datetime'] == dt].iloc[0]
            cloud_cover = met_row['cloud cover (fraction)']
            
            solar_temp = SolarRadiationCorrections.apply_cloud_correction(python_potential, cloud_cover, 0.65, 2.0)
            solar_temp = SolarRadiationCorrections.apply_shade_correction(solar_temp, 0.15)
            albedo = SolarRadiationCorrections.calculate_anderson_albedo(elevation, cloud_cover)
            python_final = SolarRadiationCorrections.apply_albedo_correction(solar_temp, albedo)
            
            potential_diffs.append(python_potential - vba_potential)
            final_diffs.append(python_final - vba_final)
    
    print(f"Potential Solar Differences:")
    print(f"  Mean: {np.mean(potential_diffs):.2f} W/m²")
    print(f"  Std:  {np.std(potential_diffs):.2f} W/m²")
    print(f"  Min:  {np.min(potential_diffs):.2f} W/m²")
    print(f"  Max:  {np.max(potential_diffs):.2f} W/m²")
    print()
    
    print(f"Final Solar Differences:")
    print(f"  Mean: {np.mean(final_diffs):.2f} W/m²")
    print(f"  Std:  {np.std(final_diffs):.2f} W/m²")
    print(f"  Min:  {np.min(final_diffs):.2f} W/m²")
    print(f"  Max:  {np.max(final_diffs):.2f} W/m²")
    print()
    
    print("=" * 80)
    print("CONCLUSION")
    print("=" * 80)
    print()
    
    if np.mean(potential_diffs) > 50:
        print("PRIMARY ISSUE: Python's Bras formula calculates MUCH HIGHER potential solar")
        print("               radiation than VBA. This is the root cause.")
        print()
        print("RECOMMENDATION: Review the Bras formula implementation in")
        print("                rtemp/solar/radiation_bras.py")
    elif abs(np.mean(final_diffs)) > 20:
        print("PRIMARY ISSUE: Correction factors (cloud/shade/albedo) are being")
        print("               applied differently than VBA.")
        print()
        print("RECOMMENDATION: Review correction implementations in")
        print("                rtemp/solar/corrections.py")
    else:
        print("No clear systematic issue identified. Differences may be due to")
        print("cumulative effects or edge cases.")


if __name__ == "__main__":
    main()
