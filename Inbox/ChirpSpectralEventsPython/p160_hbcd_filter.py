# ==============================================================================
# Loading Resting State EEG Data
# ==============================================================================
# This script section is dedicated to loading resting state EEG data for further analysis.
# The data is expected to be in the EEGLAB .set format, which is a common format for EEG data storage.
# The MNE-Python library is utilized here to read the epochs directly from the .set file.

import mne

# Path to the resting state EEG data file
# Arguments:
#   resting_file: A string representing the full path to the EEG data file in EEGLAB .set format.
resting_file = '/Users/ernie/Documents/ExampleDataHbcd/sub-PIARK0005_ses-V03_task-VEP_acq-eeg_eeg.set'

# This code block is not used in the script. It shows how to load
# continuous EEG data from a .set file with preload=True. Preloading
# is useful for preprocessing that needs the full dataset before epoching.
try:
    raw = mne.io.read_raw_eeglab(resting_file, preload=True)
except Exception as e:
    print(f"Failed to read raw EEG data: {e}")

import matplotlib
matplotlib.use('Qt5Agg')  # Change backend to Qt5
raw.plot()

raw.resample(250, npad="auto")    # set sampling frequency to 256 points per second

raw.filter(1, 30, fir_design='firwin', picks=['eeg'])  # band-pass filter from 1 to 30 frequency over just
                                                       # EEG channel and not EEG channel

raw.set_eeg_reference('average', projection=True).apply_proj()  # re-referencing with the virtual average reference
ica = mne.preprocessing.ICA(n_components=50, random_state=97, method='fastica')
ica.fit(raw)     
ica.plot_components()  # Plot all decomposed components

from autoreject import AutoReject
ar = AutoReject()
epochs_clean = ar.fit_transform(epochs)  

                                                                # Ocular artifacts (EOG)
eog_evoked = mne.preprocessing.create_eog_epochs(raw).average()   # Conveniently generate epochs around EOG artifact events
eog_evoked.apply_baseline(baseline=(None, -0.2))
eog_evoked.plot_joint()

#picks = mne.pick_types(raw.info, meg='mag', exclude=[])
#data, times = raw[picks[:10], start:stop]

#import matplotlib.pyplot as plt
#import chart_studio.plotly as py
#data, times = raw[:, :]
#plt.plot(times, data.T)
#plt.xlabel('time (s)')
#plt.ylabel('MEG data (T)')

#update = dict(layout=dict(showlegend=True), data##=[dict(name=raw.info['ch_names'][p]) for p in picks[:10]])
#py.iplot_mpl(plt.gcf())

