import mne
import yaml
import os


import mne
import yaml
import os
import numpy as np


def load_eeg(file_path=None, recording_type=None):
    """
    Load EEG data from various formats based on the specified recording type.

    Parameters:
    -----------
    file_path : str, optional
        The path to the EEG data file or URL.
    recording_type : str, optional
        The type of recording, which determines the import function to use.
        If not provided, the user will be prompted to choose from a list of available recording types.

    Returns:
    --------
    raw : mne.io.Raw or mne.Epochs
        The loaded EEG data as an MNE Raw or Epochs object with the specified montage.
    """
    # Load the YAML file with import specifications
    import_specs_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "config", "recording_types.yaml"
    )
    with open(import_specs_path, "r") as f:
        import_specs = yaml.safe_load(f)

    # Display information on how to specify the recording type for the function with colors for better readability
    if file_path is None or recording_type is None:
        print(f"Check Recording Type ...")
        display_info(import_specs)
        return None

    # Find the appropriate import function based on the recording type
    if recording_type in import_specs:
        f"Valid specification found for recording type '{recording_type}'.",
    else:
        f"No import specification found for recording type '{recording_type}'.",
        display_info(import_specs)
        return None
    print(recording_type)
    
    # Add additional conditions for recording types here
    # Call the appropriate import function
    if recording_type == "EEGLAB_RAW_SET":
        EEG = import_eeglab(file_path, recording_type)
    elif recording_type == "EEGLAB_EPOCHS_SET":
        EEG = import_eeglab(file_path, recording_type)
    
    elif recording_type == "MNE_FIF":
        EEG = import_mne(file_path, recording_type)            
    
    elif recording_type == "EGI_128_RAW":
        EEG = import_egi(file_path, recording_type)
    elif recording_type == "EGI_128_MFF":
        EEG = import_egi(file_path, recording_type)
    
    elif recording_type == "NEURONEXUS_30_EDF":
        EEG = import_neuronexus(file_path, recording_type)
        
    # Add more import functions for other recording types
    else:
        print(f"No import function found for recording type '{recording_type}'.")
        display_info(import_specs)
        return None

    return EEG


def display_info(import_specs):
    print(
        "\033[1;34m\nTo use the load_eeg function, you must specify the recording type.\033[0m"
    )
    print(
        "\033[1;34mThe recording type determines which import function will be used to load the EEG data.\033[0m"
    )
    print(
        "\033[1;32mHere is a list of available recording types and their descriptions:\033[0m"
    )
    for idx, (rec_type, value) in enumerate(import_specs.items(), start=1):
        description = value["description"]
        print(f"\033[1;36m{idx}. {rec_type} - {description}\033[0m")
    print(
        "\033[1;35mPlease specify the recording type by passing it as the 'recording_type' argument.\n\033[0m"
    )

def import_eeglab(file_path, recording_type):
    """
    Import EEGLAB recording, apply montage, and perform epoching if necessary.
    """
    if recording_type == "EEGLAB_RAW_SET":
        print("Importing EEGLAB RAW SET data...")
        try:
            EEG = mne.io.read_raw_eeglab(file_path, preload=True)
        except TypeError:
            print("Error: The specified file contains epochs. Please use 'EEGLAB_EPOCHS_SET' as the recording type.")
            return None

    if recording_type == "EEGLAB_EPOCHS_SET":
        print("Importing EEGLAB EPOCHS SET data...")
        EEG = mne.io.read_epochs_eeglab(file_path)

    return EEG

def import_mne(file_path, recording_type):
    """
    Import MNE FIF recording, apply montage, and perform epoching if necessary.
    """
    if recording_type == "MNE_FIF":
        print("Importing MNE FIF data...")
        EEG = mne.io.read_raw_fif(file_path, preload=True)
        montage = mne.channels.make_standard_montage("GSN-HydroCel-129")
        EEG.set_montage(montage, match_case=False)

    return EEG

def import_egi(file_path, recording_type):
    """
    Import EGI128 recording, apply montage, and perform epoching if necessary.
    """

    if recording_type == "EGI_128_RAW":
        print("Importing EGI 128 Channel RAW data...")
        # Implement the specific steps for importing EGI128 data
        raw = mne.io.read_raw_egi(input_fname=file_path, preload=False)
        montage = mne.channels.make_standard_montage("GSN-HydroCel-129")
        montage.ch_names[128] = "E129"
        raw.set_montage(montage, match_case=False)

    if recording_type == "EGI_128_SET":
        print("Importing EGI 128 Channel EEGLAB SET data...")
        try:
            epochs = mne.io.read_epochs_eeglab(file_path)
        except Exception as e:
            print(f"Failed to read raw EEG data, will attempt import with Epochs: {e}")
            raw = mne.io.read_raw_eeglab(file_path, preload=True)

    # This code block is not used in the script. It shows how to load
    # continuous EEG data from a .set file with preload=True. Preloading
    # is useful for preprocessing that needs the full dataset before epoching.

    return raw


def import_neuronexus(file_path, recording_type):
    """
    Import neuronexus recording, apply montage, and perform epoching if necessary.
    """
    EEG = []
    if recording_type == "NEURONEXUS_30_EDF":
        # Add code to import the Neuronexus 30-channel Multielectrode Array
        # Return an MNE object with the correct channel montage and event markers
        EEG = mne.io.read_raw_edf(file_path, preload=True)

    elif recording_type == "NEURONEXUS_30_XDF":
        # Add code to import the Neuronexus 30-channel Multielectrode Array
        # Return an MNE object with the correct channel montage and event markers
        pass
   
    return EEG

def get_num_epochs(file_path, recording_type):
    EEG = load_eeg(file_path, recording_type)
    
    if EEG is not None:
        num_epochs = len(EEG)
        duration = EEG.times[-1] - EEG.times[0]
        
        result = {
            'file_path': file_path,
            'num_epochs': num_epochs,
            'duration': duration
        }
        return result
    else:
        return None

def get_amplitude_statistics(file_path, recording_type):
    EEG = load_eeg(file_path, recording_type)
    
    if EEG is not None:
        data = EEG.get_data()  # This will be a 3D array of shape (epochs, channels, time points)
        
        # Compute statistics across all epochs and channels
        mean_amplitude = np.mean(data)
        max_amplitude = np.max(data)
        min_amplitude = np.min(data)
        amplitude_range = max_amplitude - min_amplitude
    
        result = {
            'file_path': file_path,
            'mean_amplitude': [mean_amplitude],
            'max_amplitude': [max_amplitude],
            'min_amplitude': [min_amplitude],
            'amplitude_range': [amplitude_range]
        }
        return result
    else:
        return None


if __name__ == "__main__":

    from signalfloweeg.utils import load_catalog

    # Using utils.load_catalog() to load an example EEG file
    catalog = load_catalog(
        "https://raw.githubusercontent.com/cincibrainlab/signalfloweeg_py/master/userdata/cchmc_data.yaml"
    )
    from signalfloweeg.io import load_eeg

    # EEGLAB SET FILE (CONTINUOUS)
    eeglab_set = catalog["demo_infant_resting"]
    eeglab_mne = load_eeg(file_path=eeglab_set,  recording_type = "EEGLAB_RAW_SET")

    # EEGLAB SET FILE (EPOCHED)
    eeglab_set_epoched = catalog["demo_auditory_chirp"]
    eeglab_mne_epoched = load_eeg(eeglab_set_epoched, "EEGLAB_EPOCHS_SET")