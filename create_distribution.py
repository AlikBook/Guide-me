#!/usr/bin/env python3
"""
Distribution package creator for the Metro project.
This script creates a distribution package with pre-built wheels for multiple platforms.
"""

import os
import sys
import shutil
import zipfile
from pathlib import Path
import subprocess
import platform

def create_distribution_package():
    """Create a distribution package with everything needed."""
    
    project_root = Path(__file__).parent
    dist_dir = project_root / "distribution"
    
    # Clean and create distribution directory
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir()
    
    print("Creating distribution package...")
    
    # Copy main project files
    print("Copying project files...")
    
    # Copy essential directories
    essential_dirs = [
        "fastapi-backend",
        "front_end",
        "Examples"
    ]
    
    for dir_name in essential_dirs:
        src = project_root / dir_name
        if src.exists():
            dst = dist_dir / dir_name
            shutil.copytree(src, dst, ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '.git'))
            print(f"  ✓ Copied {dir_name}")
    
    # Copy essential files
    essential_files = [
        "README.md",
        "YEN_INSTALLATION.md",
        "build_wheels.py"
    ]
    
    for file_name in essential_files:
        src = project_root / file_name
        if src.exists():
            shutil.copy2(src, dist_dir / file_name)
            print(f"  ✓ Copied {file_name}")
    
    # Create installation script
    install_script = f"""#!/usr/bin/env python3
'''
Quick installation script for the Metro Project
'''

import subprocess
import sys
import os
from pathlib import Path

def main():
    print("Metro Project - Quick Installer")
    print("=" * 40)
    
    # Install backend dependencies
    print("Installing backend dependencies...")
    backend_req = Path("fastapi-backend/requirements.txt")
    if backend_req.exists():
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(backend_req)], check=True)
    
    # Install frontend dependencies
    print("Installing frontend dependencies...")
    frontend_dir = Path("front_end")
    if frontend_dir.exists():
        os.chdir(frontend_dir)
        subprocess.run(["npm", "install"], check=True)
        os.chdir("..")
    
    # Try to build yen_wrapper
    print("Building Yen algorithm C extension...")
    try:
        subprocess.run([sys.executable, "build_wheels.py"], check=True)
        print("✓ C extension built successfully")
    except subprocess.CalledProcessError:
        print("⚠️  C extension build failed. Application will run with limited functionality.")
        print("   See YEN_INSTALLATION.md for manual installation instructions.")
    
    print("\\nInstallation completed!")
    print("\\nTo run the application:")
    print("1. Backend: cd fastapi-backend && python -m uvicorn app.main:app --reload")
    print("2. Frontend: cd front_end && npm run dev")

if __name__ == "__main__":
    main()
"""
    
    with open(dist_dir / "install.py", "w") as f:
        f.write(install_script)
    
    # Create a batch file for Windows users
    batch_script = """@echo off
echo Metro Project - Windows Installer
echo ====================================
python install.py
pause
"""
    
    with open(dist_dir / "install.bat", "w") as f:
        f.write(batch_script)
    
    # Create a shell script for Unix users
    shell_script = """#!/bin/bash
echo "Metro Project - Unix Installer"
echo "======================================"
python3 install.py
"""
    
    with open(dist_dir / "install.sh", "w") as f:
        f.write(shell_script)
    
    # Make shell script executable
    os.chmod(dist_dir / "install.sh", 0o755)
    
    # Create README for distribution
    dist_readme = f"""# Metro Project - Distribution Package

This package contains the complete Metro project with all necessary files.

## Quick Start

### Windows:
1. Double-click `install.bat`
2. Or run: `python install.py`

### Linux/macOS:
1. Run: `./install.sh`
2. Or run: `python3 install.py`

## Manual Installation

If the automatic installer doesn't work:

1. **Install backend dependencies:**
   ```
   cd fastapi-backend
   pip install -r requirements.txt
   ```

2. **Install frontend dependencies:**
   ```
   cd front_end
   npm install
   ```

3. **Build the C extension (for performance):**
   ```
   python build_wheels.py
   ```
   See `YEN_INSTALLATION.md` for detailed instructions.

## Running the Application

1. **Start the backend:**
   ```
   cd fastapi-backend
   python -m uvicorn app.main:app --reload
   ```

2. **Start the frontend:**
   ```
   cd front_end
   npm run dev
   ```

## Troubleshooting

- If you get C extension errors, see `YEN_INSTALLATION.md`
- The application will work without the C extension, but performance may be reduced
- For detailed documentation, see the main `README.md`

## System Requirements

- Python 3.9+
- Node.js 16+
- C compiler (optional, for performance optimization)

Generated on: {platform.system()} {platform.machine()}
Python: {platform.python_version()}
"""
    
    with open(dist_dir / "README_DISTRIBUTION.md", "w") as f:
        f.write(dist_readme)
    
    print(f"\\nDistribution package created in: {dist_dir}")
    print("\\nContents:")
    for item in sorted(dist_dir.iterdir()):
        print(f"  - {item.name}")
    
    # Optionally create a ZIP file
    create_zip = input("\\nCreate ZIP archive? (y/N): ").lower().startswith('y')
    if create_zip:
        zip_path = project_root / f"metro_project_distribution_{platform.system().lower()}.zip"
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(dist_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(dist_dir)
                    zipf.write(file_path, arcname)
        
        print(f"ZIP archive created: {zip_path}")
    
    return dist_dir

if __name__ == "__main__":
    create_distribution_package()
