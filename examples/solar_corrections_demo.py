"""
Demonstration of solar radiation corrections.

This example shows how to use the solar radiation corrections module
to apply cloud cover, shade, and albedo corrections to calculated
solar radiation values.
"""

from rtemp.solar.corrections import SolarRadiationCorrections
from rtemp.solar.radiation_bras import SolarRadiationBras


def main():
    """Demonstrate solar radiation corrections."""
    
    print("=" * 70)
    print("Solar Radiation Corrections Demonstration")
    print("=" * 70)
    print()
    
    # Calculate base solar radiation using Bras method
    solar_elevation = 45.0  # degrees
    earth_sun_distance = 1.0  # AU
    turbidity = 2.0
    
    base_radiation = SolarRadiationBras.calculate(
        elevation=solar_elevation,
        earth_sun_distance=earth_sun_distance,
        turbidity=turbidity
    )
    
    print(f"Base solar radiation (Bras method):")
    print(f"  Solar elevation: {solar_elevation}°")
    print(f"  Earth-Sun distance: {earth_sun_distance} AU")
    print(f"  Turbidity: {turbidity}")
    print(f"  Calculated radiation: {base_radiation:.2f} W/m²")
    print()
    
    # Example 1: Cloud cover correction
    print("-" * 70)
    print("Example 1: Cloud Cover Correction")
    print("-" * 70)
    
    for cloud_cover in [0.0, 0.25, 0.5, 0.75, 1.0]:
        corrected = SolarRadiationCorrections.apply_cloud_correction(
            base_radiation,
            cloud_cover=cloud_cover,
            kcl1=1.0,
            kcl2=2.0
        )
        reduction = (1.0 - corrected / base_radiation) * 100
        print(f"  Cloud cover {cloud_cover:4.2f}: {corrected:7.2f} W/m² "
              f"({reduction:5.1f}% reduction)")
    print()
    
    # Example 2: Shade correction
    print("-" * 70)
    print("Example 2: Shade Correction")
    print("-" * 70)
    
    for shade in [0.0, 0.25, 0.5, 0.75, 1.0]:
        corrected = SolarRadiationCorrections.apply_shade_correction(
            base_radiation,
            effective_shade=shade
        )
        reduction = (1.0 - corrected / base_radiation) * 100
        print(f"  Effective shade {shade:4.2f}: {corrected:7.2f} W/m² "
              f"({reduction:5.1f}% reduction)")
    print()
    
    # Example 3: Anderson albedo calculation
    print("-" * 70)
    print("Example 3: Anderson Albedo (Surface Reflection)")
    print("-" * 70)
    
    cloud_cover = 0.0
    print(f"  Cloud cover: {cloud_cover}")
    print()
    
    for elevation in [10, 20, 30, 45, 60, 90]:
        albedo = SolarRadiationCorrections.calculate_anderson_albedo(
            cloud_cover=cloud_cover,
            solar_elevation=elevation
        )
        absorbed = SolarRadiationCorrections.apply_albedo_correction(
            base_radiation,
            albedo=albedo
        )
        reflection = (1.0 - absorbed / base_radiation) * 100
        print(f"  Solar elevation {elevation:2d}°: albedo={albedo:.4f}, "
              f"absorbed={absorbed:7.2f} W/m² ({reflection:5.2f}% reflected)")
    print()
    
    # Example 4: All corrections combined
    print("-" * 70)
    print("Example 4: All Corrections Combined")
    print("-" * 70)
    
    cloud_cover = 0.5
    effective_shade = 0.3
    solar_elevation = 30.0
    
    result = SolarRadiationCorrections.apply_all_corrections(
        solar_radiation=base_radiation,
        cloud_cover=cloud_cover,
        effective_shade=effective_shade,
        solar_elevation=solar_elevation,
        kcl1=1.0,
        kcl2=2.0,
        use_anderson_albedo=True
    )
    
    print(f"  Input conditions:")
    print(f"    Cloud cover: {cloud_cover}")
    print(f"    Effective shade: {effective_shade}")
    print(f"    Solar elevation: {solar_elevation}°")
    print()
    print(f"  Correction sequence:")
    print(f"    Original radiation:      {result['original']:7.2f} W/m²")
    print(f"    After cloud correction:  {result['after_cloud']:7.2f} W/m² "
          f"({(1 - result['after_cloud']/result['original'])*100:5.1f}% reduction)")
    print(f"    After shade correction:  {result['after_shade']:7.2f} W/m² "
          f"({(1 - result['after_shade']/result['original'])*100:5.1f}% reduction)")
    print(f"    Calculated albedo:       {result['albedo']:.4f}")
    print(f"    Final absorbed radiation: {result['final']:7.2f} W/m² "
          f"({(1 - result['final']/result['original'])*100:5.1f}% total reduction)")
    print()
    
    # Example 5: Effect of cloud cover on albedo
    print("-" * 70)
    print("Example 5: Cloud Cover Effect on Albedo")
    print("-" * 70)
    
    solar_elevation = 15.0  # Low sun
    print(f"  Solar elevation: {solar_elevation}° (low sun)")
    print()
    
    for cloud_cover in [0.0, 0.5, 1.0]:
        albedo = SolarRadiationCorrections.calculate_anderson_albedo(
            cloud_cover=cloud_cover,
            solar_elevation=solar_elevation
        )
        print(f"  Cloud cover {cloud_cover:4.2f}: albedo={albedo:.4f}")
    print()
    
    print("=" * 70)
    print("Demonstration complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
