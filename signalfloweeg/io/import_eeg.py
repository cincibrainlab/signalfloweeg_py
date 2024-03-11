import mne
import yaml
import os


import mne
import yaml
import os


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
    # Call the appropriate import function
    if recording_type == "EGI_128_RAW":
        EEG = import_egi(file_path, recording_type)
    elif recording_type == "import_mea30":
        EEG = import_mea30(file_path)
    # Add more import functions for other recording types
    else:
        print(f"No import function found for recording type '{recording_type}'.")
        display_info(import_specs)
        return None

    return EEG


# ... (import_egi128, import_mea30, and other import functions remain the same)


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


def import_egi(file_path, recording_type):
    """
    Import EGI128 recording, apply montage, and perform epoching if necessary.
    """

    if recording_type == "EGI_128_RAW":
        print("EGI_128_RAW")
        # Implement the specific steps for importing EGI128 data
        raw = mne.io.read_raw_egi(file_path, preload=True)
        montage = mne.channels.make_standard_montage("GSN-HydroCel-128")
        raw.set_montage(montage)

    # Perform any additional preprocessing or epoching steps
    return raw


def import_mea30(file_path):
    """
    Import MEA30 recording, apply montage, and perform epoching if necessary.
    """
    # Implement the specific steps for importing MEA30 data
    raw = mne.io.read_raw_edf(file_path, preload=True)
    montage = mne.channels.make_standard_montage("standard_1020")
    raw.set_montage(montage)
    # Perform any additional preprocessing or epoching steps
    return raw


## Add more import functions for other recording types
# load_eeg(continuous_eeg_file, "EGI128A")


from signalfloweeg.utils import load_catalog

# Using utils.load_catalog() to load an example EEG file
catalog = load_catalog(
    "https://raw.githubusercontent.com/cincibrainlab/signalfloweeg_py/master/userdata/cchmc_data.yaml"
)

# EGI/MAGSTIM 128 Resting State Data
resting_raw = catalog["demo_rest_raw"]

# EGI/MAGSTIM 128 Auditory Evoked Potentials
erp_raw = catalog["demo_auditory_chirp"]

# No arguments to show recording types
load_eeg(resting_raw, "EGI_128_RAW")
