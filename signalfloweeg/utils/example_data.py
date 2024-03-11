import yaml


def load_example_data_paths(file_path):
    """
    Retrieve the paths of example datasets.

    Args:
        file_path (str): The path to the YAML file containing the dataset paths.

    Returns:
        dict: A dictionary containing dataset names as keys and their corresponding paths as values.
    """
    print("Loading example dataset paths...")
    # Load the dataset paths from the specified YAML file
    with open(file_path, "r") as file:
        example_datasets = yaml.safe_load(file)

    # Define color constants
    GREEN = "\033[92m"
    RED = "\033[91m"
    RESET = "\033[0m"

    for dataset, path in example_datasets.items():
        color = GREEN if path else RED
        print(f"{color}{dataset}: {path or 'Dataset not available'}{RESET}")

    return example_datasets
