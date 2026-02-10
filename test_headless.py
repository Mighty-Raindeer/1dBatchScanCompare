#!/usr/bin/env python3
"""
Headless test of the gamma analysis tool.
This runs the complete analysis without GUI.
"""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

from main import GammaAnalysisApp
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages

def run_headless_test():
    """Run gamma analysis test without GUI."""

    print("="*60)
    print("Running Headless Gamma Analysis Test")
    print("="*60)

    # Create app instance (will create GUI window but we won't show it)
    print("\n1. Initializing application...")
    app = GammaAnalysisApp()

    # Load reference file
    print("\n2. Loading reference file...")
    try:
        ref_data, ref_header = app._parse_ascii_file("test_data_reference.txt")
        app.reference_data_full = ref_data
        app.reference_header = ref_header
        app.reference_dataframe = pd.DataFrame(
            ref_data,
            columns=[
                'measurement number', 'measurement data', 'measurement time',
                'measurement type', 'beam type', 'beam energy', 'field size x',
                'field size y', 'SSD', 'startZ', 'stopZ', 'xpos', 'ypos',
                'zpos', 'dose'
            ]
        )
        print(f"   ✓ Loaded {len(ref_header)} reference measurements")
        for i, h in enumerate(ref_header, 1):
            print(f"     {i}. {h[4]} {h[5]}MV, {h[6]}x{h[7]}mm")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return False

    # Load measurement file
    print("\n3. Loading measurement file...")
    try:
        mes_data, mes_header = app._parse_ascii_file("test_data_measurement.txt")
        app.measurement_data_full = mes_data
        app.measurement_header = mes_header
        app.measurement_dataframe = pd.DataFrame(
            mes_data,
            columns=[
                'measurement number', 'measurement data', 'measurement time',
                'measurement type', 'beam type', 'beam energy', 'field size x',
                'field size y', 'SSD', 'startZ', 'stopZ', 'xpos', 'ypos',
                'zpos', 'dose'
            ]
        )
        print(f"   ✓ Loaded {len(mes_header)} measurement measurements")
        for i, h in enumerate(mes_header, 1):
            print(f"     {i}. {h[4]} {h[5]}MV, {h[6]}x{h[7]}mm")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return False

    # Find matches
    print("\n4. Finding matching measurement pairs...")
    try:
        matches = app._find_matching_tests()
        print(f"   ✓ Found {len(matches)} matching pairs")

        if len(matches) == 0:
            print("   ✗ No matches found!")
            return False

    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return False

    # Run gamma analysis
    print("\n5. Running gamma analysis...")
    pdf_path = "test_output_gamma_analysis.pdf"

    try:
        app.pdf_pages = PdfPages(pdf_path)

        successful = 0
        failed = 0
        results = []

        for measure_num, ref_num in matches:
            try:
                print(f"\n   Processing pair: Measurement #{measure_num} vs Reference #{ref_num}")
                app._process_gamma_pair(measure_num, ref_num)
                successful += 1
                results.append((measure_num, ref_num, "SUCCESS"))
            except Exception as e:
                failed += 1
                results.append((measure_num, ref_num, f"FAILED: {str(e)}"))
                print(f"   ✗ Failed: {e}")

        app.pdf_pages.close()

        print(f"\n   ✓ Analysis complete!")
        print(f"     - Successful: {successful}/{len(matches)}")
        print(f"     - Failed: {failed}/{len(matches)}")
        print(f"     - PDF saved: {pdf_path}")

    except Exception as e:
        if app.pdf_pages:
            app.pdf_pages.close()
        print(f"   ✗ Gamma analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Summary
    print("\n" + "="*60)
    print("Test Results Summary")
    print("="*60)

    for measure_num, ref_num, status in results:
        if "SUCCESS" in status:
            print(f"✓ Pair ({measure_num} vs {ref_num}): {status}")
        else:
            print(f"✗ Pair ({measure_num} vs {ref_num}): {status}")

    print("\n" + "="*60)
    print(f"Overall: {successful}/{len(matches)} analyses completed successfully")
    print(f"PDF Report: {pdf_path}")
    print("="*60)

    return successful == len(matches)

if __name__ == "__main__":
    import sys

    try:
        success = run_headless_test()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
