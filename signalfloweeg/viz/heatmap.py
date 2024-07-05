import glob
import os
import mne
import matplotlib.pyplot as plt
import numpy as np
from fooof import FOOOF
from fooof.utils import trim_spectrum
from fooof.sim.gen import gen_aperiodic
from signalfloweeg.utils.area import riemanArea

SAVEDIR = "portal_files/plots"
plt.switch_backend('Agg')

def heatmap_power(epochs:mne.Epochs):
    """
    Plots a heatmap of the EEG data.

    Parameters:
    epochs (mne.Epochs): The epoch object containing the segmented data.
    """
    temp_var = epochs.compute_psd()
    FOOF_List = list()
    periodic_list = list()
    area_list = list()
    for i in range(0, temp_var.data.shape[0]):
        freqs = temp_var.freqs
        psds = temp_var._data[i]

        # average across channels of interest
        avgpow = np.mean(psds, axis=0)
            
            
            
        # select frequencies to fooof
        freqs_ext, pow_ext = trim_spectrum(freqs, avgpow, [0.5,50]) 
        # fooof fit
        fm = FOOOF(
            peak_width_limits = [2,5], 
            max_n_peaks = 5,
            #min_peak_height = fooof_min_peak_height
        )
        fm.fit(freqs_ext, pow_ext)
        FOOF_List.append(fm)

    epochs = len(FOOF_List)
    freqs = FOOF_List[0].freqs
    for k in range(0, len(FOOF_List)):
        fm = FOOF_List[k]
        periodic = fm.fooofed_spectrum_
        riemanAreaVals = riemanArea(fm)
        periodic_list.append(periodic)
        area_list.append(riemanAreaVals)


    periodic_array = np.array(periodic_list)
    periodic_array = periodic_array.T
    area_array = np.array(area_list)
    area_array = area_array.T

    #Plot settings for power heat map
    plt.figure(figsize=(7.5,5))
    plt.imshow(periodic_array, cmap='jet', origin='lower', extent=[0,5*epochs,freqs.min(),freqs.max()], aspect='auto')
    plt.colorbar(label="log(Power Spectral Density)")
    plt.title("Heat map of Power on Frequency vs Time - " + "psd")
    plt.xlabel("Time (s)")
    plt.ylabel("Frequency (Hz)")
    
    plt.savefig(os.path.join(SAVEDIR, "power.png"))

    plt.figure(figsize=(7.5,5))
    plt.imshow(area_array, cmap='jet', origin='lower', extent=[0,5*epochs,freqs.min(),freqs.max()], aspect='auto')
    plt.colorbar(label="Area between FOOOFed model and aperiodic fit")
    plt.title("Heat map of Area on Frequency vs Time - " + "Area")
    plt.xlabel("Time (s)")
    plt.ylabel("Frequency (Hz)")
    plt.savefig(os.path.join(SAVEDIR, "heatArea.png"))
    plt.close()
    pass

def headMapDirectory(filePath: str, epoch_length:float):
    os.chdir(filePath)

    # list of files 
    file_list = glob.glob('*.set')
    file_list.sort()
    print(file_list)


    # temp_var = epochs.compute_psd()
    FOOF_List = list()
    periodic_list = list()
    area_list = list()
    for file in file_list:
        EEG = mne.io.read_raw_eeglab(file)
        EEG = EEG.load_data()
        epochs = mne.make_fixed_length_epochs(EEG, duration=epoch_length, preload=False)
        temp_var = epochs.compute_psd()
        for i in range(0, temp_var.data.shape[0]):
            freqs = temp_var.freqs
            psds = temp_var._data[i]

            # average across channels of interest
            avgpow = np.mean(psds, axis=0)
                
                
                
            # select frequencies to fooof
            freqs_ext, pow_ext = trim_spectrum(freqs, avgpow, [8,13]) 
            # fooof fit
            fm = FOOOF(
                peak_width_limits = [2,5], 
                max_n_peaks = 5,
                #min_peak_height = fooof_min_peak_height
            )
            fm.fit(freqs_ext, pow_ext)
            FOOF_List.append(fm)

    epochs = len(FOOF_List)
    freqs = FOOF_List[0].freqs
    for k in range(0, len(FOOF_List)):
        fm = FOOF_List[k]
        periodic = fm.fooofed_spectrum_
        riemanAreaVals = riemanArea(fm)
        periodic_list.append(periodic)
        area_list.append(riemanAreaVals)


    periodic_array = np.array(periodic_list)
    periodic_array = periodic_array.T
    area_array = np.array(area_list)
    area_array = area_array.T

    #Plot settings for power heat map
    plt.figure(figsize=(7.5,5))
    plt.imshow(periodic_array, cmap='jet', origin='lower', extent=[0,5*epochs,freqs.min(),freqs.max()], aspect='auto')
    plt.colorbar(label="log(Power Spectral Density)")
    plt.title("Heat map of Power on Frequency vs Time - " + "psd")
    plt.xlabel("Time (s)")
    plt.ylabel("Frequency (Hz)")

    plt.figure(figsize=(7.5,5))
    plt.imshow(area_array, cmap='jet', origin='lower', extent=[0,5*epochs,freqs.min(),freqs.max()], aspect='auto')
    plt.colorbar(label="Area between FOOOFed model and aperiodic fit")
    plt.title("Heat map of Area on Frequency vs Time - " + "Area")
    plt.xlabel("Time (s)")
    plt.ylabel("Frequency (Hz)")
    plt.show()
    pass