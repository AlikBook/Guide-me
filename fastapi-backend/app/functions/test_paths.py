#!/usr/bin/env python3
"""
Test script to verify that the path configurations work correctly
"""
import os
import sys

# Add the current directory to the Python path
sys.path.append(os.path.dirname(__file__))

try:
    from reads_and_pickles import get_pickle_path, get_v2_file_path
    from functionsV3 import get_pickle_path as get_pickle_path_v3
    
    print("Path Configuration Test")
    print("=" * 40)
    
    # Test pickle path from reads_and_pickles
    pickle_path = get_pickle_path("test.pkl")
    print(f"Pickle path (reads_and_pickles): {pickle_path}")
    print(f"Pickle directory exists: {os.path.exists(os.path.dirname(pickle_path))}")
    
    # Test pickle path from functionsV3
    pickle_path_v3 = get_pickle_path_v3("test.pkl")
    print(f"Pickle path (functionsV3): {pickle_path_v3}")
    print(f"Pickle directory exists: {os.path.exists(os.path.dirname(pickle_path_v3))}")
    
    # Test V2 text files path
    v2_path = get_v2_file_path("stops.txt")
    print(f"V2 text file path: {v2_path}")
    print(f"V2 text file exists: {os.path.exists(v2_path)}")
    
    # List files in V2 directory
    v2_dir = os.path.dirname(v2_path)
    if os.path.exists(v2_dir):
        files = os.listdir(v2_dir)
        print(f"Files in V2 directory: {files}")
    else:
        print("V2 directory does not exist")
    
    print("=" * 40)
    print("Test completed successfully!")
    
except ImportError as e:
    print(f"Import error: {e}")
except Exception as e:
    print(f"Error during test: {e}")
