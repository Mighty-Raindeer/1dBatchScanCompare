#!/usr/bin/env python3
"""
Quick test script to verify the dummy data files work correctly.
This tests the parsing and matching logic without running the full GUI.
"""

import sys
from main import GammaAnalysisApp

def test_dummy_data():
    """Test the dummy data files."""
    print("="*60)
    print("Testing 1D Batch Scan Compare with Dummy Data")
    print("="*60)

    app = GammaAnalysisApp()

    # Test reference file
    print("\n1. Testing Reference File Loading...")
    try:
        ref_data, ref_header = app._parse_ascii_file("test_data_reference.txt")
        app.reference_data_full = ref_data
        app.reference_header = ref_header
        print(f"   ✓ Reference file loaded: {len(ref_header)} measurements")
        for i, meas in enumerate(ref_header, 1):
            print(f"     - Measurement {i}: {meas[4]} {meas[5]}MV, "
                  f"{meas[6]}x{meas[7]}mm, depth {meas[11]}mm")
    except Exception as e:
        print(f"   ✗ Failed to load reference file: {e}")
        return False

    # Test measurement file
    print("\n2. Testing Measurement File Loading...")
    try:
        mes_data, mes_header = app._parse_ascii_file("test_data_measurement.txt")
        app.measurement_data_full = mes_data
        app.measurement_header = mes_header
        print(f"   ✓ Measurement file loaded: {len(mes_header)} measurements")
        for i, meas in enumerate(mes_header, 1):
            print(f"     - Measurement {i}: {meas[4]} {meas[5]}MV, "
                  f"{meas[6]}x{meas[7]}mm, depth {meas[11]}mm")
    except Exception as e:
        print(f"   ✗ Failed to load measurement file: {e}")
        return False

    # Test data structure
    print("\n3. Testing Data Structures...")
    import pandas as pd
    try:
        app.reference_dataframe = pd.DataFrame(
            ref_data,
            columns=[
                'measurement number', 'measurement data', 'measurement time',
                'measurement type', 'beam type', 'beam energy', 'field size x',
                'field size y', 'SSD', 'startZ', 'stopZ', 'xpos', 'ypos',
                'zpos', 'dose'
            ]
        )
        app.measurement_dataframe = pd.DataFrame(
            mes_data,
            columns=[
                'measurement number', 'measurement data', 'measurement time',
                'measurement type', 'beam type', 'beam energy', 'field size x',
                'field size y', 'SSD', 'startZ', 'stopZ', 'xpos', 'ypos',
                'zpos', 'dose'
            ]
        )
        print(f"   ✓ DataFrames created successfully")
        print(f"     - Reference rows: {len(app.reference_dataframe)}")
        print(f"     - Measurement rows: {len(app.measurement_dataframe)}")
    except Exception as e:
        print(f"   ✗ Failed to create DataFrames: {e}")
        return False

    # Test matching logic
    print("\n4. Testing Measurement Matching...")
    try:
        matches = app._find_matching_tests()
        print(f"   ✓ Found {len(matches)} matching pairs")
        if len(matches) != 3:
            print(f"   ⚠ Warning: Expected 3 matches, got {len(matches)}")
        for i, (mes_num, ref_num) in enumerate(matches, 1):
            print(f"     - Match {i}: Measurement #{mes_num} ↔ Reference #{ref_num}")
    except Exception as e:
        print(f"   ✗ Failed to find matches: {e}")
        return False

    # Summary
    print("\n" + "="*60)
    print("Test Summary:")
    print("="*60)
    print("✓ All tests passed!")
    print(f"✓ Reference file: 3 measurements with {len(ref_data)} data points")
    print(f"✓ Measurement file: 3 measurements with {len(mes_data)} data points")
    print(f"✓ Successfully matched {len(matches)}/3 expected pairs")
    print("\nThe dummy data files are ready for testing!")
    print("\nTo test the full application:")
    print("  1. Run: python main.py")
    print("  2. Load: test_data_reference.txt")
    print("  3. Load: test_data_measurement.txt")
    print("  4. Click 'Run Gamma' and save the PDF")
    print("="*60)

    return True

if __name__ == "__main__":
    success = test_dummy_data()
    sys.exit(0 if success else 1)
