import yaml
import requests


def load_catalog(file_path_or_url):
    """
    Retrieve the paths of example datasets from a local file or a GitHub URL.

    Args:
        file_path_or_url (str): The path to the local YAML file or the URL of the raw GitHub file
                                containing the dataset paths.

    Returns:
        dict: A dictionary containing dataset names as keys and their corresponding paths as values.
    """
    print("Loading example dataset paths...")

    # Determine if the input is a URL or a local file path
    if file_path_or_url.startswith(("http://", "https://")):
        # Fetch the YAML file from the GitHub URL
        response = requests.get(file_path_or_url)
        example_datasets = yaml.safe_load(response.text)
    else:
        # Load the dataset paths from the specified local YAML file
        with open(file_path_or_url, "r") as file:
            example_datasets = yaml.safe_load(file)

    # Define color constants
    GREEN = "\033[92m"
    RED = "\033[91m"
    RESET = "\033[0m"

    for dataset, path in example_datasets.items():
        color = GREEN if path else RED
        print(f"{color}{dataset}: {path or 'Dataset not available'}{RESET}")

    return example_datasets
