import signalfloweeg 
import mne 

filepath = "/home/cbl/Desktop/Test_Data/0012_rest.set"
EEG = mne.io.read_raw_eeglab(filepath)
EEG.plot()
filtered_eeg = signalfloweeg.preprocessing.filtering.bandpass_filter(EEG, 2, 50)

segment_EEG = signalfloweeg.preprocessing.segment_rejection.manual_segment_rejection(filtered_eeg)
# ica_EEG = signalfloweeg.preprocessing.ica.run_ICA(filtered_eeg)
