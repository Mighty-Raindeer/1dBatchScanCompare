# 1D Batch Scan Compare

One-dimensional scan gamma analysis for annual radiation beam profile comparisons.

## Overview

This tool performs gamma analysis (2%/2mm by default) on 1D radiation beam profiles exported from IBA dosimetry software (OmniPro / MyQA Accept). It compares reference datasets against evaluation datasets and generates a comprehensive PDF report with all analyses.

## Features

- ✅ Batch processing of multiple beam profiles
- ✅ Automatic matching of reference and measurement datasets
- ✅ User-selectable PDF output location
- ✅ Visual feedback on file loading status
- ✅ Detailed pass/fail reporting with color-coded results
- ✅ Comprehensive error handling
- ✅ Clean, refactored codebase
- ✅ Optimized PDF output with improved axis label spacing

## Installation

1. Clone this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. **Export your data**: Export profiles from OmniPro/MyQA Accept as 6.x.x ASCII format
   - **Important**: Energies with and without flattening filter (FFF) are not automatically separated - save them as separate ASCII files

2. **Run the application**:
```bash
python main.py
```

3. **Load files**:
   - Click "Open Reference" to load your baseline/reference measurements
   - Click "Open Measurement" to load your evaluation measurements
   - Status indicators will show when files are successfully loaded

4. **Run analysis**:
   - Click "Run Gamma" (enabled only when both files are loaded)
   - Choose where to save the output PDF
   - The tool will automatically match corresponding profiles and perform gamma analysis

5. **Review results**:
   - A summary dialog shows how many analyses succeeded/failed
   - The PDF contains detailed reports for each matched pair including:
     - Measurement metadata comparison
     - Dose profile overlay
     - Gamma index plot
     - Histogram distribution
     - Color-coded pass rate

## Configuration

Gamma analysis parameters can be modified in `main.py` in the `GammaAnalysisApp.__init__()` method:

```python
self.gamma_config = {
    'dose_percent_threshold': 2,        # Dose difference criterion (%)
    'distance_mm_threshold': 2,         # Distance-to-agreement criterion (mm)
    'lower_percent_dose_cutoff': 50,   # Low dose cutoff (%)
    'interp_fraction': 10,
    'max_gamma': 2,
    'local_gamma': False,               # False = global gamma
}
```

## Requirements

- Python 3.7+
- numpy
- matplotlib
- pandas
- pymedphys

## Testing

The project includes test data and validation scripts for development and verification.

### Run Tests

**Headless test** (no GUI, automated):
```bash
python test_headless.py
```

**Validate test data format**:
```bash
python validate_test_data.py
```

**Test files included**:
- `test_data_reference.txt` - Sample reference measurements
- `test_data_measurement.txt` - Sample evaluation measurements
- See `TEST_DATA_README.md` for detailed test data documentation

## Notes

- The tool automatically matches profiles based on: energy, beam type, field size, scan type, and depth
- Only matched pairs are analyzed - unmatched measurements are skipped
- Pass rate threshold: Green ≥95%, Orange ≥90%, Red <90%
- PDF output includes properly spaced axis labels for clear readability

## Future Improvements

- [ ] GUI controls for gamma parameters
- [ ] Support for additional file formats
- [ ] Statistical summary across all measurements
- [ ] Trend analysis for longitudinal QA 