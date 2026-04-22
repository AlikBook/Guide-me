import os
import sys
import subprocess
import shutil
from pathlib import Path
import platform

def check_yen_wrapper_available():
    """Check if yen_wrapper is available for import."""
    try:
        # Clear any cached imports first
        import sys
        if 'app.functions.yen_compiler.yen_wrapper' in sys.modules:
            del sys.modules['app.functions.yen_compiler.yen_wrapper']
        
        from app.functions.yen_compiler.yen_wrapper import get_k_shortest_paths
        return True
    except ImportError as e:
        print(f"   Import error: {e}")
        return False
    except Exception as e:
        print(f"   Unexpected error during import check: {e}")
        return False

def get_project_root():
    """Get the project root directory."""
    current_file = Path(__file__)
    # app/core/auto_build.py -> backend root
    # Works both on the host workspace and inside Docker (/app/app/core/...)
    return current_file.parents[2]

def clean_build_artifacts(yen_compiler_dir):
    """Clean previous build artifacts to ensure a fresh build."""
    try:
        build_dir = yen_compiler_dir / "build"
        if build_dir.exists():
            shutil.rmtree(build_dir)
            print("   Cleaned previous build directory")
        
        # Remove any .pyd/.so files
        for ext in ["*.pyd", "*.so", "*.dll"]:
            for file in yen_compiler_dir.glob(ext):
                file.unlink()
                print(f"   Removed {file.name}")
        
        # Remove Cython generated C files
        c_file = yen_compiler_dir / "yen_wrapper.c"
        if c_file.exists():
            c_file.unlink()
            print("   Removed generated C file")
            
    except Exception as e:
        print(f"   Warning: Could not clean all artifacts: {e}")

def auto_build_yen_wrapper():
    """
    Automatically build the yen_wrapper C extension if it's not available.
    Returns True if successful or already available, False if failed.
    """
    
    # First check if it's already available
    if check_yen_wrapper_available():
        print("✓ Yen C extension already available")
        return True
    
    print("WARNING: Yen C extension not found. Attempting to build automatically...")
    
    try:
        project_root = get_project_root()
        yen_compiler_dir = project_root / "app" / "functions" / "yen_compiler"
        
        if not yen_compiler_dir.exists():
            print(f"ERROR: Yen compiler directory not found: {yen_compiler_dir}")
            return False
        
        # Verify setup configuration
        if not verify_setup_configuration(yen_compiler_dir):
            return False
        
        print(f"Building C extension for {platform.system()} {platform.machine()}...")
        
        # Save current directory
        original_cwd = os.getcwd()
        
        try:
            # Change to yen_compiler directory
            os.chdir(yen_compiler_dir)
            
            # Clean previous build artifacts
            print("   Cleaning previous build artifacts...")
            clean_build_artifacts(yen_compiler_dir)
            
            # Clean previous build artifacts
            clean_build_artifacts(yen_compiler_dir)
            
            # Install build dependencies
            print("   Installing build dependencies...")
            deps_result = subprocess.run([
                sys.executable, "-m", "pip", "install", 
                "cython", "setuptools", "wheel", "build"
            ], capture_output=True, text=True)
            
            if deps_result.returncode != 0:
                print(f"   ERROR: Failed to install dependencies: {deps_result.stderr}")
                return False
            
            # Try to build in place first (faster)
            print("   Building extension in place...")
            result = subprocess.run([
                sys.executable, "setup.py", "build_ext", "--inplace"
            ], capture_output=True, text=True, shell=True)
            
            if result.returncode == 0:
                print("   Build successful!")
                # Only show summary, not full compiler output
                if result.stdout and "created" in result.stdout.lower():
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if "created" in line.lower() or "copying" in line.lower():
                            print(f"   {line.strip()}")
                
                # Clear any cached imports
                import importlib
                if 'app.functions.yen_compiler.yen_wrapper' in sys.modules:
                    importlib.reload(sys.modules['app.functions.yen_compiler.yen_wrapper'])
                
                # Verify the build worked
                if check_yen_wrapper_available():
                    print("   Extension is now available")
                    return True
                else:
                    print("   WARNING: Build completed but extension not importable")
                    print("   This might be due to import path issues - try restarting the application")
                    return False
            else:
                print(f"   ERROR: Build failed with return code {result.returncode}")
                # Only show relevant error lines, not full compiler spam
                if result.stderr:
                    error_lines = result.stderr.split('\n')
                    relevant_errors = []
                    for line in error_lines:
                        line = line.strip()
                        if (line and not line.startswith('/') and 
                            not 'link.exe' in line and 
                            not 'LIBPATH' in line and
                            not 'EXPORT:' in line and
                            not 'IMPLIB:' in line and
                            len(line) < 200):  # Skip very long compiler command lines
                            relevant_errors.append(line)
                    
                    if relevant_errors:
                        print("   Key errors:")
                        for error in relevant_errors[-5:]:  # Show last 5 relevant errors
                            print(f"     {error}")
                    else:
                        print(f"   Build process failed - check compiler installation")
                return False
                
        finally:
            # Restore original directory
            os.chdir(original_cwd)
            
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Build process failed with error: {e}")
        print(f"   Command: {e.cmd}")
        print(f"   Return code: {e.returncode}")
        if hasattr(e, 'stdout') and e.stdout:
            print(f"   STDOUT: {e.stdout}")
        if hasattr(e, 'stderr') and e.stderr:
            print(f"   STDERR: {e.stderr}")
        return False
    except FileNotFoundError as e:
        print(f"ERROR: Required file or command not found: {e}")
        print("   This usually means you need to install build tools for your platform")
        return False
    except Exception as e:
        print(f"ERROR: Unexpected error during build: {e}")
        import traceback
        print(f"   Full traceback: {traceback.format_exc()}")
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
    print("MANUAL BUILD INSTRUCTIONS")
    print("="*60)
    
    system = platform.system()
    requirements = get_build_requirements()
    
    print(f"\nRequirements for {system}:")
    for req in requirements:
        print(f"   • {req}")
    
    print(f"\nManual build steps:")
    print("   1. Install the requirements above")
    print("   2. Open a command prompt/terminal")
    print("   3. Navigate to app/functions/yen_compiler")
    print("   4. Run: python setup.py build_ext --inplace")
    
    print("="*60)

def verify_setup_configuration(yen_compiler_dir):
    """Verify that setup.py and required files exist and are properly configured."""
    setup_py = yen_compiler_dir / "setup.py"
    if not setup_py.exists():
        print("   ERROR: setup.py not found")
        return False
    
    # Check for required source files
    required_files = ["yen_wrapper.pyx", "yen_algorithm.c", "yen_algorithm.h"]
    missing_files = []
    
    for file in required_files:
        if not (yen_compiler_dir / file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"   ERROR: Missing required files: {', '.join(missing_files)}")
        return False
    
    print("   ✓ All required files present")
    return True

def ensure_yen_wrapper():
    """
    Ensure yen_wrapper is available, with automatic build attempt.
    Returns True if available, False otherwise.
    """
    if check_yen_wrapper_available():
        return True
    
    print("\nStarting automatic C extension build...")
    success = auto_build_yen_wrapper()
    
    if success:
        print("SUCCESS: C extension build completed successfully!")
        return True
    else:
        print("ERROR: Automatic build failed.")
        print_manual_build_instructions()
        return False