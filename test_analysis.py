#!/usr/bin/env python3
"""
Pure functional test of gamma analysis logic without GUI dependencies.
"""

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend

import numpy as np
import matplotlib.pyplot as plt
import re
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.gridspec import GridSpec
import pymedphys

# Gamma configuration
GAMMA_CONFIG = {
    'dose_percent_threshold': 2,
    'distance_mm_threshold': 2,
    'lower_percent_dose_cutoff': 50,
    'interp_fraction': 10,
    'max_gamma': 2,
    'random_subset': None,
    'local_gamma': False,
    'ram_available': 2 ** 29
}

def parse_ascii_file(filepath):
    """Parse IBA ASCII file."""
    data = []
    with open(filepath) as file:
        for line in file:
            templist = re.split('\t|#|\n', line)
            cleanlist = list(filter(None, templist))
            if cleanlist:
                data.append(cleanlist)

    return split_and_store(data)

def split_and_store(ref):
    """Extract measurement information from parsed ASCII data."""
    full_list = []
    measurement_list = []

    # Variables to store current measurement parameters
    measurement_number = None
    measurement_type = None
    measurement_date = None
    measurement_time = None
    field_size_x = None
    field_size_y = None
    beam_type = None
    beam_energy = None
    ssd = None
    start_x = start_y = start_z = None
    stop_x = stop_y = stop_z = None

    for line in ref:
        if not line:
            continue

        tag = line[0]

        if tag == ' Measurement number ':
            measurement_number = float(line[1])
        elif tag == '%SCN':
            measurement_type = line[1]
        elif tag == '%DAT':
            measurement_date = line[1]
        elif tag == '%TIM':
            measurement_time = line[1]
        elif tag == '%FSZ':
            field_size_x = float(line[1])
            field_size_y = float(line[2])
        elif tag == '%BMT':
            beam_type = line[1]
            beam_energy = float(line[2])
        elif tag == '%SSD':
            ssd = float(line[1])
        elif tag == '%STS':
            start_x = float(line[1])
            start_y = float(line[2])
            start_z = float(line[3])
        elif tag == '%EDS':
            stop_x = float(line[1])
            stop_y = float(line[2])
            stop_z = float(line[3])
        elif tag == "=":
            x_pos = float(line[1])
            y_pos = float(line[2])
            z_pos = float(line[3])
            dose = float(line[4])
            full_list.append([
                measurement_number, measurement_date, measurement_time,
                measurement_type, beam_type, beam_energy, field_size_x,
                field_size_y, ssd, start_z, stop_z, x_pos, y_pos, z_pos, dose
            ])
        elif tag == ":EOM  ":
            measurement_list.append([
                measurement_number, measurement_date, measurement_time,
                measurement_type, beam_type, beam_energy, field_size_x,
                field_size_y, ssd, start_x, start_y, start_z, stop_z
            ])

    return full_list, measurement_list

def find_matches(measurement_header, reference_header):
    """Find matching measurement pairs."""
    matches = []

    for measure in measurement_header:
        energy = measure[5]
        beam_type = measure[4]
        depth_start = measure[11]
        field_size_x = measure[6]
        field_size_y = measure[7]
        measure_type = measure[3]
        x_check = measure[9]
        y_check = measure[10]

        for reference in reference_header:
            if (measure_type == reference[3] and
                beam_type == reference[4] and
                energy == reference[5] and
                field_size_x == reference[6] and
                abs(depth_start - reference[11]) < 10 and
                ((x_check == 0 and reference[9] == 0) or
                 (y_check == 0 and reference[10] == 0))):

                matches.append([measure[0], reference[0]])
                print(f"  ✓ Matched: {beam_type} {energy}MV, {field_size_x}mm, depth {depth_start}mm")
                break

    return matches

def create_gamma_report(dose_reference, axis_reference, dose_evaluation,
                       axis_evaluation, ref_metadata, mes_metadata, direction, pdf_pages):
    """Create gamma analysis report figure."""
    # Calculate gamma
    gamma = pymedphys.gamma(
        axis_reference, dose_reference,
        axis_evaluation, dose_evaluation,
        **GAMMA_CONFIG
    )

    valid_gamma = gamma[~np.isnan(gamma)]
    pass_ratio = np.sum(valid_gamma <= 1) / len(valid_gamma)

    # Create figure
    fig = plt.figure(figsize=(8, 6), dpi=120, facecolor='w', edgecolor='k')
    fig.suptitle(
        f'Gamma Analysis: {ref_metadata["beam type"]} {ref_metadata["beam energy"]}MV',
        fontsize=14, fontweight='bold'
    )
    gs = GridSpec(2, 2, figure=fig, wspace=.25, hspace=.35)

    # Top panel - metadata
    ax_top = fig.add_subplot(gs[0, :])
    ax_top.axis('off')

    y_start = 0.92
    y_step = 0.08
    col1_x = 0.01
    col2_x = 0.42
    col3_x = 0.65

    # Column headers
    ax_top.text(col2_x, y_start, 'Reference', fontweight='bold', fontsize=11)
    ax_top.text(col3_x, y_start, 'Measurement', fontweight='bold', fontsize=11)

    # Metadata rows
    labels = [
        "Measurement date:",
        "Measurement time:",
        "Measurement type:",
        "Scan direction:",
        "Beam type:",
        "Beam Energy (MV):",
        "Field size (mm):",
        "Depth (mm):"
    ]

    ref_values = [
        ref_metadata['measurement data'],
        ref_metadata['measurement time'],
        ref_metadata['measurement type'],
        direction,
        ref_metadata['beam type'],
        f"{ref_metadata['beam energy']:.1f}",
        f"{ref_metadata['field size x']:.0f}",
        f"{ref_metadata['startZ']:.0f}"
    ]

    mes_values = [
        mes_metadata['measurement data'],
        mes_metadata['measurement time'],
        mes_metadata['measurement type'],
        direction,
        mes_metadata['beam type'],
        f"{mes_metadata['beam energy']:.1f}",
        f"{mes_metadata['field size x']:.0f}",
        f"{mes_metadata['startZ']:.0f}"
    ]

    for i, (label, ref_val, mes_val) in enumerate(zip(labels, ref_values, mes_values)):
        y_pos = y_start - (i + 1) * y_step
        ax_top.text(col1_x, y_pos, label, fontweight='bold')
        ax_top.text(col2_x, y_pos, ref_val)
        ax_top.text(col3_x, y_pos, mes_val)

    # Pass rate
    y_pos = y_start - (len(labels) + 2) * y_step
    ax_top.text(col1_x, y_pos, "Pass rate:", fontweight='bold', fontsize=11)
    pass_color = 'green' if pass_ratio >= 0.95 else 'orange' if pass_ratio >= 0.90 else 'red'
    ax_top.text(col2_x, y_pos, f"{pass_ratio * 100:.2f}%",
               fontweight='bold', fontsize=11, color=pass_color)

    # Dose profile plot
    ax_dose = fig.add_subplot(gs[1, :-1])
    ax_dose.tick_params(direction='in')
    ax_dose.tick_params(axis='x', bottom=True, top=True, labeltop=True)
    ax_dose.minorticks_on()
    ax_dose.set_xlabel('Position (mm)', fontsize=10)
    ax_dose.set_ylabel('Dose (Gy/MU)', fontsize=10)

    max_dose = max(np.max(dose_reference), np.max(dose_evaluation))
    ax_dose.set_ylim([0, max_dose * 1.1])

    # Gamma plot (twin axis)
    ax_gamma = ax_dose.twinx()
    ax_gamma.minorticks_on()
    ax_gamma.set_ylabel('Gamma Index', fontsize=10)
    ax_gamma.set_ylim([0, GAMMA_CONFIG['max_gamma'] * 2.0])

    # Plot curves
    curve_ref = ax_dose.plot(axis_reference, dose_reference, 'k-',
                            label='Reference dose', linewidth=1.5)
    curve_eval = ax_dose.plot(axis_evaluation, dose_evaluation, 'bo',
                             mfc='none', markersize=4, label='Evaluation dose')
    curve_gamma = ax_gamma.plot(
        axis_reference, gamma, 'r*', markersize=3,
        label=f"Gamma ({GAMMA_CONFIG['dose_percent_threshold']}%/"
              f"{GAMMA_CONFIG['distance_mm_threshold']}mm)"
    )

    curves = curve_ref + curve_eval + curve_gamma
    labels_list = [l.get_label() for l in curves]
    ax_dose.legend(curves, labels_list, loc='upper right', fontsize=9)
    ax_dose.grid(True, alpha=0.3)

    # Histogram
    ax_hist = fig.add_subplot(gs[1:, -1])
    num_bins = GAMMA_CONFIG['interp_fraction'] * GAMMA_CONFIG['max_gamma']
    bins = np.linspace(0, GAMMA_CONFIG['max_gamma'], int(num_bins) + 1)
    ax_hist.hist(valid_gamma, bins, density=True, color='skyblue', edgecolor='black')
    ax_hist.set_xlim([0, GAMMA_CONFIG['max_gamma']])
    ax_hist.set_xlabel('Gamma Index', fontsize=10)
    ax_hist.set_ylabel('Probability Density', fontsize=10)
    ax_hist.axvline(x=1, color='red', linestyle='--', linewidth=2, label='Pass threshold')
    ax_hist.legend(fontsize=8)

    # Save to PDF
    pdf_pages.savefig(fig, bbox_inches='tight')
    plt.close(fig)

    print(f"  ✓ {ref_metadata['beam type']} {ref_metadata['beam energy']}MV "
          f"({direction}): {pass_ratio*100:.2f}% pass rate")

    return pass_ratio

def process_gamma_pair(measure_number, reference_number, ref_df, mes_df, pdf_pages):
    """Process a single matched measurement pair."""
    # Extract data for this measurement pair
    ref_data = ref_df.loc[ref_df['measurement number'] == reference_number].copy()
    mes_data = mes_df.loc[mes_df['measurement number'] == measure_number].copy()

    # Normalize to central axis
    ref_center = ref_data['dose'][
        (ref_data['xpos'] > -1) & (ref_data['xpos'] < 1) &
        (ref_data['ypos'] > -1) & (ref_data['ypos'] < 1)
    ]
    mes_center = mes_data['dose'][
        (mes_data['xpos'] > -1) & (mes_data['xpos'] < 1) &
        (mes_data['ypos'] > -1) & (mes_data['ypos'] < 1)
    ]

    ref_center_val = ref_center.mean()
    mes_center_val = mes_center.mean()

    ref_data.loc[:, 'normalized dose'] = ref_data.loc[:, 'dose'] / ref_center_val
    mes_data.loc[:, 'normalized dose'] = mes_data.loc[:, 'dose'] / mes_center_val

    # Sort and remove first/last points
    ref_data_sorted = ref_data.sort_values(by=['xpos', 'ypos'])
    mes_data_sorted = mes_data.sort_values(by=['xpos', 'ypos'])

    ref_data_sorted = ref_data_sorted.iloc[1:-1]
    mes_data_sorted = mes_data_sorted.iloc[1:-1]

    # Extract metadata and arrays
    ref_metadata = ref_data_sorted.iloc[0]
    mes_metadata = mes_data_sorted.iloc[0]

    ref_normal_dose = ref_data_sorted.loc[:, 'normalized dose'].to_numpy()
    ref_xpos = ref_data_sorted.loc[:, 'xpos'].to_numpy()
    ref_ypos = ref_data_sorted.loc[:, 'ypos'].to_numpy()

    mes_normal_dose = mes_data_sorted.loc[:, 'normalized dose'].to_numpy()
    mes_xpos = mes_data_sorted.loc[:, 'xpos'].to_numpy()
    mes_ypos = mes_data_sorted.loc[:, 'ypos'].to_numpy()

    # Determine scan direction
    midpoint = len(ref_xpos) // 2
    if ref_xpos[midpoint] == ref_xpos[0]:
        direction = "Inline"
        pass_ratio = create_gamma_report(
            ref_normal_dose, ref_ypos, mes_normal_dose, mes_ypos,
            ref_metadata, mes_metadata, direction, pdf_pages
        )
    elif ref_ypos[midpoint] == ref_ypos[0]:
        direction = "Crossline"
        pass_ratio = create_gamma_report(
            ref_normal_dose, ref_xpos, mes_normal_dose, mes_xpos,
            ref_metadata, mes_metadata, direction, pdf_pages
        )
    else:
        raise Exception("Cannot determine scan direction")

    return pass_ratio

def main():
    """Run the test."""
    print("="*60)
    print("Gamma Analysis Test (No GUI)")
    print("="*60)

    # Load reference file
    print("\n1. Loading reference file...")
    ref_data, ref_header = parse_ascii_file("test_data_reference.txt")
    ref_df = pd.DataFrame(
        ref_data,
        columns=[
            'measurement number', 'measurement data', 'measurement time',
            'measurement type', 'beam type', 'beam energy', 'field size x',
            'field size y', 'SSD', 'startZ', 'stopZ', 'xpos', 'ypos',
            'zpos', 'dose'
        ]
    )
    print(f"   ✓ Loaded {len(ref_header)} measurements, {len(ref_data)} data points")

    # Load measurement file
    print("\n2. Loading measurement file...")
    mes_data, mes_header = parse_ascii_file("test_data_measurement.txt")
    mes_df = pd.DataFrame(
        mes_data,
        columns=[
            'measurement number', 'measurement data', 'measurement time',
            'measurement type', 'beam type', 'beam energy', 'field size x',
            'field size y', 'SSD', 'startZ', 'stopZ', 'xpos', 'ypos',
            'zpos', 'dose'
        ]
    )
    print(f"   ✓ Loaded {len(mes_header)} measurements, {len(mes_data)} data points")

    # Find matches
    print("\n3. Finding matching pairs...")
    matches = find_matches(mes_header, ref_header)
    print(f"   ✓ Found {len(matches)} matching pairs")

    # Run analysis
    print("\n4. Running gamma analysis...")
    pdf_path = "test_output_gamma_analysis.pdf"
    pdf_pages = PdfPages(pdf_path)

    results = []
    for mes_num, ref_num in matches:
        try:
            pass_rate = process_gamma_pair(mes_num, ref_num, ref_df, mes_df, pdf_pages)
            results.append((mes_num, ref_num, pass_rate, "SUCCESS"))
        except Exception as e:
            results.append((mes_num, ref_num, 0, f"FAILED: {e}"))
            print(f"  ✗ Failed: {e}")

    pdf_pages.close()

    # Summary
    print("\n" + "="*60)
    print("Test Results")
    print("="*60)
    for mes_num, ref_num, pass_rate, status in results:
        if "SUCCESS" in status:
            color = "green" if pass_rate >= 0.95 else "orange" if pass_rate >= 0.90 else "red"
            print(f"✓ Pair ({mes_num} vs {ref_num}): {pass_rate*100:.2f}% pass rate")
        else:
            print(f"✗ Pair ({mes_num} vs {ref_num}): {status}")

    successful = sum(1 for r in results if "SUCCESS" in r[3])
    print(f"\n{successful}/{len(matches)} analyses completed successfully")
    print(f"PDF saved: {pdf_path}")
    print("="*60)

    return successful == len(matches)

if __name__ == "__main__":
    import sys
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
