import os
import sys
import numpy as np
import mne
from numba import jit

# Add the path to the SpectralEvents package to the system path
sys.path.append('/Users/ernie/Documents/GitHub/SpectralEvents')
import spectralevents as se

# Define the number of channels and points per trial
no_of_channels = 68
points_per_trial = 1626
no_of_trials = 80

def get_set_files_list(path):
    """
    Get a list of all .set files in the specified directory.

    Parameters
    ----------
    path : str
        The path to the directory containing .set files.

    Returns
    -------
    list
        A list of paths to .set files found in the specified directory.
    """
    set_files = [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.set')]
    return set_files
def read_eeglab(file_path):
    raw = mne.io.read_raw_eeglab(file_path, preload=True)
    return raw
def reshape_eeg_data(raw, points_per_trial, no_of_channels):
    """
    Reshape the EEG data array to the form (n_channels, n_times, n_trials).

    Parameters
    ----------
    arr : ndarray
        The EEG data array to be reshaped.
    points_per_trial : int, optional
        The number of time points per trial. Default is 1626.
    no_of_channels : int, optional
        The number of channels in the EEG data. Default is 68.

    Returns
    -------
    reshaped_arr : ndarray
        The reshaped EEG data array.

    Raises
    ------
    AssertionError
        If the reshaped array dimensions do not match the expected values.
    """
    arr = raw.get_data()
    reshaped_arr = np.reshape(arr, (no_of_channels, points_per_trial, -1))
    #assert reshaped_arr.shape[0] == no_of_channels, "Number of channels does not match expected value."
    #assert reshaped_arr.shape[1] == points_per_trial, "Points per trial do not match expected value."
    return reshaped_arr
def get_single_channel_data(reshaped_arr, channel=1, no_of_trials=80):
    """
    Extract a single channel of EEG data from a 3D array and convert it to a 2D trial time series.

    Parameters
    ----------
    reshaped_arr : ndarray
        The reshaped EEG data array.
    channel : int, optional
        The channel to extract. Default is 1.

    Returns
    -------
    transposed_data : ndarray
        The 2D trial time series of the specified channel.

    Raises
    ------
    AssertionError
        If the reshaped array dimensions do not match the expected values.
    """

    single_channel_data = np.squeeze(reshaped_arr[channel, :, :])
    transposed_data = np.transpose(single_channel_data)
    transposed_data = transposed_data[:no_of_trials, : ]
    return transposed_data

set_files = get_set_files_list('/Users/ernie/Documents/ExampleData/Chirp')

# Read the EEG data
raw = read_eeglab(set_files[1])
samp_freq = raw.info['sfreq']  # Get the sampling rate from the raw object

# Reshape the EEG data
reshaped_arr = reshape_eeg_data(raw, points_per_trial, no_of_channels)

for i in range(no_of_channels-1):
    single_channel_data = get_single_channel_data(reshaped_arr, i)
    print(single_channel_data.shape)

# Spectral Events Parameters
freqs = np.arange(1, 60+1, 1)  # Hz
times = np.arange(points_per_trial) / samp_freq  # seconds
event_band = [7.5, 12.5]  # beta band (Hz)
thresh_FOM = 4.0  # factor-of-the-median threshold

# calculate TFR
tfrs = se.tfr(single_channel_data, freqs, samp_freq)

fig = se.plot_avg_spectrogram(tfr=tfrs, times=times, freqs=freqs,
                              event_band=event_band)

# find spectral events!!
spec_events = se.find_events(tfr=tfrs, times=times, freqs=freqs,
                             event_band=event_band, threshold_FOM=thresh_FOM)
epoch = int(1)
chan_no = int(1)
spec_events = []
updated_spec_events = []  # Initialize an empty list to hold updated spectral events for all channels
for channel_data in range(3): #range(no_of_channels):
    # Assuming spec_events is a list of lists for each channel
    print(channel_data)
    single_channel_data = get_single_channel_data(reshaped_arr, channel_data )
    
    # calculate TFR
    tfrs = se.tfr(single_channel_data, freqs, samp_freq)

    # find spectral events!!
    spec_events = se.find_events(tfr=tfrs, times=times, freqs=freqs,
                                event_band=event_band, threshold_FOM=thresh_FOM)

    #channel_spec_events = spec_events[channel_data] if len(spec_events) > channel_data else []
    epoch_spec_events = []
    for epoch in range(0, no_of_trials):
        for event in spec_events[epoch]:
            if isinstance(event, dict):  # Ensure event is a dictionary before modifying
                modified_event = event.copy()  # Make a copy to avoid modifying the original list
                modified_event['Epoch'] = epoch+1
                modified_event['Filename'] = "test_filename.set"
                modified_event['Channel'] = channel_data
                epoch_spec_events.append(modified_event)
                epoch += 1  # Increment epoch for each event
            else:
                raise TypeError(f"Expected event to be a dictionary, got {type(event)}")
            updated_spec_events.append(epoch_spec_events)  # Append the modified events for the current channel to the list

    spec_events = updated_spec_events  # Update the spec_events list with modified events for all channels

# Assuming spec_events is already populated with the spectral event data
# Define the file path where the JSON file will be saved
# Specify the file path to save the JSON data
json_file_path = '/Users/ernie/Documents/ExampleData/Chirp/spec_events.json'

# Use the json module to write the spec_events list to a file in JSON format, handling numpy int64 serialization issue
with open(json_file_path, 'w') as outfile:
    json.dump(spec_events, outfile, indent=4, default=lambda o: int(o) if isinstance(o, np.integer) else o)
print(f"Spectral events data has been written to {json_file_path}")



import json
import numpy as np
# Define the custom serializer function
def make_custom_serializer(filename, channel, epoch):
    def custom_serializer(obj):
        if isinstance(obj, np.ndarray):
            return {"filename": filename, "channel": channel, "epoch": epoch, "data": obj.tolist()}
        elif isinstance(obj, dict):
            return obj
        # Handle additional data types for serialization
        elif isinstance(obj, (int, float, str, bool, np.integer, np.floating)):
            return obj.item() if isinstance(obj, (np.integer, np.floating)) else obj
        elif isinstance(obj, list):
            return [custom_serializer(item) for item in obj]
        else:
            raise TypeError(f"Unsupported data type {type(obj)} for serialization")
    return custom_serializer
# Prepare additional inputs for the custom serializer
filename = "example_filename.set"
channel = 1
epoch = 0  # Initialize epoch number

# Assuming spec_events is defined somewhere in your code
# Create a custom_serializer function configured with the filename, channel, and epoch
configured_serializer = make_custom_serializer(filename, channel, epoch)

# Convert spectral events to JSON format using the configured custom serializer
spec_events_json = json.dumps(spec_events, indent=4, default=configured_serializer)

# Specify the file path to save the JSON data
json_file_path = '/Users/ernie/Documents/ExampleData/Chirp/spec_events.json'

# Write the JSON data to a file
with open(json_file_path, 'w') as json_file:
    json_file.write(spec_events_json)

print(f"Spectral events exported to JSON format at {json_file_path}")
