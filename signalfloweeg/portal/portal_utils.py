import hashlib
import yaml
import os
from rich.console import Console


# Define the default configuration file name
YAML_CONFIG = os.path.join(os.path.dirname(__file__), "portal_config.yaml")

def check_database_and_tables():
    """
    Checks if the database and required tables are present and correctly structured.
    Returns True if all required tables and their structures are correct, otherwise False.
    """
    from sqlalchemy import inspect
    from signalfloweeg.portal.db_connection import get_engine
    from rich.console import Console

    console = Console()
    engine = get_engine()
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    required_tables = {
        'startup_table': ['id', 'sf_config_path'],
        'config': ['id', 'database', 'frontend', 'api', 'folder_paths', 'eeg_formats', 'eeg_paradigms', 'eeg_analyses'],
        'upload_catalog': ['status', 'date_added', 'original_name', 'dataset_name', 'dataset_id', 'eeg_format', 'eeg_paradigm', 'is_set_file', 'has_fdt_file', 'fdt_filename', 'fdt_upload_id', 'hash', 'upload_id', 'size', 'remove_upload'],
        'dataset_catalog': ['dataset_name', 'dataset_id', 'description'],
        'import_catalog': ['status', 'date_added', 'original_name', 'dataset_name', 'dataset_id', 'eeg_format', 'eeg_paradigm', 'is_set_file', 'has_fdt_file', 'fdt_filename', 'fdt_upload_id', 'hash', 'upload_id', 'remove', 'sample_rate', 'n_channels', 'n_epochs', 'total_samples', 'mne_load_error'],
        'analysis_joblist': ['id', 'job_id', 'upload_id', 'eeg_format_name', 'eeg_paradigm_name', 'eeg_analysis_name', 'status', 'created_at', 'parameters', 'result'],
        'eeg_paradigm': ['id', 'name', 'description'],
        'eeg_analyses': ['id', 'name', 'description', 'category', 'valid_formats', 'valid_paradigms', 'parameters'],
        'eeg_format': ['id', 'name', 'description']
    }

    missing_tables = []
    incorrect_structure = []

    for table, fields in required_tables.items():
        if table not in tables:
            missing_tables.append(table)
        else:
            columns = [column['name'] for column in inspector.get_columns(table)]
            if not all(field in columns for field in fields):
                incorrect_structure.append(table)

    if missing_tables:
        console.print(f"[red]Missing tables:[/red] {missing_tables}")
    if incorrect_structure:
        console.print(f"[red]Tables with incorrect structure:[/red] {incorrect_structure}")

    if not missing_tables and not incorrect_structure:
        console.print("[green]Database and all required tables are verified and correctly structured.[/green]")
        return True
    else:
        return False


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

    console = Console()
    console.print(f"Using: [bold]{config_file_path}[/bold]")

    try:
        with open(file_path, "r") as stream:
            config = yaml.safe_load(stream)
            return config
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
    with open(file_path, "rb") as f:
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
        return "NEW"
    elif code == 201:
        return "IMPORTED"
    elif code == 204:
        return "DELETED"
    elif code == 500:
        return "LOAD_ERROR"
    else:
        return "UNHANDLED"

if __name__ == "__main__":
    check_database_and_tables()