"""
Setup script for GoldSim-rTemp integration
Copies necessary files to GoldSim model directory
"""

import os
import shutil
import sys
from pathlib import Path

# Target directory (your GoldSim model location)
TARGET_DIR = r"C:\Users\JasonLillywhite\GoldSim\GTGData - Documents\Library\Applications\Water Management\Water Quality\rTemp"

# Files to copy
FILES_TO_COPY = [
    "rtemp_goldsim_adapter.py",
    "rtemp_adapter.json",
    "validate_environment.py",
    "verify_json_config.py"
]

def main():
    print("=" * 70)
    print("GoldSim-rTemp Integration Setup")
    print("=" * 70)
    
    # Check if target directory exists
    if not os.path.exists(TARGET_DIR):
        print(f"\n❌ Target directory does not exist:")
        print(f"   {TARGET_DIR}")
        print("\nPlease create the directory first or verify the path.")
        return False
    
    print(f"\n✓ Target directory found:")
    print(f"  {TARGET_DIR}")
    
    # Get Python path
    python_path = sys.prefix
    print(f"\n✓ Python installation:")
    print(f"  {python_path}")
    print(f"  Version: {sys.version.split()[0]}")
    
    # Copy files
    print(f"\n📁 Copying files...")
    copied_files = []
    for filename in FILES_TO_COPY:
        src = filename
        dst = os.path.join(TARGET_DIR, filename)
        
        if not os.path.exists(src):
            print(f"  ⚠️  {filename} - NOT FOUND (skipping)")
            continue
        
        try:
            shutil.copy2(src, dst)
            copied_files.append(filename)
            print(f"  ✓ {filename}")
        except Exception as e:
            print(f"  ❌ {filename} - ERROR: {e}")
    
    # Update JSON with correct Python path
    json_path = os.path.join(TARGET_DIR, "rtemp_adapter.json")
    if os.path.exists(json_path):
        print(f"\n📝 Updating rtemp_adapter.json with your Python path...")
        try:
            with open(json_path, 'r') as f:
                content = f.read()
            
            # Replace the placeholder path with actual Python path
            # Use double backslashes for JSON
            python_path_json = python_path.replace("\\", "\\\\")
            content = content.replace(
                "C:\\\\Users\\\\YourUsername\\\\AppData\\\\Local\\\\Programs\\\\Python\\\\Python311",
                python_path_json
            )
            
            with open(json_path, 'w') as f:
                f.write(content)
            
            print(f"  ✓ Updated python_path to: {python_path}")
        except Exception as e:
            print(f"  ⚠️  Could not update JSON: {e}")
            print(f"     You'll need to manually edit python_path in rtemp_adapter.json")
    
    # Summary
    print("\n" + "=" * 70)
    print("Setup Summary")
    print("=" * 70)
    print(f"\n✓ Copied {len(copied_files)} files to:")
    print(f"  {TARGET_DIR}")
    
    print("\n📋 Next Steps:")
    print("\n1. Download GSPy v1.8.8 DLL:")
    print("   https://github.com/GoldSim/GSPy/releases")
    print(f"   Get: GSPy_Release_py314.dll (for Python 3.14)")
    
    print("\n2. Copy and rename the DLL:")
    print(f"   Copy GSPy_Release_py314.dll to:")
    print(f"   {TARGET_DIR}")
    print(f"   Rename it to: rtemp_adapter.dll")
    
    print("\n3. Update REFERENCE_DATE in rtemp_goldsim_adapter.py:")
    print("   Set it to match your GoldSim simulation start date")
    
    print("\n4. Run validation:")
    print(f"   cd \"{TARGET_DIR}\"")
    print("   python validate_environment.py")
    
    print("\n5. Configure GoldSim External Element:")
    print("   - DLL: rtemp_adapter.dll")
    print("   - Function: GSPy")
    print("   - 14 inputs, 3 outputs (see documentation)")
    
    print("\n" + "=" * 70)
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
