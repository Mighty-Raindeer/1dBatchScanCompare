# 1D Batch Scan Compare

Annual or baseline-versus-current beam-profile QA often means comparing many 1D scans one file at a time. This Python application batch-compares radiation beam profiles exported from IBA dosimetry software (OmniPro / MyQA Accept ASCII 6.x), matches corresponding scans automatically, runs gamma analysis, and writes a single consolidated PDF report.

## What it compares

- **Reference datasets**: baseline or prior-year 1D profiles (OmniPro / MyQA Accept ASCII)
- **Evaluation datasets**: current measurements in the same ASCII format
- **Matching keys**: energy, beam type, field size, scan type (inline/crossline), and depth (±10 mm tolerance)
- **Analysis**: global gamma by default (2%/2 mm, 50% low-dose cutoff; configurable in `main.py`)
- **Report**: one PDF containing, for each matched pair, metadata comparison, dose-profile overlay, gamma-index plot, histogram, and color-coded pass rate

> **Screenshot placeholder**  
> *Insert an application window screenshot here (reference/measurement loaded, Run Gamma enabled). Do not commit a fabricated image.*

> **Example report placeholder**  
> *Insert one representative PDF report page here (or link a checked-in example). Do not commit a fabricated image.*

FFF and flattened beams are not distinguished in ASCII exports; keep those measurement sets in separate files before loading.

## Features

- Batch gamma analysis across all matched profile pairs in the loaded files
- Automatic matching of reference and measurement datasets by energy, beam type, field size, scan type, and depth
- User-selectable PDF output location
- GUI status indicators when reference and measurement files load successfully
- Per-pair pass/fail reporting with color-coded pass rates (green ≥95%, orange ≥90%, red <90%)
- Continues through the batch when individual pairs fail so remaining matches still produce report pages
- PDF figures with spaced axis labels for readability

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

## Clinical-use notice

This software is provided for research, education, and development. It is not a medical device and has not been validated for clinical decision-making.

Users are responsible for independent code review, testing, commissioning, verification of calculations and outputs, and compliance with applicable institutional policies before using any portion of the software in a clinical environment.

No patient information or protected health information is included in this repository. Examples and test data are synthetic or de-identified unless explicitly documented otherwise.

## Future Improvements

- [ ] GUI controls for gamma parameters
- [ ] Support for additional file formats
- [ ] Statistical summary across all measurements
- [ ] Trend analysis for longitudinal QA
