import hashlib
import yaml
import os

# Define the default configuration file name
YAML_CONFIG = "portal_config.yaml"

def load_config(file_path=YAML_CONFIG):
    """
    Loads the YAML configuration file.

    Args:
        file_path (str): The path to the YAML configuration file. Defaults to YAML_CONFIG.

    Returns:
        dict: The loaded YAML configuration as a dictionary, or None if an error occurs.
    """
    if os.path.isfile(file_path):
        config_file_path = file_path
    else:
        config_file_path = os.path.join(os.path.dirname(__file__), file_path)
    from rich.console import Console
    console = Console()
    console.print(f"Active portal_config located at: [bold]{config_file_path}[/bold]")
    try:
        with open(file_path, 'r') as stream:
            return yaml.safe_load(stream)
    except FileNotFoundError:
        print(f"File {file_path} not found.")
    except yaml.YAMLError as exc:
        print(exc)

def create_file_hash(file_path):
    """
    Creates a BLAKE2 hash for a given file.

    Args:
        file_path (str): The path to the file to hash.

    Returns:
        str: The hexadecimal representation of the hash.
    """
    hash_blake2 = hashlib.blake2b()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_blake2.update(chunk)
    return hash_blake2.hexdigest()

def add_status_code(code):
    """
    Maps a status code to a status string.

    Args:
        code (int): The status code to map.

    Returns:
        str: The corresponding status string.
    """
    if code == 200:
        return 'NEW'
    elif code == 201:
        return 'IMPORTED'
    elif code == 204:
        return 'DELETED'
    elif code == 500:
        return 'LOAD_ERROR'
    else:
        return 'UNHANDLED'