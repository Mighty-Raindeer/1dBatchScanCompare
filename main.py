import numpy as np
import matplotlib.pyplot as plt
import csv
import pymedphys
import urllib.request
import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename, askdirectory
import re
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.gridspec import GridSpec

"""Requesting files from the user"""
global measuredatafull, measureheader, referencedatafull, referenceheader, referencedataframe, measurementdataframe
pd.options.mode.chained_assignment = None  # default='warn'
pp = PdfPages('test.pdf')


def empty_list_remove(input_list):
    new_list = []
    for ele in input_list:
        if len(ele) > 0:
            new_list.append(ele)
    return new_list


def openreferenceasciifile():
    filepath = askopenfilename(title='Select reference ascii file')
    print(filepath)
    reference = []
    global referenceheader, referencedatafull, referencedataframe
    with open(filepath) as file:
        for line in file:
            templist = re.split('\t|#|\n', line)
            cleanlist = list(filter(None, templist))
            reference.append(cleanlist)

    res = empty_list_remove(reference)
    referencedatafull, referenceheader = splitandstore(res)
    referencedataframe = pd.DataFrame(referencedatafull,
                                      columns=['measurement number', 'measurement data', 'measurement time',
                                               'measurement type', 'beam type', 'beam energy', 'field size x',
                                               'field size y', 'SSD', 'startZ', 'stopZ', 'xpos', 'ypos', 'zpos',
                                               'dose'])
    # print(referencedatafull)
    # print(referencedataframe)
    # print(referenceheader)


def openmeasurementasciifile():
    filepath = askopenfilename(title='Select measurement ascii file')
    print(filepath)
    measurement = open(filepath, 'r').readlines
    measurement = []
    global measuredatafull, measureheader, measurementdataframe
    with open(filepath) as file:
        for line in file:
            templist = re.split('\t|#|\n', line)
            cleanlist = list(filter(None, templist))
            measurement.append(cleanlist)
    # print(measurement)
    res = empty_list_remove(measurement)
    # print(res)
    measuredatafull, measureheader = splitandstore(res)
    measurementdataframe = pd.DataFrame(measuredatafull,
                                        columns=['measurement number', 'measurement data', 'measurement time',
                                                 'measurement type', 'beam type', 'beam energy', 'field size x',
                                                 'field size y', 'SSD', 'startZ', 'stopZ', 'xpos', 'ypos', 'zpos',
                                                 'dose'])
    # print(measuredatafull)
    # print(measurementdataframe)
    # print(measureheader)


"""Read and process the ASCII files based on IBA syntax"""


def splitandstore(ref):
    """I want this to create a large matrix from the data in the ascii file. This matrix should contain [measurement
    #, energy, radiation type, scan type, field size x, field size y, measurment data, measurement time, x, y, z,
    reading, normalized reading] This will be a large matrix of 13 categories with thousands of rows. """
    """we converted the ascii file into a list of lists now we need to extract information"""
    totalmeasurenumb = ref[0][1]
    print(totalmeasurenumb)
    fulllist = []
    MeasurementList = []
    for list in ref:
        if list[0] == ' Measurement number ':
            measurementnumber = float(list[1])
        elif list[0] == '%SCN ':
            measurementtype = list[1]
        elif list[0] == '%DAT ':
            measurementdate = list[1]
        elif list[0] == '%TIM ':
            measurementtime = list[1]
        elif list[0] == '%FSZ ':
            fieldsizeX = float(list[1])
            fieldsizeY = float(list[2])
        elif list[0] == '%BMT ':
            Beamtype = list[1]
            BeamEnergy = float(list[2])
        elif list[0] == '%SSD ':
            SSD = float(list[1])
        elif list[0] == '%STS ':
            startX = float(list[1])
            startY = float(list[2])
            startZ = float(list[3])
        elif list[0] == '%EDS ':
            stopX = float(list[1])
            stopY = float(list[2])
            stopZ = float(list[3])
        elif list[0] == "= ":
            xpos = float(list[1])
            ypos = float(list[2])
            zpos = float(list[3])
            dose = float(list[4])
            # print(xpos,ypos,zpos,dose)
            fulllist.append(
                [measurementnumber, measurementdate, measurementtime, measurementtype, Beamtype, BeamEnergy, fieldsizeX,
                 fieldsizeY, SSD, startZ, stopZ, xpos, ypos, zpos, dose])

        elif list[0] == ":EOM  ":
            MeasurementList.append(
                [measurementnumber, measurementdate, measurementtime, measurementtype, Beamtype, BeamEnergy, fieldsizeX,
                 fieldsizeY, SSD, startX, startY, startZ, stopZ])
    # print(fulllist, MeasurementList)
    return fulllist, MeasurementList


def splitandstore2(ref):
    """I want this to create a large matrix from the data in the ascii file. This matrix should contain [measurement
    #, energy, radiation type, scan type, field size x, field size y, measurment data, measurement time, x, y, z,
    reading, normalized reading] This will be a large matrix of 13 categories with thousands of rows. """
    """we converted the ascii file into a list of lists now we need to extract information"""
    columnlist = ['measurementnumber', 'measurementdate', 'measurementtime', 'measurementtype', 'Beamtype',
                  'BeamEnergy', 'fieldsizeX',
                  'fieldsizeY', 'SSD', 'startX', 'startY', 'startZ', 'stopZ', 'X', 'Y', 'Z', 'dose']
    df = pd.DataFrame(columns=columnlist)

    totalmeasurenumb = ref[0][1]
    print(totalmeasurenumb)
    fulllist = []
    MeasurementList = []
    for list in ref:
        if list[0] == ' Measurement number ':
            measurementnumber = float(list[1])
            # print(measurementnumber)
        elif list[0] == '%SCN ':
            measurementtype = list[1]
            # print(measurementtype)
        elif list[0] == '%DAT ':
            measurementdate = list[1]
            # print(measurementdate)
        elif list[0] == '%TIM ':
            measurementtime = list[1]
            # print(measurementtime)
        elif list[0] == '%FSZ ':
            fieldsizeX = float(list[1])
            fieldsizeY = float(list[2])
            # print(fieldsizeX,fieldsizeY)
        elif list[0] == '%BMT ':
            Beamtype = list[1]
            BeamEnergy = float(list[2])
            # print(BeamEnergy, Beamtype)
        elif list[0] == '%SSD ':
            SSD = float(list[1])
            # print(SSD)
        elif list[0] == '%STS ':
            startX = float(list[1])
            startY = float(list[2])
            startZ = float(list[3])
        elif list[0] == '%EDS ':
            stopX = float(list[1])
            stopY = float(list[2])
            stopZ = float(list[3])
        elif list[0] == "= ":
            xpos = float(list[1])
            ypos = float(list[2])
            zpos = float(list[3])
            dose = float(list[4])
            # print(xpos,ypos,zpos,dose)
            fulllist.append(
                [measurementnumber, measurementdate, measurementtime, measurementtype, Beamtype, BeamEnergy, fieldsizeX,
                 fieldsizeY, SSD, startZ, stopZ, xpos, ypos, zpos, dose])
            df2 = pd.DataFrame([[measurementnumber, measurementdate, measurementtime, measurementtype, Beamtype,
                                 BeamEnergy, fieldsizeX,
                                 fieldsizeY, SSD, startX, startY, startZ, stopZ, xpos, ypos, zpos, dose]])
            pd.concat([df, df2])

        elif list[0] == ":EOM  ":
            MeasurementList.append(
                [measurementnumber, measurementdate, measurementtime, measurementtype, Beamtype, BeamEnergy, fieldsizeX,
                 fieldsizeY, SSD, startX, startY, startZ, stopZ])
    # print(fulllist, MeasurementList)
    return df, MeasurementList


def gammacalc():
    print("gamma calc subroutine, call on each matching test then run physics gamma")
    """First lets check that there is a reference and measurement dataset"""
    """Using the measurement data we want to find the matching data set from the reference. This should check for energy, field size, depth and scan type? """
    global measuredatafull, measureheader, referencedatafull, referenceheader

    testmatch = []
    for measure in measureheader:
        energycheck = measure[5]
        typecheck = measure[4]
        depthcheckstart = measure[11]
        fieldsizecheckX = measure[6]
        fieldsizecheckY = measure[7]
        measuretype = measure[3]
        xcheck = measure[9]
        ycheck = measure[10]
        for reference in referenceheader:
            if measuretype == reference[3] and typecheck == reference[4] and energycheck == reference[
                5] and fieldsizecheckX == reference[6] and abs(depthcheckstart - reference[11]) < 10 and (
                    (xcheck == 0 and reference[9] == 0) or (ycheck == 0 and reference[10] == 0)):
                testmatch.append([measure[0], reference[0]])
                print(measure, reference)
                print("matched")
            else:
                print('no match')
                print(measure, reference)

    print(testmatch)
    for group in testmatch:
        measurenumber = group[0]
        referencenumber = group[1]
        refdata = referencedataframe.loc[referencedataframe['measurement number'] == referencenumber]
        mesdata = measurementdataframe.loc[measurementdataframe['measurement number'] == measurenumber]
        refcenter = refdata['dose'][
            (refdata['xpos'] > -1) & (refdata['xpos'] < 1) & (refdata['ypos'] > -1) & (refdata['ypos'] < 1)]
        meascenter = mesdata['dose'][
            (mesdata['xpos'] > -1) & (mesdata['xpos'] < 1) & (mesdata['ypos'] > -1) & (mesdata['ypos'] < 1)]
        refcenterval = refcenter.mean()
        meascenterval = meascenter.mean()
        refdata.loc[:, 'normalized dose'] = (refdata.loc[:, 'dose'] / refcenterval)
        mesdata.loc[:, 'normalized dose'] = (mesdata.loc[:, 'dose'] / meascenterval)


        refdatasorted = refdata.sort_values(by=['xpos', 'ypos'])
        mesdatasorted = mesdata.sort_values(by=['xpos', 'ypos'])
        refdatasorted = refdatasorted.drop(index=refdatasorted.first_valid_index())
        refdatasorted = refdatasorted.drop(index=refdatasorted.last_valid_index())
        mesdatasorted = mesdatasorted.drop(index=mesdatasorted.first_valid_index())
        mesdatasorted = mesdatasorted.drop(index=mesdatasorted.last_valid_index())



        refmetadata = refdatasorted.iloc[0]
        mesmetadata = mesdatasorted.iloc[0]
        refnormaldosenp = refdatasorted.loc[:, 'normalized dose'].to_numpy()
        refxposnp = refdatasorted.loc[:, 'xpos'].to_numpy()
        refyposnp = refdatasorted.loc[:, 'ypos'].to_numpy()
        mesnormaldosenp = mesdatasorted.loc[:, 'normalized dose'].to_numpy()
        mesxposnp = mesdatasorted.loc[:, 'xpos'].to_numpy()
        mesyposnp = mesdatasorted.loc[:, 'ypos'].to_numpy()
        print(refmetadata)
        print(mesmetadata)
        if refxposnp[round(len(refxposnp) / 2)] == refxposnp[0]:
            print("this is an inline measurement")

            gammareport(refnormaldosenp, refyposnp, mesnormaldosenp, mesyposnp, refmetadata, mesmetadata, "Inline")

        elif refyposnp[round(len(refyposnp) / 2)] == refyposnp[0]:
            print("this is a crossline")

            gammareport(refnormaldosenp, refxposnp, mesnormaldosenp, mesxposnp, refmetadata, mesmetadata, "Crossline")
        else:
            print("I have no idea what is happening here...")

    print('All scans completed')

    pp.close()


def gammareport(dose_reference, axis_reference, dose_evaluation, axis_evaluation, refmetadata, mesmetadata, direction):
    try:

        gamma_options = {
            'dose_percent_threshold': 2,
            'distance_mm_threshold': 2,
            'lower_percent_dose_cutoff': 50,
            'interp_fraction': 10,  # Should be 10 or more for more accurate results
            'max_gamma': 2,
            'random_subset': None,
            'local_gamma': False,  # False indicates global gamma is calculated
            'ram_available': 2 ** 29  # 1/2 GB
        }
        # for global dose normalization, the maximum reference dose is used
        # but in TG218, it said usually the prescribed dose or the maximum dose in a plan (evaluation) is used
        gamma = pymedphys.gamma(
            axis_reference, dose_reference,
            axis_evaluation, dose_evaluation,
            **gamma_options)
        valid_gamma = gamma[~np.isnan(gamma)]
        print('# of reference points with a valid gamma {0}'.format(len(valid_gamma)))
        num_bins = (
                gamma_options['interp_fraction'] * gamma_options['max_gamma'])
        bins = np.linspace(0, gamma_options['max_gamma'], num_bins + 1)

        if gamma_options['local_gamma']:
            gamma_norm_condition = 'Local gamma'
        else:
            gamma_norm_condition = 'Global gamma'

        pass_ratio = np.sum(valid_gamma <= 1) / len(valid_gamma)
        max_ref_dose = np.max(dose_reference)  # max reference dose
        max_eva_dose = np.max(dose_evaluation)  # max evaluation dose
        lower_dose_cutoff = gamma_options['lower_percent_dose_cutoff'] / 100 * max_ref_dose
        print(pass_ratio)

        figure_2 = plt.figure(2, figsize=(8, 6), dpi=120, facecolor='w', edgecolor='k')
        figure_2.suptitle(
            'Gamma evaluation for '.format(refmetadata['beam type']),
            fontsize=12)
        gs = GridSpec(2, 2, figure=figure_2, wspace=.25)
        # gs.tight_layout(pad=1.5)

        verticaltexti = 0.92
        verticaltextpad = 0.08
        catcolumnalgin = 0.01
        refcolumnalign = 0.42
        mescolumnalign = 0.65

        ax_top = figure_2.add_subplot(gs[0, :])
        # ax_top.text(0.01,verticaltexti,'Reference Test')
        # ax_top.text(0.01, verticaltexti -  verticaltextpad, 'Reference Test')
        ax_top.text(catcolumnalgin, verticaltexti - 2 * verticaltextpad, "measurement date: ")
        ax_top.text(catcolumnalgin, verticaltexti - 3 * verticaltextpad, "Measurement time: ")
        ax_top.text(catcolumnalgin, verticaltexti - 4 * verticaltextpad, "Mesasurement type: ")
        ax_top.text(catcolumnalgin, verticaltexti - 5 * verticaltextpad, "scan direction: ")
        ax_top.text(catcolumnalgin, verticaltexti - 6 * verticaltextpad, "Beam type: ")
        ax_top.text(catcolumnalgin, verticaltexti - 7 * verticaltextpad, "Beam Energy (MV): ")
        ax_top.text(catcolumnalgin, verticaltexti - 8 * verticaltextpad, "Field size (mm): ")
        ax_top.text(catcolumnalgin, verticaltexti - 9 * verticaltextpad, "Depth (mm): ")

        ax_top.text(refcolumnalign, verticaltexti, 'Reference Test')
        # ax_top.text(refcolumnalign, verticaltexti -  verticaltextpad, 'Reference Test')
        ax_top.text(refcolumnalign, verticaltexti - 2 * verticaltextpad, refmetadata['measurement data'])
        ax_top.text(refcolumnalign, verticaltexti - 3 * verticaltextpad, refmetadata['measurement time'])
        ax_top.text(refcolumnalign, verticaltexti - 4 * verticaltextpad, refmetadata['measurement type'])
        ax_top.text(refcolumnalign, verticaltexti - 5 * verticaltextpad, direction)
        ax_top.text(refcolumnalign, verticaltexti - 6 * verticaltextpad, refmetadata['beam type'])
        ax_top.text(refcolumnalign, verticaltexti - 7 * verticaltextpad, refmetadata['beam energy'])
        ax_top.text(refcolumnalign, verticaltexti - 8 * verticaltextpad, refmetadata['field size x'])
        ax_top.text(refcolumnalign, verticaltexti - 9 * verticaltextpad, refmetadata['startZ'])

        ax_top.text(mescolumnalign, verticaltexti, 'Measurement Test')
        # ax_top.text(mescolumnalign, verticaltexti -  verticaltextpad, 'Reference Test')
        ax_top.text(mescolumnalign, verticaltexti - 2 * verticaltextpad, mesmetadata['measurement data'])
        ax_top.text(mescolumnalign, verticaltexti - 3 * verticaltextpad, mesmetadata['measurement time'])
        ax_top.text(mescolumnalign, verticaltexti - 4 * verticaltextpad, mesmetadata['measurement type'])
        ax_top.text(mescolumnalign, verticaltexti - 5 * verticaltextpad, direction)
        ax_top.text(mescolumnalign, verticaltexti - 6 * verticaltextpad, mesmetadata['beam type'])
        ax_top.text(mescolumnalign, verticaltexti - 7 * verticaltextpad, mesmetadata['beam energy'])
        ax_top.text(mescolumnalign, verticaltexti - 8 * verticaltextpad, mesmetadata['field size x'])
        ax_top.text(mescolumnalign, verticaltexti - 9 * verticaltextpad, mesmetadata['startZ'])

        ax_top.text(catcolumnalgin, verticaltexti - 11 * verticaltextpad, "Pass rate%: ")
        ax_top.text(refcolumnalign, verticaltexti - 11 * verticaltextpad, round((pass_ratio / 1) * 100, 2))

        ax_1 = figure_2.add_subplot(gs[1, :-1])
        ax_1.tick_params(direction='in')
        ax_1.tick_params(axis='x', bottom='on', top='on')
        ax_1.tick_params(labeltop='on')
        ax_1.minorticks_on()
        ax_1.set_xlabel('x(mm)', fontsize=10, labelpad=2)
        ax_1.set_ylabel('dose(Gy/MU)', fontsize=10, labelpad=2)
        ax_1.set_ylim([0, max(max_ref_dose, max_eva_dose) * 1.1])

        ax_2 = ax_1.twinx()
        ax_2.minorticks_on()
        ax_2.set_ylabel('gamma index', fontsize=10, labelpad=2)
        ax_2.set_ylim([0, gamma_options['max_gamma'] * 2.0])

        curve_0 = ax_1.plot(axis_reference, dose_reference, 'k-', label='reference dose')
        curve_1 = ax_1.plot(axis_evaluation, dose_evaluation, 'bo', mfc='none', markersize=5, label='evaluation dose')
        curve_2 = ax_2.plot(axis_reference, gamma, 'r*',
                            label=f"gamma ({gamma_options['dose_percent_threshold']}%/{gamma_options['distance_mm_threshold']}mm)")
        curves = curve_0 + curve_1 + curve_2

        labels = [l.get_label() for l in curves]
        ax_1.legend(curves, labels, loc='center left')
        ax_1.grid(True)

        ax_3 = figure_2.add_subplot(gs[1:, -1])
        ax_3.hist(valid_gamma, bins, density=True)  # y value is probability density in each bin
        # plt.hist(valid_gamma, bins, density=False) #y value is counts in each bin
        ax_3.set_xlim([0, gamma_options['max_gamma']])
        ax_3.set_xlabel('gamma index of reference point', fontsize=10, labelpad=2)  # FG
        ax_3.set_ylabel('probability density', fontsize=10, labelpad=2)
        # plt.ylabel('counts')
        ax_3.vlines(x=[1], ymin=0, ymax=1, colors='purple', ls='--', lw=2, label='target')
        # plt.savefig('1D_{0}_histogram.png'.format(gamma_norm_condition), dpi=300)  # plt.savefig() must be before plt.show()
        # show gamma index together with dose points

        # save figure first and show it
        figureName = '1D dose_reference_evaluation_{0} index.png'.format(gamma_norm_condition)
        plt.savefig(figureName)  # plt.savefig() must be before plt.show()
        #plt.show()

        # joinfig = plt.figure()
        # axis1 = joinfig.add_subplot(211)
        # axis1.
        pp.savefig(figure_2)
        plt.close(figure_2)
       
        print("success")


    except Exception as e:
        pass
        print("error occured for measurements:  ", e)


""" start of the tkinter window build and run"""
window = tk.Tk()
window.title("ASCI gamma analysis")
window.rowconfigure(0, minsize=200, weight=1)
window.columnconfigure(1, minsize=200, weight=1)

fr_Reference = tk.LabelFrame(window, relief=tk.RAISED, text="Reference ASCII", width=200,
                             height=200)
fr_Reference.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)
btn_ref_open = tk.Button(fr_Reference, text="open Reference", command=openreferenceasciifile)
btn_ref_open.place(x=50, y=50)

fr_Measurement = tk.LabelFrame(window, relief=tk.RAISED, text="Measurement ASCII", width=200,
                               height=200)
fr_Measurement.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)
btn_mes_open = tk.Button(fr_Measurement, text="open measurement", command=openmeasurementasciifile)
btn_mes_open.place(x=50, y=50)

fr_Gamma = tk.LabelFrame(window, relief=tk.RAISED, text="Run Gamma", width=200,
                         height=200)
fr_Gamma.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)
btn_mes_open = tk.Button(fr_Gamma, text="Run Gamma", command=gammacalc)
btn_mes_open.place(x=50, y=50)

window.mainloop()
