# Yen Algorithm C Extension - Installation Guide

## 🚀 Automatic Build (New!)

**Good news!** The backend now automatically attempts to build the C extension when it starts up. 

**For most users, you don't need to do anything manually!**

When you run the backend:
```bash
cd fastapi-backend
python -m uvicorn app.main:app --reload
```

The system will:
1. ✅ Check if C extension is available
2. 🔨 Automatically build it if missing
3. ⚡ Enable high-performance mode if successful
4. 🐌 Fall back to compatibility mode if build fails

## Manual Options (If Auto-Build Fails)

### Option 1: Use Pre-built Wheels (Easiest)

If you have access to pre-built wheels for your platform:

```bash
pip install path/to/yen_wrapper-1.0.0-cp311-cp311-win_amd64.whl
```

### Option 2: Build Locally (Recommended)

1. **Install build dependencies:**
   ```bash
   pip install build cython wheel
   ```

2. **Run the build script:**
   ```bash
   python build_wheels.py
   ```

3. **Install the built wheel:**
   ```bash
   pip install wheels/yen_wrapper-*.whl
   ```

### Option 3: Manual Build

If the automated script doesn't work:

1. **Navigate to the yen_compiler directory:**
   ```bash
   cd fastapi-backend/app/functions/yen_compiler
   ```

2. **Install dependencies:**
   ```bash
   pip install cython setuptools wheel
   ```

3. **Build the extension:**
   ```bash
   python setup.py build_ext --inplace
   ```

   Or build a wheel:
   ```bash
   python -m build --wheel
   ```

### Option 4: GitHub Actions (For Distribution)

The project includes GitHub Actions workflows that automatically build wheels for:
- Windows (x64)
- macOS (x64 and ARM64)
- Linux (x64)

These are triggered on pushes to main/master branches.

## Platform-Specific Notes

### Windows
- Requires Microsoft C++ Build Tools or Visual Studio
- The build script will attempt to use the Python's built-in compiler

### macOS
- Requires Xcode Command Line Tools: `xcode-select --install`

### Linux
- Requires GCC: `sudo apt-get install gcc` (Ubuntu/Debian)

## Troubleshooting

### "Microsoft Visual C++ 14.0 is required" (Windows)
1. Install Microsoft C++ Build Tools from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Or use the pre-built wheel if available

### "error: Unable to find vcvarsall.bat" (Windows)
- Same solution as above - install Microsoft C++ Build Tools

### Import Error at Runtime
If you see "Warning: yen_wrapper not available":
1. The C extension wasn't built or installed properly
2. Run `python build_wheels.py` to build for your platform
3. Some functionality will be limited but the application will still work

## Verification

To verify the installation worked:

```python
try:
    from yen_wrapper import get_k_shortest_paths
    print("✓ Yen wrapper installed successfully")
except ImportError as e:
    print(f"✗ Installation failed: {e}")
```

## Performance

With the C extension:
- Metro pathfinding: ~1-5ms per query
- Complex RER calculations: ~10-50ms per query

Without the C extension:
- Same operations: 100-1000x slower
- Not suitable for real-time applications
