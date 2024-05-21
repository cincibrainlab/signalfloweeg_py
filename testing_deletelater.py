import signalfloweeg 
import mne 

filepath = "/home/cbl/Desktop/Test_Data/0012_rest.set"
EEG = mne.io.read_raw_eeglab(filepath)
filtered_eeg = signalfloweeg.preprocessing.filtering.bandpass_filter(EEG, 2, 50)
filtered_eeg = signalfloweeg.preprocessing.filtering.notch_filter(filtered_eeg, 60)
filtered_eeg = signalfloweeg.preprocessing.resampling.resample(filtered_eeg, 500)
epochs = signalfloweeg.preprocessing.epoching.epoch_time(filtered_eeg, 1)

signalfloweeg.viz.heatmap.heatmap_power(epochs)



# # filtered_eeg = signalfloweeg.preprocessing.filtering.bandpass_filter(EEG, 2, 50)

# from mne.preprocessing import ICA

# # Load your data
# raw = EEG
# raw.load_data()

# # High-pass filter the data before running ICA
# raw.filter(l_freq=1., h_freq=None)

# # Define the ICA object
# ica = ICA(n_components=20, random_state=97)

# # Fit the ICA model to the raw data
# ica.fit(raw)

# # Visualize the components. You'll have to decide which ones are artifactual based on their time courses and topographies
# ica.plot_components()

# # Identify artifact components (e.g., components 0, 1 and 3)
# artifact_components = [0, 1, 3]

# # Create an annotation for each artifact component
# for component in artifact_components:
#     # Find the times when the component's absolute value is above a threshold
#     component_data = ica.get_sources(raw).get_data()[component]
#     artifact_times, artifact_values = mne.preprocessing.peak_finder(component_data, thresh=0.5)
    
#     # Create an annotation for each artifact time
#     annotations = mne.Annotations(artifact_times / raw.info['sfreq'],
#                                   0.1,  # Duration of each annotation
#                                   'artifact',
#                                   orig_time=raw.info['meas_date'])
    
#     # Add the annotations to the raw data
#     raw.set_annotations(annotations)

# # Now, when you plot the raw data, the artifacts will be annotated
# raw.plot(block = True)



