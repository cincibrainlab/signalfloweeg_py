import mne

def get_core_eeg_info( set_file_path ):
    """
    Extracts metadata from an EEG file.

    Args:
        set_file_path (str): The path to the EEG file.

    Returns:
        dict: A dictionary containing the metadata of the EEG file.
    """

    try:
        # Load the EEG data using MNE
        try:
            EEG = mne.io.read_raw_eeglab(set_file_path, preload=True)
            info = EEG.info
            eeg_core_info = {
                'mne_load_error': False,  # This key can be used to track the error in the database
                'mne_data_type': 'raw_eeglab',
                'n_channels': len(info['ch_names']),
                'sample_rate': info['sfreq'],
                'n_epochs': 1,
                'total_samples': len(EEG)
            }
        except Exception as e:
            EEG = mne.io.read_epochs_eeglab(set_file_path)
            info = EEG.info
            eeg_core_info = {
                'mne_load_error': False,  # This key can be used to track the error in the database
                'mne_data_type': 'epochs_eeglab',
                'n_channels': len(info['ch_names']),
                'sample_rate': info['sfreq'],
                'n_epochs': len(EEG) if hasattr(EEG, '__len__') else 1,
                'total_samples': (len(EEG) if hasattr(EEG, '__len__') else 1) * len(EEG.times)
            }
    except Exception as e:
        # Handle potential errors from the entire block
        eeg_core_info = {
            'mne_load_error': True,  # This key can be used to track the error in the database
            'mne_data_type': 'error',  # This key can be used to track the error in the database
            'n_channels': 0,
            'sample_rate': 0,
            'n_epochs': 0,
            'total_samples': 0
        }
        # Optionally log the error or handle it as needed

    return eeg_core_info


if __name__ == "__main__":

    file_path = "/Users/ernie/Documents/ExampleData/Chirp/D0320_chirp-ST_postcompMN_EEG_Constr_2018.set"
    get_core_eeg_info(file_path)
