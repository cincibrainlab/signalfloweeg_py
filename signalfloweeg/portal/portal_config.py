import json
import yaml
import os
from rich.console import Console
from signalfloweeg.portal.db_connection import get_database

console = Console()
console.print("[bold]Module portal_config is currently running...[/bold]")

async def get_portal_config_path():
    db = await get_database()
    startup_record = await db.startup.find_one({"_id": 1})
    if startup_record:
        return startup_record.get('sf_config_path')
    else:
        return None

async def is_config_table_present():
    """
    Check if the configuration collection exists in the database.

    Returns:
        bool: True if the configuration collection exists, False otherwise.
    """
    try:
        db = await get_database()
        collections = await db.list_collection_names()
        return 'config' in collections
    except Exception as e:
        console.print(f"Error checking for config collection: {e}")
        return False

async def check_database_and_tables():
    """
    Verify the presence of required collections in the database.

    Returns:
        bool: True if all required collections are present, otherwise False.
    """
    db = await get_database()
    existing_collections = await db.list_collection_names()

    required_collections = [
        "startup", "config", "upload_catalog", "dataset_catalog", "import_catalog",
        "analysis_joblist", "eeg_paradigms", "eeg_analyses", "eeg_formats", "users"
    ]

    for collection in required_collections:
        if collection not in existing_collections:
            await db.create_collection(collection)
            console.print(f"[yellow]Created missing collection: {collection}[/yellow]")
        else:
            console.print(f"[green]Collection {collection} already exists[/green]")

    return True

async def load_config():
    """
    Load the YAML configuration file.

    Returns:
        dict: The loaded YAML configuration as a dictionary, or None if an error occurs.
    """
    file_path = await get_portal_config_path()

    if not os.path.isfile(file_path):
        file_path = os.path.join(os.path.dirname(__file__), file_path)

    try:
        with open(file_path, "r") as stream:
            return yaml.safe_load(stream)
    except FileNotFoundError:
        console.print(f"File {file_path} not found.")
    except yaml.YAMLError as exc:
        console.print(exc)

async def load_config_from_yaml():
    """
    Load configuration from YAML and update the database accordingly.
    Returns:
        bool: True if successful, False otherwise.
    """
    data = await load_config()
    if data is None:
        return False

    db = await get_database()
    config_collection = db.config

    # Update or insert each section of the configuration
    for section, content in data.items():
        if isinstance(content, list):
            # Handle array content (like users, eeg_formats, etc.)
            section_collection = db[section]
            # Clear existing documents in the collection
            await section_collection.delete_many({})
            # Insert new documents
            if content:
                await section_collection.insert_many(content)
        else:
            # Handle non-array content
            await config_collection.update_one(
                {"_id": section},
                {"$set": content},
                upsert=True
            )

    console.print("[green]Configuration loaded and updated in the database.[/green]")
    return True

async def add_eeg_analysis_to_db():
    """
    Add EEG analysis configurations to the database.
    """
    db = await get_database()
    eeg_analyses_collection = db.eeg_analyses

    eeg_analyses = [
        {
            "name": "Power Spectrum",
            "description": "Compute the power spectral density using Welch's method.",
            "category": "Spectral",
            "valid_formats": ["EDF", "BDF", "SET"],
            "valid_paradigms": ["Resting State", "Task-based"],
            "parameters": {
                "fmin": {"type": "float", "default": 0.0, "description": "Minimum frequency of interest"},
                "fmax": {"type": "float", "default": 50.0, "description": "Maximum frequency of interest"},
                "tmin": {"type": "float", "default": None, "description": "Start time to use"},
                "tmax": {"type": "float", "default": None, "description": "End time to use"},
            },
        },
        # Add more EEG analyses configurations here
    ]

    try:
        for analysis in eeg_analyses:
            await eeg_analyses_collection.update_one(
                {"name": analysis["name"]},
                {"$set": analysis},
                upsert=True
            )
        console.print("[green]EEG analyses configurations added to the database.[/green]")
    except Exception as e:
        console.print(f"[red]Error adding EEG analyses configurations: {e}[/red]")

async def add_eeg_formats_to_db():
    """
    Add EEG format configurations to the database.
    """
    db = await get_database()
    eeg_format_collection = db.eeg_format

    eeg_formats = [
        {"name": "EDF", "description": "European Data Format"},
        {"name": "BDF", "description": "BioSemi Data Format"},
        {"name": "SET", "description": "EEGLAB SET format"},
        # Add more EEG format configurations here
    ]

    try:
        for format in eeg_formats:
            await eeg_format_collection.update_one(
                {"name": format["name"]},
                {"$set": format},
                upsert=True
            )
        console.print("[green]EEG format configurations added to the database.[/green]")
    except Exception as e:
        console.print(f"[red]Error adding EEG format configurations: {e}[/red]")

async def add_eeg_paradigms_to_db():
    """
    Add EEG paradigm configurations to the database.
    """
    db = await get_database()
    eeg_paradigm_collection = db.eeg_paradigm

    eeg_paradigms = [
        {"name": "Resting State", "description": "EEG recorded during rest"},
        {"name": "Task-based", "description": "EEG recorded during a specific task"},
        # Add more EEG paradigm configurations here
    ]

    try:
        for paradigm in eeg_paradigms:
            await eeg_paradigm_collection.update_one(
                {"name": paradigm["name"]},
                {"$set": paradigm},
                upsert=True
            )
        console.print("[green]EEG paradigm configurations added to the database.[/green]")
    except Exception as e:
        console.print(f"[red]Error adding EEG paradigm configurations: {e}[/red]")

async def add_users_to_db():
    """
    Add user data to the database.
    """
    db = await get_database()
    users_collection = db.users

    users_list = await get_users_dict()
    console.print(f"[yellow]Processed users list: {users_list}[/yellow]")
    
    try:
        for user in users_list:
            console.print(f"[cyan]Inserting user: {user}[/cyan]")
            result = await users_collection.update_one(
                {"email": user["email"]},
                {"$set": user},
                upsert=True
            )
            console.print(f"[green]User inserted/updated: {result.modified_count} modified, {result.upserted_id} upserted[/green]")
        console.print("[green]Users added to the database.[/green]")
    except Exception as e:
        console.print(f"[red]Error adding users: {e}[/red]")
        console.print(f"[yellow]Users list: {users_list}[/yellow]")
        import traceback
        console.print("[bold red]Traceback:[/bold red]")
        console.print(traceback.format_exc())
        raise  # Re-raise the exception to be caught in the calling function

async def get_users_dict():
    """
    Retrieve users configuration from the database.

    Returns:
        list: List of users configuration.
    """
    config = await load_config_from_yaml()
    users = config.get('users', [])
    console.print(f"[yellow]Raw users from config: {users}[/yellow]")
    return [{'email': user['email'], 'username': user['username']} for user in users]

async def get_database_info():
    """
    Retrieve database configuration information from the database.

    Returns:
        dict: Database configuration information.
    """
    db = await get_database()
    config_doc = await db.config.find_one({"_id": "main_config"})
    if config_doc and "database" in config_doc:
        return config_doc["database"]
    return {}

async def get_frontend_info():
    """
    Retrieve frontend configuration information from the database.

    Returns:
        dict: Frontend configuration information.
    """
    db = await get_database()
    config_collection = db.config
    frontend_config = await config_collection.find_one({"_id": "frontend"})
    if not frontend_config or 'url' not in frontend_config:
        console.print("[red]Frontend URL not found in configuration. Using default 'http://localhost:5173'.[/red]")
        return {"url": "http://localhost:5173"}
    return frontend_config

async def get_api_info():
    """
    Retrieve API configuration information from the database.

    Returns:
        dict: API configuration information.
    """
    db = await get_database()
    config_collection = db.config
    api_config = await config_collection.find_one({"_id": "api"})
    if not api_config or 'port' not in api_config:
        console.print("[red]API port not found in configuration. Using default port 3005.[/red]")
        return {"port": 3005}
    return api_config

async def get_folder_paths():
    """
    Retrieve folder paths configuration from the database.

    Returns:
        dict: Folder paths configuration information.
    """
    db = await get_database()
    config_doc = await db.config.find_one({"_id": "folder_paths"})
    if config_doc:
        config_doc.pop('_id', None)
        return config_doc
    return {}

async def get_eeg_formats_dict():
    """
    Retrieve EEG formats configuration from the database.

    Returns:
        list: List of EEG formats configuration.
    """
    db = await get_database()
    eeg_formats = await db.eeg_format.find().to_list(length=None)
    return eeg_formats

async def get_eeg_paradigms_dict():
    """
    Retrieve EEG paradigms configuration from the database.

    Returns:
        list: List of EEG paradigms configuration.
    """
    db = await get_database()
    eeg_paradigms = await db.eeg_paradigm.find().to_list(length=None)
    return eeg_paradigms

async def get_eeg_analyses_dict():
    """
    Retrieve EEG analyses configuration from the database.

    Returns:
        list: List of EEG analyses configuration.
    """
    db = await get_database()
    eeg_analyses = await db.eeg_analyses.find().to_list(length=None)
    return eeg_analyses

async def get_all_config_parameters():
    """
    Retrieve all configuration parameters from the database.

    Returns:
        dict: All configuration parameters.
    """
    db = await get_database()
    config_doc = await db.config.find_one({"_id": "main_config"})
    if config_doc:
        return {
            "database": config_doc.get("database", {}),
            "folder_paths": config_doc.get("folder_paths", {}),
            "eeg_formats": await get_eeg_formats_dict(),
            "eeg_paradigms": await get_eeg_paradigms_dict(),
            "eeg_analyses": await get_eeg_analyses_dict(),
        }
    return {}

async def test_functions():
    """
    Test various configuration retrieval functions.
    """
    console = Console()
    console.print("[bold magenta]Testing Configuration Functions[/bold magenta]")

    folder_paths = await get_folder_paths()
    console.print("[bold green]Folder Paths:[/bold green]", folder_paths)

    eeg_formats = await get_eeg_formats_dict()
    console.print("[bold green]EEG Formats:[/bold green]", eeg_formats)

    eeg_paradigms = await get_eeg_paradigms_dict()
    console.print("[bold green]EEG Paradigms:[/bold green]", eeg_paradigms)

    eeg_analyses = await get_eeg_analyses_dict()
    console.print("[bold green]EEG Analyses:[/bold green]", eeg_analyses)

if __name__ == "__main__":
    import asyncio
    asyncio.run(check_database_and_tables())
    # asyncio.run(load_config_from_yaml())
    # asyncio.run(test_functions())
