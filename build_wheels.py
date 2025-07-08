#!/usr/bin/env python3
"""
Build script for creating wheels for the yen_wrapper extension.
Run this script to build wheels for your current platform.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def main():
    # Get the directory containing this script
    script_dir = Path(__file__).parent
    yen_compiler_dir = script_dir / "fastapi-backend" / "app" / "functions" / "yen_compiler"
    
    if not yen_compiler_dir.exists():
        print(f"Error: Directory {yen_compiler_dir} does not exist!")
        return 1
    
    print(f"Building wheel for {platform.system()} {platform.machine()}...")
    print(f"Python version: {sys.version}")
    
    # Change to the yen_compiler directory
    original_cwd = os.getcwd()
    os.chdir(yen_compiler_dir)
    
    try:
        # Install build dependencies
        print("Installing build dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "build", "cython", "wheel"], check=True)
        
        # Build the wheel
        print("Building wheel...")
        subprocess.run([sys.executable, "-m", "build", "--wheel"], check=True)
        
        # List the built wheels
        dist_dir = yen_compiler_dir / "dist"
        if dist_dir.exists():
            wheels = list(dist_dir.glob("*.whl"))
            if wheels:
                print(f"\nSuccessfully built wheel(s):")
                for wheel in wheels:
                    print(f"  - {wheel.name}")
                print(f"\nWheels are located in: {dist_dir}")
                
                # Copy wheel to project root for easy access
                project_root = script_dir
                wheels_dir = project_root / "wheels"
                wheels_dir.mkdir(exist_ok=True)
                
                for wheel in wheels:
                    dest = wheels_dir / wheel.name
                    import shutil
                    shutil.copy2(wheel, dest)
                    print(f"Copied wheel to: {dest}")
                    
            else:
                print("No wheels found in dist directory!")
                return 1
        else:
            print("No dist directory found!")
            return 1
            
    except subprocess.CalledProcessError as e:
        print(f"Error during build: {e}")
        return 1
    finally:
        os.chdir(original_cwd)
    
    print("\nBuild completed successfully!")
    print("\nTo distribute this wheel to other users:")
    print("1. Share the .whl file(s) from the 'wheels' directory")
    print("2. Users can install with: pip install path/to/wheel.whl")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
