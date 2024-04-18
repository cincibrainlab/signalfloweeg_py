import json
from sqlalchemy.exc import SQLAlchemyError
from signalfloweeg.portal.models import ConfigDB, Startup, initialize_database
import yaml
import os
from rich.console import Console

from signalfloweeg.portal.db_connection import get_session

console = Console()
console.print("[bold]Module portal_config is currently running...[/bold]")


def is_config_table_present():
    """
    Checks if the configuration table exists in the database.

    Returns:
        bool: True if the configuration table exists, False otherwise.
    """
    try:
        with get_session() as session:
            # Attempt to query the first row of the ConfigDB table
            if session.query(ConfigDB).first() is not None:
                return True
            else:
                return False
    except SQLAlchemyError as e:
        print(f"Error checking for ConfigDB table: {e}")
        return False


def load_config():
    """
    Loads the YAML configuration file.

    Args:
        file_path (str): The path to the YAML configuration file. Defaults to YAML_CONFIG.

    Returns:
        dict: The loaded YAML configuration as a dictionary, or None if an error occurs.
    """

    file_path = get_portal_config_path()

    if os.path.isfile(file_path):
        config_file_path = file_path
    else:
        config_file_path = os.path.join(os.path.dirname(__file__), file_path)

    console = Console()
    #console.print(f"Using: [bold]{config_file_path}[/bold]")

    try:
        with open(file_path, "r") as stream:
            config_db = yaml.safe_load(stream)
            return config_db
    except FileNotFoundError:
        print(f"File {file_path} not found.")
    except yaml.YAMLError as exc:
        print(exc)


def load_config_from_yaml():
    data = load_config()
    try:
        with get_session() as session:
            # Check if the config_db already exists, if so, update it
            config_db = session.query(ConfigDB).filter_by(id=1).first()
            if not config_db:
                config_db = ConfigDB(id=1)
                session.add(config_db)

            config_db.database = json.dumps(data["database"])
            config_db.frontend = json.dumps(data["frontend"])
            config_db.api = json.dumps(data["api"])
            config_db.folder_paths = json.dumps(data["folder_paths"])
            config_db.eeg_formats = json.dumps(data["eeg_formats"])
            config_db.eeg_paradigms = json.dumps(data["eeg_paradigms"])
            config_db.eeg_analyses = json.dumps(data["eeg_analyses"])

            session.commit()

            add_eeg_format_to_db()
            add_eeg_paradigm_to_db()
            add_eeg_analysis_to_db()
            
            # Adding rich print out in a table format for debugging
            from rich.table import Table

            table = Table(title="ConfigDB Update Debug")
            table.add_column("Column", style="cyan")
            table.add_column("Value", style="magenta")
            table.add_row("database", json.dumps(data["database"]))
            table.add_row("frontend", json.dumps(data["frontend"]))
            table.add_row("api", json.dumps(data["api"]))
            table.add_row("database_url", data["database"]["url"])
            table.add_row("database_reset", str(data["database"]["reset"]))
            table.add_row("eeg_formats", json.dumps(data["eeg_formats"]))
            table.add_row("eeg_paradigms", json.dumps(data["eeg_paradigms"]))
            table.add_row("eeg_analyses", json.dumps(data["eeg_analyses"]))
            console = Console()
            console.print(table)

    except SQLAlchemyError as e:
        print(f"Database error when updating configuration: {e}")
        session.rollback()

def add_eeg_format_to_db():
    from signalfloweeg.portal.models import EegFormat

    eeg_formats_list = get_eeg_formats_dict()  # Assuming this returns a list of dictionaries
    with get_session() as session:
        # Drop the existing table if it exists
        EegFormat.__table__.drop(session.bind, checkfirst=True)
        # Create a new table
        EegFormat.__table__.create(session.bind)

        for eeg_format in eeg_formats_list:
            new_format = EegFormat(name=eeg_format['name'], description=eeg_format['description'])
            session.add(new_format)
        try:
            session.commit()
            print("Added all new EEG formats.")
        except SQLAlchemyError as e:
            print(f"Failed to add new EEG formats: {e}")
            session.rollback()

def add_eeg_paradigm_to_db():
    from signalfloweeg.portal.models import EegParadigm

    eeg_paradigms_list = get_eeg_paradigms_dict()  # Assuming this returns a list of dictionaries
    with get_session() as session:
        # Drop the existing table if it exists
        EegParadigm.__table__.drop(session.bind, checkfirst=True)
        # Create a new table
        EegParadigm.__table__.create(session.bind)

        for eeg_paradigm in eeg_paradigms_list:
            new_paradigm = EegParadigm(name=eeg_paradigm['name'], description=eeg_paradigm['description'])
            session.add(new_paradigm)
        try:
            session.commit()
            print("Added all new EEG paradigms.")
        except SQLAlchemyError as e:
            print(f"Failed to add new EEG paradigms: {e}")
            session.rollback()

def add_eeg_analysis_to_db():
    from signalfloweeg.portal.models import EegAnalyses

    eeg_analyses_list = get_eeg_analyses_dict()  # Assuming this returns a list of dictionaries
    with get_session() as session:
        # Drop the existing table if it exists
        EegAnalyses.__table__.drop(session.bind, checkfirst=True)
        # Create a new table
        EegAnalyses.__table__.create(session.bind)

        for eeg_analysis in eeg_analyses_list:
            new_analysis = EegAnalyses(
                name=eeg_analysis['name'],
                description=eeg_analysis['description'],
                category=eeg_analysis['category'],
                valid_formats=json.dumps(eeg_analysis['valid_formats']),
                valid_paradigms=json.dumps(eeg_analysis['valid_paradigms']),
                parameters=json.dumps(eeg_analysis.get('parameters', {}))  # Default to empty JSON if not provided
            )
            session.add(new_analysis)
        try:
            session.commit()
            print("Added all new EEG analyses.")
        except SQLAlchemyError as e:
            print(f"Failed to add new EEG analyses: {e}")
            session.rollback()

def json_to_dict(json_str):
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return {}


def get_database_info():
    with get_session() as session:
        try:
            config_db = session.query(ConfigDB).first()
            if config_db:
                return {
                    "database_url": config_db.database_url,
                    "database_reset": config_db.database_reset,
                }
        except SQLAlchemyError as e:
            print(f"Database error when retrieving database info: {e}")
    return {}


def get_frontend_info():
    with get_session() as session:
        try:
            config_db = session.query(ConfigDB).first()
            if config_db:
                return json_to_dict(config_db.frontend)
        except SQLAlchemyError as e:
            print(f"Database error when retrieving frontend info: {e}")
    return {}

def get_api_info():
    with get_session() as session:
        try:
            config_db = session.query(ConfigDB).first()
            if config_db:
                return json_to_dict(config_db.api)
        except SQLAlchemyError as e:
            print(f"Database error when retrieving api info: {e}")
    return {}

def get_folder_paths():
    with get_session() as session:
        try:
            config_db = session.query(ConfigDB).first()
            if config_db:
                return json_to_dict(config_db.folder_paths)
        except SQLAlchemyError as e:
            print(f"Database error when retrieving folder paths: {e}")
    return {}


def get_eeg_formats_dict():
    with get_session() as session:
        try:
            config_db = session.query(ConfigDB).first()
            if config_db and config_db.eeg_formats:
                return json_to_dict(config_db.eeg_formats)
        except SQLAlchemyError as e:
            print(f"Database error when retrieving EEG formats: {e}")
    return []


def get_eeg_paradigms_dict():
    with get_session() as session:
        try:
            config_db = session.query(ConfigDB).first()
            if config_db and config_db.eeg_paradigms:
                return json_to_dict(config_db.eeg_paradigms)
        except SQLAlchemyError as e:
            print(f"Database error when retrieving EEG paradigms: {e}")
    return []


def get_eeg_analyses_dict():
    with get_session() as session:
        try:
            config_db = session.query(ConfigDB).first()
            if config_db and config_db.eeg_analyses:
                return json_to_dict(config_db.eeg_analyses)
        except SQLAlchemyError as e:
            print(f"Database error when retrieving EEG analyses: {e}")
    return []


def get_all_config_parameters():
    with get_session() as session:
        try:
            config_db = session.query(ConfigDB).first()
            if config_db:
                return {
                    "database_url": config_db.database_url,
                    "database_reset": config_db.database_reset,
                    "folder_paths": json_to_dict(config_db.folder_paths)
                    if config_db.folder_paths
                    else {},
                    "eeg_formats": json_to_dict(config_db.eeg_formats)
                    if config_db.eeg_formats
                    else [],
                    "eeg_paradigms": json_to_dict(config_db.eeg_paradigms)
                    if config_db.eeg_paradigms
                    else [],
                    "eeg_analyses": json_to_dict(config_db.eeg_analyses)
                    if config_db.eeg_analyses
                    else [],
                }
        except SQLAlchemyError as e:
            print(f"Database error when retrieving all config_db parameters: {e}")
    return {}


def set_portal_config_path(script_path):
    try:
        initialize_database(reset=False)
        if not os.path.exists(script_path):
            return "Invalid script path"
        with get_session() as session:
            # Check if the config_db already exists, if so, update it
            startup_record = session.query(Startup).filter_by(id=1).first()
            if not startup_record:
                startup_record = Startup(id=1)
                session.add(startup_record)

            startup_record.sf_config_path = script_path
            session.add(startup_record)
            session.commit()
            startup_record = session.query(Startup).filter_by(id=1).first()

            # Adding rich print out in a table format for debugging
            from rich.table import Table

            table = Table(title="Startup Update")
            table.add_column("Column", style="cyan")
            table.add_column("Value", style="magenta")
            table.add_row("portal_script", script_path)

            console = Console()
            console.print(table)

            load_config_from_yaml()

    except SQLAlchemyError as e:
        print(f"Database error when updating configuration: {e}")
        session.rollback()


def get_portal_config_path():
    with get_session() as session:
        try:
            startup_record = session.query(Startup).filter_by(id=1).first()
            if startup_record:
                return (startup_record.sf_config_path)
            else:
                return None
        except SQLAlchemyError as e:
            print(f"Database error when retrieving portal config: {e}")
    return {"sf_config_path": None}


def test_functions():
    console = Console()
    console.print("[bold magenta]Testing Configuration Functions[/bold magenta]")

    # Test get_folder_paths
    folder_paths = get_folder_paths()
    console.print("[bold green]Folder Paths:[/bold green]", folder_paths)

    # Test get_eeg_formats
    eeg_formats = get_eeg_formats()
    console.print("[bold green]EEG Formats:[/bold green]", eeg_formats)

    # Test get_eeg_paradigms
    eeg_paradigms = get_eeg_paradigms()
    console.print("[bold green]EEG Paradigms:[/bold green]", eeg_paradigms)

    # Test get_eeg_analyses
    eeg_analyses = get_eeg_analyses()
    console.print("[bold green]EEG Analyses:[/bold green]", eeg_analyses)


if __name__ == "__main__":
    print(is_config_table_present())
    print(get_portal_config_path())
    load_config_from_yaml()
    # config_db = get_all_config_parameters()
    #test_functions()
