"""
Environment Validation Script for GoldSim-rTemp Integration

This script validates that your environment is correctly configured for running
the GoldSim-rTemp integration. It checks Python version, required packages,
file presence, and performs a test execution of the adapter.

Usage:
    py -3.11 validate_environment.py
    or
    py -3.14 validate_environment.py

Requirements: 6.6, 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 12.6
"""

import sys
import os
import json
from pathlib import Path


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_check(passed, message):
    """Print a check result."""
    status = "✓" if passed else "✗"
    color = "\033[92m" if passed else "\033[91m"
    reset = "\033[0m"
    print(f"{color}{status}{reset} {message}")


def check_python_version():
    """Check Python version compatibility."""
    print_header("Python Version Check")
    
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    print(f"Python version: {version_str}")
    print(f"Architecture: {sys.maxsize.bit_length() + 1}-bit")
    
    # Check version
    is_correct_version = (version.major == 3 and version.minor in [11, 14])
    print_check(is_correct_version, 
                f"Python version is 3.11 or 3.14 (required by GSPy v1.8.8)")
    
    # Check architecture
    is_64bit = sys.maxsize > 2**32
    print_check(is_64bit, "Python is 64-bit (required by GoldSim)")
    
    return is_correct_version and is_64bit


def check_packages():
    """Check required Python packages."""
    print_header("Required Packages Check")
    
    required_packages = {
        'numpy': 'NumPy',
        'pandas': 'Pandas',
        'scipy': 'SciPy',
        'rtemp': 'rTemp'
    }
    
    all_installed = True
    
    for package_name, display_name in required_packages.items():
        try:
            module = __import__(package_name)
            version = getattr(module, '__version__', 'unknown')
            print_check(True, f"{display_name} installed (version {version})")
        except ImportError:
            print_check(False, f"{display_name} NOT installed")
            all_installed = False
    
    if not all_installed:
        print("\nTo install missing packages, run:")
        print(f"  py -{sys.version_info.major}.{sys.version_info.minor} -m pip install numpy pandas scipy rtemp")
    
    return all_installed


def check_files():
    """Check required files are present."""
    print_header("Required Files Check")
    
    required_files = {
        'rtemp_goldsim_adapter.py': 'Python adapter script',
        'rtemp_adapter.json': 'GSPy configuration file',
    }
    
    optional_files = {
        'rtemp_adapter.dll': 'GSPy DLL (renamed from GSPy_Release_py3XX.dll)',
    }
    
    all_present = True
    
    for filename, description in required_files.items():
        exists = Path(filename).exists()
        print_check(exists, f"{description}: {filename}")
        if not exists:
            all_present = False
    
    for filename, description in optional_files.items():
        exists = Path(filename).exists()
        if exists:
            print_check(True, f"{description}: {filename}")
        else:
            print(f"  ⚠ {description} not found (required for GoldSim execution)")
    
    return all_present


def check_json_config():
    """Validate JSON configuration file."""
    print_header("JSON Configuration Check")
    
    json_file = 'rtemp_adapter.json'
    
    if not Path(json_file).exists():
        print_check(False, f"{json_file} not found")
        return False
    
    try:
        with open(json_file, 'r') as f:
            config = json.load(f)
        
        print_check(True, "JSON file is valid")
        
        # Check required fields
        required_fields = ['python_path', 'script_path', 'function_name', 'log_level', 'inputs', 'outputs']
        all_fields_present = True
        
        for field in required_fields:
            present = field in config
            print_check(present, f"Field '{field}' present")
            if not present:
                all_fields_present = False
        
        if not all_fields_present:
            return False
        
        # Check input count
        input_count = len(config.get('inputs', []))
        correct_inputs = input_count == 14
        print_check(correct_inputs, f"Input count: {input_count} (expected 14)")
        
        # Check output count
        output_count = len(config.get('outputs', []))
        correct_outputs = output_count == 3
        print_check(correct_outputs, f"Output count: {output_count} (expected 3)")
        
        # Check python_path
        python_path = config.get('python_path', '')
        if 'YourUsername' in python_path:
            print_check(False, "python_path contains placeholder 'YourUsername' - needs to be updated")
            print(f"  Current value: {python_path}")
            print(f"  Suggested value: {sys.prefix}")
            return False
        else:
            print_check(True, f"python_path configured: {python_path}")
        
        # Check function_name
        function_name = config.get('function_name', '')
        correct_function = function_name == 'process_data'
        print_check(correct_function, f"function_name: {function_name} (expected 'process_data')")
        
        return correct_inputs and correct_outputs and correct_function
        
    except json.JSONDecodeError as e:
        print_check(False, f"JSON parsing error: {e}")
        return False
    except Exception as e:
        print_check(False, f"Error reading JSON: {e}")
        return False


def check_adapter_syntax():
    """Check adapter script syntax."""
    print_header("Adapter Script Syntax Check")
    
    adapter_file = 'rtemp_goldsim_adapter.py'
    
    if not Path(adapter_file).exists():
        print_check(False, f"{adapter_file} not found")
        return False
    
    try:
        with open(adapter_file, 'r') as f:
            code = f.read()
        
        compile(code, adapter_file, 'exec')
        print_check(True, "Adapter script syntax is valid")
        
        # Check for REFERENCE_DATE
        if 'REFERENCE_DATE' in code:
            print_check(True, "REFERENCE_DATE constant found")
            
            # Check if it's still the default
            if 'datetime(2024, 1, 1)' in code:
                print("  ⚠ REFERENCE_DATE is set to default (2024-01-01)")
                print("    Make sure this matches your GoldSim simulation start date!")
        else:
            print_check(False, "REFERENCE_DATE constant not found")
            return False
        
        # Check for process_data function
        if 'def process_data(' in code:
            print_check(True, "process_data() function found")
        else:
            print_check(False, "process_data() function not found")
            return False
        
        return True
        
    except SyntaxError as e:
        print_check(False, f"Syntax error: {e}")
        return False
    except Exception as e:
        print_check(False, f"Error reading adapter: {e}")
        return False


def test_adapter_execution():
    """Test adapter execution with sample data."""
    print_header("Adapter Execution Test")
    
    adapter_file = 'rtemp_goldsim_adapter.py'
    
    if not Path(adapter_file).exists():
        print_check(False, f"{adapter_file} not found")
        return False
    
    try:
        # Import the adapter module
        import importlib.util
        spec = importlib.util.spec_from_file_location("adapter", adapter_file)
        adapter = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(adapter)
        
        print_check(True, "Adapter module imported successfully")
        
        # Test with sample data
        print("\nTesting with sample data...")
        
        # Sample inputs (14 parameters)
        test_args = (
            15.0,   # Current_Water_Temp (°C)
            15.0,   # Current_Sediment_Temp (°C)
            1.0,    # Water_Depth (meters)
            45.0,   # Latitude (degrees)
            -120.0, # Longitude (degrees)
            100.0,  # Elevation (meters)
            8.0,    # Timezone (hours from UTC)
            10.0,   # Air_Temp_Min (°C)
            25.0,   # Air_Temp_Max (°C)
            5.0,    # Dewpoint_Min (°C)
            15.0,   # Dewpoint_Max (°C)
            3.0,    # Wind_Speed_Avg (m/s)
            0.3,    # Cloud_Cover_Avg (fraction)
            0.0     # Simulation_Date (days)
        )
        
        # Execute adapter
        result = adapter.process_data(*test_args)
        
        print_check(True, "Adapter executed without errors")
        
        # Check result structure
        if isinstance(result, tuple) and len(result) == 3:
            print_check(True, f"Result is a 3-tuple: {result}")
            
            new_water_temp, new_sediment_temp, daily_avg_net_flux = result
            
            # Check result types
            all_floats = all(isinstance(x, (int, float)) for x in result)
            print_check(all_floats, "All outputs are numeric")
            
            # Check result ranges
            temp_valid = -5 <= new_water_temp <= 50 and -5 <= new_sediment_temp <= 50
            print_check(temp_valid, f"Temperatures in valid range: "
                       f"T_water={new_water_temp:.2f}°C, T_sed={new_sediment_temp:.2f}°C")
            
            flux_reasonable = -500 <= daily_avg_net_flux <= 1000
            print_check(flux_reasonable, f"Net flux reasonable: {daily_avg_net_flux:.1f} W/m²")
            
            return all_floats and temp_valid and flux_reasonable
        else:
            print_check(False, f"Result is not a 3-tuple: {result}")
            return False
        
    except Exception as e:
        print_check(False, f"Execution error: {e}")
        import traceback
        print("\nFull traceback:")
        print(traceback.format_exc())
        return False


def test_dry_bed_logic():
    """Test dry-bed bypass logic."""
    print_header("Dry-Bed Logic Test")
    
    adapter_file = 'rtemp_goldsim_adapter.py'
    
    if not Path(adapter_file).exists():
        print_check(False, f"{adapter_file} not found")
        return False
    
    try:
        # Import the adapter module
        import importlib.util
        spec = importlib.util.spec_from_file_location("adapter", adapter_file)
        adapter = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(adapter)
        
        # Test with dry-bed condition (depth = 0.005 m, below threshold of 0.01 m)
        test_args = (
            20.0,   # Current_Water_Temp (°C)
            18.0,   # Current_Sediment_Temp (°C)
            0.005,  # Water_Depth (meters) - DRY BED
            45.0,   # Latitude
            -120.0, # Longitude
            100.0,  # Elevation
            8.0,    # Timezone
            10.0,   # Air_Temp_Min
            25.0,   # Air_Temp_Max
            5.0,    # Dewpoint_Min
            15.0,   # Dewpoint_Max
            3.0,    # Wind_Speed_Avg
            0.3,    # Cloud_Cover_Avg
            0.0     # Simulation_Date
        )
        
        result = adapter.process_data(*test_args)
        
        new_water_temp, new_sediment_temp, daily_avg_net_flux = result
        
        # Check dry-bed behavior
        water_temp_preserved = abs(new_water_temp - 20.0) < 0.01
        print_check(water_temp_preserved, 
                   f"Water temperature preserved: {new_water_temp:.2f}°C (expected 20.0°C)")
        
        expected_sediment = (10.0 + 25.0) / 2.0  # Mean of air temp
        sediment_correct = abs(new_sediment_temp - expected_sediment) < 0.01
        print_check(sediment_correct,
                   f"Sediment temperature = mean air temp: {new_sediment_temp:.2f}°C "
                   f"(expected {expected_sediment:.2f}°C)")
        
        flux_zero = abs(daily_avg_net_flux) < 0.01
        print_check(flux_zero, f"Net flux is zero: {daily_avg_net_flux:.4f} W/m²")
        
        return water_temp_preserved and sediment_correct and flux_zero
        
    except Exception as e:
        print_check(False, f"Dry-bed test error: {e}")
        return False


def main():
    """Run all validation checks."""
    print("\n" + "=" * 70)
    print("  GoldSim-rTemp Integration Environment Validation")
    print("=" * 70)
    print("\nThis script validates your environment for running the GoldSim-rTemp")
    print("integration. It checks Python version, packages, files, and performs")
    print("test executions of the adapter.")
    
    results = {}
    
    # Run all checks
    results['python'] = check_python_version()
    results['packages'] = check_packages()
    results['files'] = check_files()
    results['json'] = check_json_config()
    results['syntax'] = check_adapter_syntax()
    
    # Only run execution tests if basic checks pass
    if results['python'] and results['packages'] and results['files'] and results['syntax']:
        results['execution'] = test_adapter_execution()
        results['dry_bed'] = test_dry_bed_logic()
    else:
        results['execution'] = False
        results['dry_bed'] = False
        print("\n⚠ Skipping execution tests due to failed basic checks")
    
    # Summary
    print_header("Validation Summary")
    
    all_passed = all(results.values())
    
    for check_name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print_check(passed, f"{check_name.replace('_', ' ').title()}: {status}")
    
    print("\n" + "=" * 70)
    if all_passed:
        print("  ✓ All checks passed! Environment is ready for GoldSim integration.")
    else:
        print("  ✗ Some checks failed. Please fix the issues above.")
    print("=" * 70)
    
    # Exit with appropriate code
    sys.exit(0 if all_passed else 1)


if __name__ == '__main__':
    main()
