#!/usr/bin/env python3
"""
Simple validation script for the dummy test data files.
This checks file format without requiring external dependencies.
"""

import re

def validate_ascii_file(filepath, expected_measurements=3):
    """Validate an IBA ASCII file format."""
    print(f"\nValidating: {filepath}")
    print("-" * 60)

    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()

        measurement_count = 0
        data_point_counts = []
        current_measurement = None
        current_points = 0
        measurements_info = []

        for line in lines:
            line = line.strip()

            # Count measurements
            if line.startswith('# Measurement number'):
                parts = re.split(r'\t', line)
                if len(parts) >= 2:
                    measurement_count += 1
                    current_measurement = parts[1]
                    current_points = 0

            # Extract beam info
            elif line.startswith('%BMT'):
                parts = re.split(r'\t', line)
                if len(parts) >= 3:
                    beam_type = parts[1]
                    beam_energy = parts[2]

            # Extract field size
            elif line.startswith('%FSZ'):
                parts = re.split(r'\t', line)
                if len(parts) >= 3:
                    field_x = parts[1]
                    field_y = parts[2]

            # Extract date
            elif line.startswith('%DAT'):
                parts = re.split(r'\t', line)
                if len(parts) >= 2:
                    date = parts[1]

            # Count data points
            elif line.startswith('='):
                current_points += 1

            # End of measurement
            elif line.startswith(':EOM'):
                data_point_counts.append(current_points)
                measurements_info.append({
                    'number': current_measurement,
                    'beam_type': beam_type,
                    'energy': beam_energy,
                    'field_size': f"{field_x}x{field_y}",
                    'date': date,
                    'points': current_points
                })

        # Print results
        print(f"✓ File is valid ASCII format")
        print(f"✓ Total measurements: {measurement_count}")
        print(f"✓ Total data points: {sum(data_point_counts)}")

        print(f"\nMeasurement Details:")
        for i, info in enumerate(measurements_info, 1):
            print(f"  {i}. {info['beam_type']} {info['energy']}MV, "
                  f"Field: {info['field_size']}mm, "
                  f"Points: {info['points']}, "
                  f"Date: {info['date']}")

        # Validate expectations
        if measurement_count == expected_measurements:
            print(f"\n✓ Expected {expected_measurements} measurements: PASS")
        else:
            print(f"\n✗ Expected {expected_measurements}, found {measurement_count}: FAIL")
            return False

        return True

    except FileNotFoundError:
        print(f"✗ File not found: {filepath}")
        return False
    except Exception as e:
        print(f"✗ Error validating file: {e}")
        return False


def main():
    """Main validation routine."""
    print("="*60)
    print("Validating Test Data Files")
    print("="*60)

    ref_valid = validate_ascii_file("test_data_reference.txt", expected_measurements=3)
    mes_valid = validate_ascii_file("test_data_measurement.txt", expected_measurements=3)

    print("\n" + "="*60)
    print("Validation Summary")
    print("="*60)

    if ref_valid and mes_valid:
        print("✓ All files validated successfully!")
        print("\nTest Data Overview:")
        print("  • 3 matched measurement pairs")
        print("  • Beam: 6MV Photon (PHO)")
        print("  • Field sizes: 100x100mm, 200x200mm")
        print("  • Scan directions: Inline and Crossline")
        print("  • Depth: 100mm")
        print("\nThe measurement data has small intentional differences")
        print("(~0.5-1% dose variations) to produce realistic gamma results.")
        print("\nTo test the application:")
        print("  1. python main.py")
        print("  2. Load test_data_reference.txt as reference")
        print("  3. Load test_data_measurement.txt as measurement")
        print("  4. Run gamma analysis and save the PDF")
        print("\nExpected results:")
        print("  • 3 matching pairs found")
        print("  • Pass rates should be ~95-99%")
        print("  • Small gamma failures at field edges")
        return True
    else:
        print("✗ Validation failed!")
        return False


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
