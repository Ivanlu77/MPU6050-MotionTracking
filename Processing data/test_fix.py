#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick test for the pandas fixes
"""

import pandas as pd
import numpy as np
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from functions import integral, integral_vel, get_vel_drift
    print("? Successfully imported functions")
except ImportError as e:
    print(f"? Import error: {e}")
    sys.exit(1)

def test_functions():
    """Test the fixed functions with sample data"""
    print("\n=== Testing Fixed Functions ===")
    
    # Create sample data similar to what the program expects
    time = np.linspace(0, 5, 50)  # 5 seconds, 50 samples
    
    # Sample acceleration data
    acc_data = pd.DataFrame({
        'accx': np.sin(time) * 2 + np.random.normal(0, 0.1, len(time)),
        'accy': np.cos(time) * 1.5 + np.random.normal(0, 0.1, len(time)),
        'accz': np.ones_like(time) * 0.5 + np.random.normal(0, 0.1, len(time))
    })
    
    print(f"Sample data shape: {acc_data.shape}")
    print(f"Time array length: {len(time)}")
    
    # Test integral function
    try:
        print("\nTesting integral function...")
        vel_result = integral(time, acc_data, ['velx', 'vely', 'velz'])
        print(f"? integral function works, result shape: {vel_result.shape}")
        print(f"  Result columns: {list(vel_result.columns)}")
        print(f"  Sample values: {vel_result.iloc[0].values}")
    except Exception as e:
        print(f"? integral function failed: {e}")
        return False
    
    # Test integral_vel function
    try:
        print("\nTesting integral_vel function...")
        # Create a simple stationary array
        stationary = np.zeros(len(time)-1)  # All moving
        stationary[10:20] = 1  # Stationary period in the middle
        
        vel_result2 = integral_vel(acc_data, time, stationary)
        print(f"? integral_vel function works, result shape: {vel_result2.shape}")
        print(f"  Result columns: {list(vel_result2.columns)}")
        print(f"  Sample values: {vel_result2.iloc[0].values}")
    except Exception as e:
        print(f"? integral_vel function failed: {e}")
        return False
    
    # Test get_vel_drift function (this calls multiple functions)
    try:
        print("\nTesting get_vel_drift function...")
        vel_drift = get_vel_drift(time, acc_data)
        print(f"? get_vel_drift function works, result shape: {vel_drift.shape}")
        print(f"  Result columns: {list(vel_drift.columns)}")
        print(f"  Sample values: {vel_drift.iloc[0].values}")
    except Exception as e:
        print(f"? get_vel_drift function failed: {e}")
        print(f"  Error details: {str(e)}")
        return False
    
    return True

def main():
    print("=== Quick Pandas Fix Test ===")
    print(f"Pandas version: {pd.__version__}")
    print(f"NumPy version: {np.__version__}")
    
    if test_functions():
        print("\n? All tests passed! The fixes work correctly.")
        print("You can now try running main.py again.")
    else:
        print("\n? Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main() 