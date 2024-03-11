# ==============================================================================
# Demonstration of Using the New MNE Browser Based on PyQtGraph
# ==============================================================================
# This section of the code demonstrates the use of the new MNE browser for plotting 2D data.
# The new backend, based on pyqtgraph and Qt's Graphics View Framework, offers an alternative
# for visualizing EEG data interactively. This development was initiated during the Google Summer
# of Code 2021.
#
# To utilize this new browser, ensure that you have the latest version of MNE and the mne-qt-browser
# package installed. You can install or update these packages using pip:
# pip install -U mne mne-qt-browser

import mne
import matplotlib

# Specify the path to the resting state EEG data file
# Parameters:
#   eeg_file: String indicating the full path to the EEG data file in EEGLAB .set format.
eeg_file = '/Users/ernie/Documents/ExampleDataHbcd/sub-PIARK0005_ses-V03_task-VEP_acq-eeg_eeg.set'

# The following code block demonstrates how to load
# continuous EEG data from a .set file with the preload option set to True. Preloading
# the data is advantageous for preprocessing steps that require access to the entire dataset prior to epoching.
try:
    raw = mne.io.read_raw_eeglab(eeg_file, preload=True)
except Exception as e:
    print(f"Failed to read raw EEG data: {e}")

# For updated installation: pip install -U mne-qt-browser
# More information available at: https://github.com/mne-tools/mne-qt-browser
matplotlib.use('Qt5Agg')  # Switching backend to Qt5 for compatibility
raw.plot(block=True)
