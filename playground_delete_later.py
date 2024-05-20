import signalfloweeg 
import mne 

filepath = "C:\\Users\\sueo8x\\Documents\\raw_files_ForNate_3.10.2022\\128_EGI_SET\\0012_rest.set"
EEG = mne.io.read_raw_eeglab(filepath, preload=True)
filtered_eeg = signalfloweeg.preprocessing.filtering.bandpass_filter(EEG, 2, 50)

# segment_EEG = signalfloweeg.preprocessing.segment_rejection.manual_segment_rejection(filtered_eeg)
ica_EEG = signalfloweeg.preprocessing.ica.run_ICA(filtered_eeg)
print(filtered_eeg)
