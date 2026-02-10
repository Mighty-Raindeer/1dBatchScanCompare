# Test Data Documentation

## Overview

This directory contains dummy test data files in IBA OmniPro ASCII format for testing the gamma analysis application.

## Test Files

### `test_data_reference.txt`
- **Purpose**: Reference/baseline measurements (e.g., from commissioning or previous year)
- **Date**: 01-15-2024
- **Measurements**: 3 profiles

### `test_data_measurement.txt`
- **Purpose**: Evaluation measurements (e.g., from current annual QA)
- **Date**: 01-15-2025
- **Measurements**: 3 profiles

## Measurement Details

Both files contain identical beam configurations with small intentional dose variations (~0.5-1%) to simulate realistic measurement differences:

| # | Beam Type | Energy | Field Size | Scan Type  | Points | X Range | Y Range | Depth |
|---|-----------|--------|------------|------------|--------|---------|---------|-------|
| 1 | PHO (X-ray) | 6.0 MV | 100×100 mm | Inline     | 41     | -200 to +200 mm | 0 mm | 100 mm |
| 2 | PHO (X-ray) | 6.0 MV | 100×100 mm | Crossline  | 41     | 0 mm | -200 to +200 mm | 100 mm |
| 3 | PHO (X-ray) | 6.0 MV | 200×200 mm | Inline     | 51     | -250 to +250 mm | 0 mm | 100 mm |

### Dose Profile Characteristics

- **Profile shape**: Symmetric Gaussian-like distribution
- **Central axis**: Normalized to 1.0 (100%)
- **Penumbra**: Smooth falloff from 80% to 20%
- **Tail region**: Low dose (<5%) beyond field edges

### Intentional Differences

The measurement file includes small variations to test gamma analysis:

1. **Dose variations**: ±0.3-0.5% in high dose region
2. **Slight shifts**: Subtle positioning differences
3. **Peak variations**: Up to 0.5% difference at central axis

These variations simulate realistic measurement scenarios:
- Detector positioning uncertainty
- Machine output variations
- Environmental conditions
- Detector calibration drift

## Expected Gamma Analysis Results

With default settings (2%/2mm, 50% cutoff):

- **Pass rates**: Should be 95-99%
- **Failures**: Mainly at field edges where dose gradient is steep
- **Visual inspection**: Close agreement with small deviations visible

### Why Some Points May Fail

1. **Field edges**: Steep dose gradients make gamma analysis more sensitive
2. **Low dose regions**: Below 50% cutoff, but close enough to affect interpolation
3. **Measurement uncertainty**: Realistic variations included in test data

## Using the Test Data

### Quick Validation

```bash
python validate_test_data.py
```

This checks file format and structure without requiring dependencies.

### Full Application Test

```bash
python main.py
```

Then:
1. Click "Open Reference" → select `test_data_reference.txt`
2. Click "Open Measurement" → select `test_data_measurement.txt`
3. Click "Run Gamma"
4. Choose output location for PDF report
5. Review the generated PDF with all 3 analyses

### Expected Console Output

```
Loading reference file: test_data_reference.txt
Total measurements in file: 3
Successfully loaded 3 reference measurements

Loading measurement file: test_data_measurement.txt
Total measurements in file: 3
Successfully loaded 3 measurement measurements

Found 3 matching measurement pairs
Running gamma analysis...
  ✓ Matched: PHO 6.0MV, 100.0mm, depth 100.0mm
  ✓ PHO 6.0MV (Inline): 98.XX% pass rate
  ✓ Matched: PHO 6.0MV, 100.0mm, depth 100.0mm
  ✓ PHO 6.0MV (Crossline): 97.XX% pass rate
  ✓ Matched: PHO 6.0MV, 200.0mm, depth 100.0mm
  ✓ PHO 6.0MV (Inline): 96.XX% pass rate

Analysis complete: 3 successful, 0 failed
```

## Creating Your Own Test Data

To create custom test data:

1. **Header**: Start with `# Number of measurements: N`
2. **For each measurement**:
   - Measurement number
   - Scan parameters (%SCN, %BMT, %FSZ, etc.)
   - Data points (= X Y Z dose)
   - End marker (:EOM)
3. **Footer**: End with `:EOF`

### Important Tags

- `%SCN`: Scan type (PRO = profile)
- `%BMT`: Beam type and energy (e.g., PHO 6.0)
- `%FSZ`: Field size X Y (in mm)
- `%SSD`: Source-to-surface distance (mm)
- `%STS`: Start position X Y Z (mm)
- `%EDS`: End position X Y Z (mm)
- `=`: Data point X Y Z dose (dose is normalized)

### Inline vs Crossline

- **Inline**: X varies, Y = 0 (parallel to gantry rotation axis)
- **Crossline**: X = 0, Y varies (perpendicular to gantry rotation axis)

The application automatically detects scan direction based on which coordinate varies.

## Notes

- Dose values are normalized (typically 0-1.0 range)
- Position units are in millimeters
- All measurements at same depth will be matched if other parameters align
- The tool matches based on: energy, beam type, field size, scan type, and depth (±10mm tolerance)
