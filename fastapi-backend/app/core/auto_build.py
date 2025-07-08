"""
Auto-build utility for the Yen C extension.
This module handles automatic building of the C extension when needed.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import platform

def check_yen_wrapper_available():
    """Check if yen_wrapper is available for import."""
    try:
        from app.functions.yen_compiler.yen_wrapper import get_k_shortest_paths
        return True
    except ImportError:
        return False

def get_project_root():
    """Get the project root directory."""
    current_file = Path(__file__)
    # Go up from app/core/auto_build.py to project root
    return current_file.parent.parent.parent

def auto_build_yen_wrapper():
    """
    Automatically build the yen_wrapper C extension if it's not available.
    Returns True if successful or already available, False if failed.
    """
    
    # First check if it's already available
    if check_yen_wrapper_available():
        print("✓ Yen C extension already available")
        return True
    
    print("⚠️  Yen C extension not found. Attempting to build automatically...")
    
    try:
        project_root = get_project_root()
        yen_compiler_dir = project_root / "fastapi-backend" / "app" / "functions" / "yen_compiler"
        
        if not yen_compiler_dir.exists():
            print(f"❌ Yen compiler directory not found: {yen_compiler_dir}")
            return False
        
        print(f"🔧 Building C extension for {platform.system()} {platform.machine()}...")
        
        # Save current directory
        original_cwd = os.getcwd()
        
        try:
            # Change to yen_compiler directory
            os.chdir(yen_compiler_dir)
            
            # Install build dependencies
            print("   📦 Installing build dependencies...")
            subprocess.run([
                sys.executable, "-m", "pip", "install", 
                "cython", "setuptools", "wheel", "build"
            ], check=True, capture_output=True, text=True)
            
            # Try to build in place first (faster)
            print("   🔨 Building extension in place...")
            result = subprocess.run([
                sys.executable, "setup.py", "build_ext", "--inplace"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("   ✓ Build successful!")
                
                # Verify the build worked
                if check_yen_wrapper_available():
                    print("   ✓ Extension is now available")
                    return True
                else:
                    print("   ⚠️  Build completed but extension not importable")
                    return False
            else:
                print(f"   ❌ Build failed: {result.stderr}")
                return False
                
        finally:
            # Restore original directory
            os.chdir(original_cwd)
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed with error: {e}")
        if hasattr(e, 'stderr') and e.stderr:
            print(f"   Error details: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during build: {e}")
        return False

def get_build_requirements():
    """Get platform-specific build requirements."""
    system = platform.system().lower()
    
    requirements = {
        "windows": [
            "Microsoft C++ Build Tools",
            "https://visualstudio.microsoft.com/visual-cpp-build-tools/"
        ],
        "darwin": [
            "Xcode Command Line Tools", 
            "Run: xcode-select --install"
        ],
        "linux": [
            "GCC compiler",
            "Ubuntu/Debian: sudo apt-get install gcc build-essential",
            "CentOS/RHEL: sudo yum install gcc gcc-c++ make"
        ]
    }
    
    return requirements.get(system, ["C compiler"])

def print_manual_build_instructions():
    """Print manual build instructions if auto-build fails."""
    print("\n" + "="*60)
    print("🛠️  MANUAL BUILD INSTRUCTIONS")
    print("="*60)
    
    system = platform.system()
    requirements = get_build_requirements()
    
    print(f"\n📋 Requirements for {system}:")
    for req in requirements:
        print(f"   • {req}")
    
    print(f"\n🔧 Manual build steps:")
    print("   1. Install the requirements above")
    print("   2. Run: python build_wheels.py")
    print("   3. Or navigate to fastapi-backend/app/functions/yen_compiler")
    print("   4. Run: python setup.py build_ext --inplace")
    
    print(f"\n💡 Alternative:")
    print("   • The application will work without the C extension")
    print("   • Performance will be reduced but all features available")
    print("   • See YEN_INSTALLATION.md for detailed instructions")
    print("="*60)

def ensure_yen_wrapper():
    """
    Ensure yen_wrapper is available, with automatic build attempt.
    Returns True if available, False otherwise.
    """
    if check_yen_wrapper_available():
        return True
    
    print("\n🚀 Starting automatic C extension build...")
    success = auto_build_yen_wrapper()
    
    if success:
        print("✅ C extension build completed successfully!")
        return True
    else:
        print("❌ Automatic build failed.")
        print_manual_build_instructions()
        return False
