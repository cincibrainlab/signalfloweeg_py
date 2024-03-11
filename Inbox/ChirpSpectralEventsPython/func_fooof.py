import os
import mne
from neurodsp.spectral import compute_spectrum
from specparam import SpectralGroupModel
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sns.set(style='white', font_scale=1.2)

def load_and_process_eeg(file_path):
    """
    Load EEG data and preprocess it into epochs and evoked data.
    """
    print(f"Processing file: {os.path.basename(file_path)}")
    raw = mne.io.read_raw_eeglab(file_path, preload=True)
    epochs = mne.make_fixed_length_epochs(raw, duration=1626/raw.info['sfreq'], preload=True)[:80]
    evoked = epochs.average()
    return raw, epochs, evoked

def compute_psd_welch(raw):
    """
    Computes PSD using Welch method.
    """
    data = raw.get_data(units="uV")
    sf = raw.info['sfreq']
    freqs, psd_chans = compute_spectrum(data, sf, method='welch', avg_type='mean', nperseg=sf*2)
    chan_names = raw.info['ch_names']
    return freqs, psd_chans, chan_names

def spectral_parameterization(freqs, psd_chans, file_basename, chans):
    """
    Perform spectral parameterization using FOOOF.
    """
    freq_range = [3, 40]
    fg = SpectralGroupModel(peak_width_limits=[1.0, 8.0], aperiodic_mode='knee', max_n_peaks=5)
    fg.report(freqs, psd_chans, freq_range)
    fg.save_report(file_name='group_results')
    fg.save(file_name='group_results_export', save_results=True)
    group_results = fg.get_results()

    # Aperiodic parameters
    aperiodic_data = [
        {
            'filename': file_basename,
            'channel': idx + 1,
            'label': chan,
            'freq_range': f"{freq_range[0]}-{freq_range[1]} Hz",
            'freq_res': fg.freq_res,
            'max_peaks': fg.max_n_peaks,
            'aperiodic_mode': fg.aperiodic_mode,
            'peak_width_limits': f"{fg.peak_width_limits[0]}-{fg.peak_width_limits[1]}",
            'min_peak_height': fg.min_peak_height,
            'peak_threshold': fg.peak_threshold,
            'measure': 'aperiodic',
            'offset': result.aperiodic_params[0],
            'knee': result.aperiodic_params[1] if len(result.aperiodic_params) == 3 else 0,
            'exponent': result.aperiodic_params[-1],
            'error': result.error,
            'r_squared': result.r_squared
        }
        for idx, (result, chan) in enumerate(zip(group_results, chans))
    ]
    aperiodic_df = pd.DataFrame(aperiodic_data)
    aperiodic_df.to_csv('aperiodic.csv')

    # Periodic parameters
    periodic_data = []
    for idx, result in enumerate(group_results):
        for peak_no, (peak, gauss) in enumerate(zip(result.peak_params, result.gaussian_params), start=1):
            periodic_data.append({
                'filename': file_basename,
                'channel': idx + 1,
                'label': chans[idx],
                'measure': 'periodic',
                'peak_no': peak_no,
                'peak_center': peak[0],
                'peak_power': peak[1],
                'peak_width': peak[2],
                'fit_mean': gauss[0],
                'fit_height': gauss[1],
                'fit_sd': gauss[2]
            })
    periodic_df = pd.DataFrame(periodic_data)
    periodic_df.to_csv('periodic.csv')

    return aperiodic_df, periodic_df

def main(file_path):
    """
    Main function to process EEG data, compute PSD, and perform spectral parameterization.
    """
    raw, epochs, evoked = load_and_process_eeg(file_path)
    freqs, psd_chans, chan_names = compute_psd_welch(raw)
    aperiodic_df, periodic_df = spectral_parameterization(freqs, psd_chans, os.path.basename(file_path), chan_names)
    return aperiodic_df, periodic_df

file_path = '/Users/ernie/Documents/ExampleData/Chirp/D0179_chirp-ST_postcomp_MN_EEG_Constr_2018.set'
aperiodic_df, periodic_df = main(file_path)

