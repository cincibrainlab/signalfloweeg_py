import signalfloweeg 
import mne 

filepath = "/home/cbl/Desktop/Test_Data/0012_rest.set"
EEG = mne.io.read_raw_eeglab(filepath)
fig = EEG.compute_psd().plot
# filtered_eeg = signalfloweeg.preprocessing.filtering.bandpass_filter(EEG, 2, 50)
resampled_eeg = signalfloweeg.preprocessing.resampling.resample(EEG)
fig = EEG.compute_psd().plot
# segment_EEG = signalfloweeg.preprocessing.segment_rejection.manual_segment_rejection(filtered_eeg)
end = input("Press enter to continue\n")
