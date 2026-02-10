import numpy as np
import matplotlib.pyplot as plt
import re
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.gridspec import GridSpec
import pymedphys


class GammaAnalysisApp:
    """Application for performing gamma analysis on 1D radiation beam profiles."""

    def __init__(self):
        # Gamma analysis parameters
        self.gamma_config = {
            'dose_percent_threshold': 2,
            'distance_mm_threshold': 2,
            'lower_percent_dose_cutoff': 50,
            'interp_fraction': 10,
            'max_gamma': 2,
            'random_subset': None,
            'local_gamma': False,
            'ram_available': 2 ** 29
        }

        # Data storage
        self.reference_data_full = None
        self.reference_header = None
        self.reference_dataframe = None
        self.measurement_data_full = None
        self.measurement_header = None
        self.measurement_dataframe = None
        self.pdf_pages = None

        # Suppress pandas chained assignment warning
        pd.options.mode.chained_assignment = None

        # Build GUI
        self._build_gui()

    def _build_gui(self):
        """Build the Tkinter GUI."""
        self.window = tk.Tk()
        self.window.title("ASCII Gamma Analysis")
        self.window.geometry("600x250")
        self.window.rowconfigure(0, minsize=200, weight=1)
        self.window.columnconfigure([0, 1, 2], minsize=200, weight=1)

        # Reference frame
        fr_reference = tk.LabelFrame(
            self.window, relief=tk.RAISED, text="Reference ASCII",
            width=200, height=200
        )
        fr_reference.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        self.btn_ref_open = tk.Button(
            fr_reference, text="Open Reference",
            command=self.open_reference_file
        )
        self.btn_ref_open.pack(pady=20)

        self.lbl_ref_status = tk.Label(fr_reference, text="No file loaded", fg="gray")
        self.lbl_ref_status.pack()

        # Measurement frame
        fr_measurement = tk.LabelFrame(
            self.window, relief=tk.RAISED, text="Measurement ASCII",
            width=200, height=200
        )
        fr_measurement.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        self.btn_mes_open = tk.Button(
            fr_measurement, text="Open Measurement",
            command=self.open_measurement_file
        )
        self.btn_mes_open.pack(pady=20)

        self.lbl_mes_status = tk.Label(fr_measurement, text="No file loaded", fg="gray")
        self.lbl_mes_status.pack()

        # Gamma analysis frame
        fr_gamma = tk.LabelFrame(
            self.window, relief=tk.RAISED, text="Run Gamma Analysis",
            width=200, height=200
        )
        fr_gamma.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")

        self.btn_run_gamma = tk.Button(
            fr_gamma, text="Run Gamma",
            command=self.run_gamma_analysis,
            state=tk.DISABLED
        )
        self.btn_run_gamma.pack(pady=20)

        # Display gamma parameters
        params_text = f"{self.gamma_config['dose_percent_threshold']}%/{self.gamma_config['distance_mm_threshold']}mm\n"
        params_text += f"Cutoff: {self.gamma_config['lower_percent_dose_cutoff']}%"
        lbl_params = tk.Label(fr_gamma, text=params_text, fg="blue", font=("Arial", 9))
        lbl_params.pack()

    def _empty_list_remove(self, input_list):
        """Remove empty elements from a list."""
        return [ele for ele in input_list if len(ele) > 0]

    def _parse_ascii_file(self, filepath):
        """Parse IBA ASCII file and extract measurement data."""
        data = []
        try:
            with open(filepath) as file:
                for line in file:
                    templist = re.split('\t|#|\n', line)
                    cleanlist = list(filter(None, templist))
                    data.append(cleanlist)
        except Exception as e:
            raise Exception(f"Failed to read file: {str(e)}")

        data = self._empty_list_remove(data)
        return self._split_and_store(data)

    def _split_and_store(self, ref):
        """Extract measurement information from parsed ASCII data."""
        if not ref or len(ref) == 0:
            raise Exception("No data found in file")

        total_measure_num = ref[0][1]
        print(f"Total measurements in file: {total_measure_num}")

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

    def open_reference_file(self):
        """Open and parse reference ASCII file."""
        filepath = filedialog.askopenfilename(
            title='Select reference ASCII file',
            filetypes=[("ASCII files", "*.txt *.asc"), ("All files", "*.*")]
        )

        if not filepath:
            return

        try:
            print(f"\nLoading reference file: {filepath}")
            data_full, header = self._parse_ascii_file(filepath)

            self.reference_data_full = data_full
            self.reference_header = header
            self.reference_dataframe = pd.DataFrame(
                data_full,
                columns=[
                    'measurement number', 'measurement data', 'measurement time',
                    'measurement type', 'beam type', 'beam energy', 'field size x',
                    'field size y', 'SSD', 'startZ', 'stopZ', 'xpos', 'ypos',
                    'zpos', 'dose'
                ]
            )

            self.lbl_ref_status.config(
                text=f"✓ Loaded ({len(header)} measurements)",
                fg="green"
            )
            self._update_gamma_button_state()
            print(f"Successfully loaded {len(header)} reference measurements")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load reference file:\n{str(e)}")
            self.lbl_ref_status.config(text="✗ Load failed", fg="red")

    def open_measurement_file(self):
        """Open and parse measurement ASCII file."""
        filepath = filedialog.askopenfilename(
            title='Select measurement ASCII file',
            filetypes=[("ASCII files", "*.txt *.asc"), ("All files", "*.*")]
        )

        if not filepath:
            return

        try:
            print(f"\nLoading measurement file: {filepath}")
            data_full, header = self._parse_ascii_file(filepath)

            self.measurement_data_full = data_full
            self.measurement_header = header
            self.measurement_dataframe = pd.DataFrame(
                data_full,
                columns=[
                    'measurement number', 'measurement data', 'measurement time',
                    'measurement type', 'beam type', 'beam energy', 'field size x',
                    'field size y', 'SSD', 'startZ', 'stopZ', 'xpos', 'ypos',
                    'zpos', 'dose'
                ]
            )

            self.lbl_mes_status.config(
                text=f"✓ Loaded ({len(header)} measurements)",
                fg="green"
            )
            self._update_gamma_button_state()
            print(f"Successfully loaded {len(header)} measurement measurements")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load measurement file:\n{str(e)}")
            self.lbl_mes_status.config(text="✗ Load failed", fg="red")

    def _update_gamma_button_state(self):
        """Enable gamma button only when both files are loaded."""
        if (self.reference_dataframe is not None and
            self.measurement_dataframe is not None):
            self.btn_run_gamma.config(state=tk.NORMAL)

    def run_gamma_analysis(self):
        """Run gamma analysis on all matching measurement pairs."""
        # Ask user for PDF output location
        pdf_path = filedialog.asksaveasfilename(
            title='Save gamma analysis PDF as',
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            initialfile="gamma_analysis.pdf"
        )

        if not pdf_path:
            return

        try:
            self.pdf_pages = PdfPages(pdf_path)

            # Find matching measurement pairs
            test_matches = self._find_matching_tests()

            if not test_matches:
                messagebox.showwarning(
                    "No Matches",
                    "No matching measurement pairs found.\n\n"
                    "Ensure reference and measurement files contain matching:\n"
                    "- Energy\n- Beam type\n- Field size\n- Scan type\n- Depth"
                )
                self.pdf_pages.close()
                return

            print(f"\nFound {len(test_matches)} matching measurement pairs")
            print("Running gamma analysis...")

            successful = 0
            failed = 0

            # Process each matching pair
            for measure_num, ref_num in test_matches:
                try:
                    self._process_gamma_pair(measure_num, ref_num)
                    successful += 1
                except Exception as e:
                    failed += 1
                    print(f"  ✗ Failed for measurement {measure_num}: {str(e)}")

            self.pdf_pages.close()

            # Show results
            message = f"Gamma analysis complete!\n\n"
            message += f"Successful: {successful}/{len(test_matches)}\n"
            if failed > 0:
                message += f"Failed: {failed}/{len(test_matches)}\n\n"
                message += "Check console for error details."
            message += f"\n\nPDF saved to:\n{pdf_path}"

            messagebox.showinfo("Complete", message)
            print(f"\n{'='*60}")
            print(f"Analysis complete: {successful} successful, {failed} failed")
            print(f"PDF saved: {pdf_path}")
            print(f"{'='*60}\n")

        except Exception as e:
            if self.pdf_pages:
                self.pdf_pages.close()
            messagebox.showerror("Error", f"Gamma analysis failed:\n{str(e)}")

    def _find_matching_tests(self):
        """Find matching measurement pairs between reference and measurement datasets."""
        matches = []

        for measure in self.measurement_header:
            energy = measure[5]
            beam_type = measure[4]
            depth_start = measure[11]
            field_size_x = measure[6]
            field_size_y = measure[7]
            measure_type = measure[3]
            x_check = measure[9]
            y_check = measure[10]

            for reference in self.reference_header:
                # Check if measurements match on key parameters
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

    def _process_gamma_pair(self, measure_number, reference_number):
        """Process a single matched measurement pair."""
        # Extract data for this measurement pair
        ref_data = self.reference_dataframe.loc[
            self.reference_dataframe['measurement number'] == reference_number
        ].copy()
        mes_data = self.measurement_dataframe.loc[
            self.measurement_dataframe['measurement number'] == measure_number
        ].copy()

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
            self._create_gamma_report(
                ref_normal_dose, ref_ypos, mes_normal_dose, mes_ypos,
                ref_metadata, mes_metadata, direction
            )
        elif ref_ypos[midpoint] == ref_ypos[0]:
            direction = "Crossline"
            self._create_gamma_report(
                ref_normal_dose, ref_xpos, mes_normal_dose, mes_xpos,
                ref_metadata, mes_metadata, direction
            )
        else:
            raise Exception("Cannot determine scan direction (neither inline nor crossline)")

    def _create_gamma_report(self, dose_reference, axis_reference, dose_evaluation,
                            axis_evaluation, ref_metadata, mes_metadata, direction):
        """Create gamma analysis report figure."""
        # Calculate gamma
        gamma = pymedphys.gamma(
            axis_reference, dose_reference,
            axis_evaluation, dose_evaluation,
            **self.gamma_config
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
        ax_dose.tick_params(direction='in', labelsize=9)
        ax_dose.tick_params(axis='x', bottom=True, top=True, labeltop=True)
        ax_dose.minorticks_on()
        ax_dose.set_xlabel('Position (mm)', fontsize=10)
        ax_dose.set_ylabel('Dose (Gy/MU)', fontsize=10, labelpad=15)

        max_dose = max(np.max(dose_reference), np.max(dose_evaluation))
        ax_dose.set_ylim([0, max_dose * 1.1])

        # Gamma plot (twin axis)
        ax_gamma = ax_dose.twinx()
        ax_gamma.minorticks_on()
        ax_gamma.tick_params(labelsize=9)
        ax_gamma.set_ylabel('Gamma Index', fontsize=10, labelpad=15)
        ax_gamma.set_ylim([0, self.gamma_config['max_gamma'] * 2.0])

        # Plot curves
        curve_ref = ax_dose.plot(axis_reference, dose_reference, 'k-',
                                label='Reference dose', linewidth=1.5)
        curve_eval = ax_dose.plot(axis_evaluation, dose_evaluation, 'bo',
                                 mfc='none', markersize=4, label='Evaluation dose')
        curve_gamma = ax_gamma.plot(
            axis_reference, gamma, 'r*', markersize=3,
            label=f"Gamma ({self.gamma_config['dose_percent_threshold']}%/"
                  f"{self.gamma_config['distance_mm_threshold']}mm)"
        )

        curves = curve_ref + curve_eval + curve_gamma
        labels_list = [l.get_label() for l in curves]
        ax_dose.legend(curves, labels_list, loc='upper right', fontsize=9)
        ax_dose.grid(True, alpha=0.3)

        # Histogram
        ax_hist = fig.add_subplot(gs[1:, -1])
        num_bins = self.gamma_config['interp_fraction'] * self.gamma_config['max_gamma']
        bins = np.linspace(0, self.gamma_config['max_gamma'], int(num_bins) + 1)
        ax_hist.hist(valid_gamma, bins, density=True, color='skyblue', edgecolor='black')
        ax_hist.set_xlim([0, self.gamma_config['max_gamma']])
        ax_hist.set_xlabel('Gamma Index', fontsize=10)
        ax_hist.set_ylabel('Probability Density', fontsize=10)
        ax_hist.axvline(x=1, color='red', linestyle='--', linewidth=2, label='Pass threshold')
        ax_hist.legend(fontsize=8)

        # Save to PDF
        fig.tight_layout(rect=[0, 0, 1, 0.96])  # Adjust layout, leaving room for title
        self.pdf_pages.savefig(fig, bbox_inches='tight')
        plt.close(fig)

        print(f"  ✓ {ref_metadata['beam type']} {ref_metadata['beam energy']}MV "
              f"({direction}): {pass_ratio*100:.2f}% pass rate")

    def run(self):
        """Start the application."""
        self.window.mainloop()


if __name__ == "__main__":
    app = GammaAnalysisApp()
    app.run()
