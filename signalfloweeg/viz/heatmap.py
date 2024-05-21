import mne
import matplotlib.pyplot as plt
import numpy as np
from fooof import FOOOF
from fooof.utils import trim_spectrum
from fooof.sim.gen import gen_aperiodic
from signalfloweeg.utils.area import riemanArea
#TODO
def heatmap_power(epochs:mne.Epochs):
    """
    Plots a heatmap of the EEG data.

    Parameters:
    epochs (mne.Epochs): The epoch object containing the segmented data.
    """
    temp = epochs.compute_psd()
    FOOF_List = list()
    periodic_list = list()
    area_list = list()
    for i in range(0, temp.data.shape[0]):
        freqs = temp.freqs
        psd = temp.data[i]
        avgpow = np.mean(psd, axis=0)
        freqs_ext, pow_ext = trim_spectrum(freqs, avgpow, [0.5,50])
        fm = FOOOF(
                    peak_width_limits = [2,5], 
                    max_n_peaks = 5,
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
    plt.figure(figsize=(7.5,7.5))
    plt.imshow(periodic_array, cmap='jet', origin='lower', extent=[0,1*epochs,freqs.min(),freqs.max()], aspect='auto')
    plt.colorbar(label="log(Power Spectral Density)", location='bottom', orientation='horizontal')
    plt.title("Heat map of Power on Frequency vs Time - " + "psd")
    plt.xlabel("Time (s)")
    plt.ylabel("Frequency (Hz)")
    plt.show()

    plt.figure(figsize=(7.5,7.5))
    plt.imshow(area_array, cmap='jet', origin='lower', extent=[0,1*epochs,freqs.min(),freqs.max()], aspect='auto')
    plt.colorbar(label="Area between FOOOFed model and aperiodic fit", location='bottom', orientation='horizontal')
    plt.title("Heat map of Area on Frequency vs Time - " + "area")
    plt.xlabel("Time (s)")
    plt.ylabel("Frequency (Hz)")
    plt.show()
    pass