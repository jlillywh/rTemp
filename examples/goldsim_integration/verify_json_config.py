"""
Verification script for GSPy JSON configuration.

This script validates that the rtemp_adapter.json configuration matches
the process_data function signature in rtemp_goldsim_adapter.py.
"""

import json

def verify_json_config():
    """Verify the JSON configuration matches requirements."""
    
    # Load JSON configuration
    with open('rtemp_adapter.json', 'r') as f:
        config = json.load(f)
    
    print("=" * 70)
    print("GSPy JSON Configuration Verification")
    print("=" * 70)
    
    # Verify required fields
    required_fields = ['python_path', 'script_path', 'function_name', 'log_level', 'inputs', 'outputs']
    for field in required_fields:
        if field not in config:
            print(f"❌ FAIL: Missing required field '{field}'")
            return False
        else:
            print(f"✓ Field '{field}' present")
    
    print()
    
    # Verify script_path
    expected_script = "rtemp_goldsim_adapter.py"
    if config['script_path'] == expected_script:
        print(f"✓ script_path: {config['script_path']}")
    else:
        print(f"❌ FAIL: script_path is '{config['script_path']}', expected '{expected_script}'")
        return False
    
    # Verify function_name
    expected_function = "process_data"
    if config['function_name'] == expected_function:
        print(f"✓ function_name: {config['function_name']}")
    else:
        print(f"❌ FAIL: function_name is '{config['function_name']}', expected '{expected_function}'")
        return False
    
    # Verify log_level
    expected_log_level = 2
    if config['log_level'] == expected_log_level:
        print(f"✓ log_level: {config['log_level']} (INFO)")
    else:
        print(f"❌ FAIL: log_level is {config['log_level']}, expected {expected_log_level}")
        return False
    
    print()
    
    # Verify inputs array
    expected_inputs = [
        "Current_Water_Temp",
        "Current_Sediment_Temp",
        "Water_Depth",
        "Latitude",
        "Longitude",
        "Elevation",
        "Timezone",
        "Air_Temp_Min",
        "Air_Temp_Max",
        "Dewpoint_Min",
        "Dewpoint_Max",
        "Wind_Speed_Avg",
        "Cloud_Cover_Avg",
        "Simulation_Date"
    ]
    
    print(f"Input Parameters ({len(config['inputs'])} total):")
    print("-" * 70)
    
    if len(config['inputs']) != len(expected_inputs):
        print(f"❌ FAIL: Expected {len(expected_inputs)} inputs, got {len(config['inputs'])}")
        return False
    
    for i, (input_spec, expected_name) in enumerate(zip(config['inputs'], expected_inputs)):
        if input_spec['name'] != expected_name:
            print(f"❌ FAIL: Input {i} name is '{input_spec['name']}', expected '{expected_name}'")
            return False
        if input_spec['type'] != 'scalar':
            print(f"❌ FAIL: Input {i} type is '{input_spec['type']}', expected 'scalar'")
            return False
        if input_spec['dimensions'] != []:
            print(f"❌ FAIL: Input {i} dimensions is {input_spec['dimensions']}, expected []")
            return False
        print(f"  {i:2d}. {input_spec['name']:25s} (scalar) ✓")
    
    print()
    
    # Verify outputs array
    expected_outputs = [
        "New_Water_Temp",
        "New_Sediment_Temp",
        "Daily_Avg_Net_Flux"
    ]
    
    print(f"Output Parameters ({len(config['outputs'])} total):")
    print("-" * 70)
    
    if len(config['outputs']) != len(expected_outputs):
        print(f"❌ FAIL: Expected {len(expected_outputs)} outputs, got {len(config['outputs'])}")
        return False
    
    for i, (output_spec, expected_name) in enumerate(zip(config['outputs'], expected_outputs)):
        if output_spec['name'] != expected_name:
            print(f"❌ FAIL: Output {i} name is '{output_spec['name']}', expected '{expected_name}'")
            return False
        if output_spec['type'] != 'scalar':
            print(f"❌ FAIL: Output {i} type is '{output_spec['type']}', expected 'scalar'")
            return False
        if output_spec['dimensions'] != []:
            print(f"❌ FAIL: Output {i} dimensions is {output_spec['dimensions']}, expected []")
            return False
        print(f"  {i}. {output_spec['name']:25s} (scalar) ✓")
    
    print()
    print("=" * 70)
    print("✓ All verification checks passed!")
    print("=" * 70)
    print()
    print("Configuration Summary:")
    print(f"  - Python path: {config['python_path']}")
    print(f"  - Script: {config['script_path']}")
    print(f"  - Function: {config['function_name']}")
    print(f"  - Log level: {config['log_level']} (INFO)")
    print(f"  - Inputs: {len(config['inputs'])} parameters")
    print(f"  - Outputs: {len(config['outputs'])} parameters")
    print()
    print("Note: Update 'python_path' to match your Python installation directory")
    print("      before using with GoldSim.")
    
    return True

if __name__ == '__main__':
    success = verify_json_config()
    exit(0 if success else 1)
