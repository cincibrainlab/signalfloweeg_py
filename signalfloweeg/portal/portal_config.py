
import json
from sqlalchemy.exc import SQLAlchemyError
from signalfloweeg.portal.models import (
    ConfigDB, Startup, initialize_database, Users
)
import yaml
import os
from rich.console import Console
from sqlalchemy import inspect


from signalfloweeg.portal.db_connection import get_session, get_engine

console = Console()
console.print("[bold]Module portal_config is currently running...[/bold]")


def get_portal_config_path():
    with get_session() as session:
        startup_record = session.query(Startup).filter_by(id=1).first()
        if startup_record:
            return startup_record.sf_config_path
        else:
            return None



def is_config_table_present():
    """
    Check if the configuration table exists in the database.

    Returns:
        bool: True if the configuration table exists, False otherwise.
    """
    try:
        with get_session() as session:
            return session.query(ConfigDB).first() is not None
    except SQLAlchemyError as e:
        print(f"Error checking for ConfigDB table: {e}")
        return False

def check_database_and_tables():
    """
    Verify the presence and structure of required tables in the database.

    Returns:
        bool: True if all required tables and their structures are correct, otherwise False.
    """
    console = Console()
    engine = get_engine()
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    required_tables = {
        'startup_table': ['id', 'sf_config_path'],
        'config': ['id', 'database', 'frontend', 'api', 'folder_paths', 'eeg_formats', 'eeg_paradigms', 'eeg_analyses'],
        'upload_catalog': ['status', 'date_added', 'original_name', 'dataset_id', 'eeg_format', 'eeg_paradigm', 'is_set_file', 'has_fdt_file', 'fdt_filename', 'fdt_upload_id', 'hash', 'upload_id', 'size', 'remove_upload'],
        'dataset_catalog': ['dataset_name', 'dataset_id', 'description'],
        'import_catalog': ['status', 'date_added', 'original_name', 'dataset_id', 'eeg_format', 'eeg_paradigm', 'is_set_file', 'has_fdt_file', 'fdt_filename', 'fdt_upload_id', 'hash', 'upload_id', 'remove_import', 'sample_rate', 'n_channels', 'n_epochs', 'total_samples', 'mne_load_error'],
        'analysis_joblist': ['id', 'job_id', 'upload_id', 'eeg_format_name', 'eeg_paradigm_name', 'eeg_analysis_name', 'status', 'created_at', 'parameters', 'result'],
        'eeg_paradigm': ['id', 'name', 'description'],
        'eeg_analyses': ['id', 'name', 'description', 'category', 'valid_formats', 'valid_paradigms', 'parameters'],
        'eeg_format': ['id', 'name', 'description'],
        'users': ['user_id', 'username', 'email', 'hashed_password', 'is_active', 'is_superuser']
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

    return not missing_tables and not incorrect_structure

def load_config():
    """
    Load the YAML configuration file.

    Returns:
        dict: The loaded YAML configuration as a dictionary, or None if an error occurs.
    """
    file_path = get_portal_config_path()

    if not os.path.isfile(file_path):
        file_path = os.path.join(os.path.dirname(__file__), file_path)

    try:
        with open(file_path, "r") as stream:
            return yaml.safe_load(stream)
    except FileNotFoundError:
        print(f"File {file_path} not found.")
    except yaml.YAMLError as exc:
        print(exc)
def load_config_from_yaml():
    """
    Load configuration from YAML and update the database accordingly.
    Returns:
        bool: True if successful, False otherwise.
    """
    console = Console()
    data = load_config()
    if data is None:
        return False

    try:
        with get_session() as session:
            config_db = session.query(ConfigDB).filter_by(id=1).first()
            if not config_db:
                config_db = ConfigDB(id=1)
                session.add(config_db)

            try:
                config_db.database = json.dumps(data["database"])
                config_db.frontend = json.dumps(data["frontend"])
                config_db.api = json.dumps(data["api"])
                config_db.users = json.dumps(data["users"])
                config_db.folder_paths = json.dumps(data["folder_paths"])
                config_db.eeg_formats = json.dumps(data["eeg_formats"])
                config_db.eeg_paradigms = json.dumps(data["eeg_paradigms"])
                config_db.eeg_analyses = json.dumps(data["eeg_analyses"])
            except KeyError as e:
                console.print(f"[red]Error: Missing expected configuration key {e} in portal.yaml[/red]")
                return False

            session.commit()

            add_eeg_format_to_db()
            add_eeg_paradigm_to_db()
            add_email_to_db()
            add_eeg_analysis_to_db()
            
            from rich.table import Table

            table = Table(title="ConfigDB Update Debug")
            table.add_column("Column", style="cyan")
            table.add_column("Value", style="magenta")
            table.add_row("database", json.dumps(data["database"]))
            table.add_row("frontend", json.dumps(data["frontend"]))
            table.add_row("api", json.dumps(data["api"]))
            table.add_row("users", json.dumps(data["users"]))
            table.add_row("database_url", data["database"]["url"])
            table.add_row("database_reset", str(data["database"]["reset"]))
            table.add_row("eeg_formats", json.dumps(data["eeg_formats"]))
            table.add_row("eeg_paradigms", json.dumps(data["eeg_paradigms"]))
            table.add_row("eeg_analyses", json.dumps(data["eeg_analyses"]))
            console.print(table)

            return True

    except SQLAlchemyError as e:
        print(f"Database error when updating configuration: {e}")
        session.rollback()
        return False

def add_eeg_format_to_db():
    """
    Add EEG format data to the database.
    """
    from signalfloweeg.portal.models import EegFormat

    eeg_formats_list = get_eeg_formats_dict()
    with get_session() as session:
        EegFormat.__table__.drop(session.bind, checkfirst=True)
        EegFormat.__table__.create(session.bind)

        for eeg_format in eeg_formats_list:
            new_format = EegFormat(name=eeg_format['name'], description=eeg_format['description'])
            session.add(new_format)
        try:
            session.commit()
            console.print("✅ Added all new EEG formats.")
        except SQLAlchemyError as e:
            console.print(f"❌ Failed to add new EEG formats: {e}")
            session.rollback()

def add_eeg_paradigm_to_db():
    """
    Add EEG paradigm data to the database.
    """
    from signalfloweeg.portal.models import EegParadigm

    eeg_paradigms_list = get_eeg_paradigms_dict()
    with get_session() as session:
        EegParadigm.__table__.drop(session.bind, checkfirst=True)
        EegParadigm.__table__.create(session.bind)

        for eeg_paradigm in eeg_paradigms_list:
            new_paradigm = EegParadigm(name=eeg_paradigm['name'], description=eeg_paradigm['description'])
            session.add(new_paradigm)
        try:
            session.commit()
            console.print("✅ Added all new EEG paradigms.")
        except SQLAlchemyError as e:
            console.print(f"❌ Failed to add new EEG paradigms: {e}")
            session.rollback()

def add_eeg_analysis_to_db():
    """
    Add EEG analysis data to the database.
    """
    from signalfloweeg.portal.models import EegAnalyses

    eeg_analyses_list = get_eeg_analyses_dict()
    with get_session() as session:
        EegAnalyses.__table__.drop(session.bind, checkfirst=True)
        EegAnalyses.__table__.create(session.bind)

        for eeg_analysis in eeg_analyses_list:
            new_analysis = EegAnalyses(
                name=eeg_analysis['name'],
                description=eeg_analysis['description'],
                category=eeg_analysis['category'],
                valid_formats=json.dumps(eeg_analysis['valid_formats']),
                valid_paradigms=json.dumps(eeg_analysis['valid_paradigms']),
                parameters=json.dumps(eeg_analysis.get('parameters', {}))
            )
            session.add(new_analysis)
        try:
            session.commit()
            console.print("✅ Added all new EEG analyses.")
        except SQLAlchemyError as e:
            console.print(f"❌ Failed to add new EEG analyses: {e}")
            session.rollback()

def add_email_to_db():
    """
    Add email data to the database.
    """
    from signalfloweeg.portal.models import Users

    emails_list = get_users_dict()
    with get_session() as session:
        Users.__table__.drop(session.bind, checkfirst=True)
        Users.__table__.create(session.bind)

        import hashlib

        for email in emails_list:
            hashed_user_id = hashlib.sha256(email['email'].encode()).hexdigest()
            new_email = Users(user_id=hashed_user_id, email=email['email'])
            session.merge(new_email)
        try:
            session.commit()
            console.print("✅ Added all new emails.")
        except SQLAlchemyError as e:
            console.print(f"❌ Failed to add new emails: {e}")
            session.rollback()

def json_to_dict(json_str):
    """
    Convert a JSON string to a dictionary.

    Args:
        json_str (str): JSON string to be converted.

    Returns:
        dict: Dictionary representation of the JSON string.
    """
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return {}

def get_database_info():
    """
    Retrieve database configuration information from the database.

    Returns:
        dict: Database configuration information.
    """
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
    """
    Retrieve frontend configuration information from the database.

    Returns:
        dict: Frontend configuration information.
    """
    with get_session() as session:
        try:
            config_db = session.query(ConfigDB).first()
            if config_db:
                return json_to_dict(config_db.frontend)
        except SQLAlchemyError as e:
            console.print(f"❌ Database error when retrieving frontend info: {e}")
    return {}

def get_api_info():
    """
    Retrieve API configuration information from the database.

    Returns:
        dict: API configuration information.
    """
    with get_session() as session:
        try:
            config_db = session.query(ConfigDB).first()
            if config_db:
                return json_to_dict(config_db.api)
        except SQLAlchemyError as e:
            console.print(f"❌ Database error when retrieving api info: {e}")
    return {}

def get_folder_paths():
    """
    Retrieve folder paths configuration from the database.

    Returns:
        dict: Folder paths configuration information.
    """
    with get_session() as session:
        try:
            config_db = session.query(ConfigDB).first()
            if config_db:
                return json_to_dict(config_db.folder_paths)
        except SQLAlchemyError as e:
            console.print(f"❌ Database error when retrieving folder paths: {e}")
    return {}

def get_eeg_formats_dict():
    """
    Retrieve EEG formats configuration from the database.

    Returns:
        list: List of EEG formats configuration.
    """
    with get_session() as session:
        try:
            config_db = session.query(ConfigDB).first()
            if config_db and config_db.eeg_formats:
                return json_to_dict(config_db.eeg_formats)
        except SQLAlchemyError as e:
            console.print(f"❌ Database error when retrieving EEG formats: {e}")
    return []

def get_eeg_paradigms_dict():
    """
    Retrieve EEG paradigms configuration from the database.

    Returns:
        list: List of EEG paradigms configuration.
    """
    with get_session() as session:
        try:
            config_db = session.query(ConfigDB).first()
            if config_db and config_db.eeg_paradigms:
                return json_to_dict(config_db.eeg_paradigms)
        except SQLAlchemyError as e:
            console.print(f"❌ Database error when retrieving EEG paradigms: {e}")
    return []

def get_eeg_analyses_dict():
    """
    Retrieve EEG analyses configuration from the database.

    Returns:
        list: List of EEG analyses configuration.
    """
    with get_session() as session:
        try:
            config_db = session.query(ConfigDB).first()
            if config_db and config_db.eeg_analyses:
                return json_to_dict(config_db.eeg_analyses)
        except SQLAlchemyError as e:
            console.print(f"❌ Database error when retrieving EEG analyses: {e}")
    return []

def get_users_dict():
    """
    Retrieve users configuration from the database.

    Returns:
        list: List of users configuration.
    """
    with get_session() as session:
        try:
            config_db = session.query(ConfigDB).first()
            if config_db and config_db.users:
                return json_to_dict(config_db.users)
        except SQLAlchemyError as e:
            console.print(f"❌ Database error when retrieving users: {e}")
    return []


def get_all_config_parameters():
    """
    Retrieve all configuration parameters from the database.

    Returns:
        dict: All configuration parameters.
    """
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
            console.print(f"❌ Database error when retrieving all config_db parameters: {e}")
    return {}

def test_functions():
    """
    Test various configuration retrieval functions.
    """
    console = Console()
    console.print("[bold magenta]Testing Configuration Functions[/bold magenta]")

    folder_paths = get_folder_paths()
    console.print("[bold green]Folder Paths:[/bold green]", folder_paths)

    eeg_formats = get_eeg_formats_dict()
    console.print("[bold green]EEG Formats:[/bold green]", eeg_formats)

    eeg_paradigms = get_eeg_paradigms_dict()
    console.print("[bold green]EEG Paradigms:[/bold green]", eeg_paradigms)

    eeg_analyses = get_eeg_analyses_dict()
    console.print("[bold green]EEG Analyses:[/bold green]", eeg_analyses)

if __name__ == "__main__":
    check_database_and_tables()
    print(is_config_table_present())
    print(get_portal_config_path())
    load_config_from_yaml()
    # config_db = get_all_config_parameters()
    #test_functions()
