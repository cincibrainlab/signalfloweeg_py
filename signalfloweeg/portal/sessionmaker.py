from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from signalfloweeg.portal.models import Base, EegFormat, EegParadigm, ImportCatalog, EegAnalyses, DatasetCatalog
from signalfloweeg.portal.portal_utils import load_config
import logging
import json


db_url = 'postgresql://sfportal:sfportal@localhost:3002/sfportal'
engine = create_engine(db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    Base.metadata.create_all(bind=engine)

@contextmanager
def get_db():
    db = SessionLocal()
    try:
        create_tables()  # Create tables if they don't exist
        yield db
    finally:
        db.close()

def drop_all_tables():
    try:
        engine = create_engine(db_url)
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        logging.info("All tables dropped successfully.")
    except Exception as e:
        logging.error(f"Failed to drop all tables: {e}")
    finally:
        engine.dispose()

def generate_eeg_format_and_paradigm():
    """
    Generates EEGFormat and EEGParadigm records from a YAML file.
    
    Args:
        yaml_file (str): Path to the YAML file containing the format and paradigm data.
    """
    with get_db() as session:

        config = load_config()
        
        from rich.console import Console
        from rich.table import Table

        console = Console()
        
        for format_data in config['eeg_formats']:
            format_name = format_data['name']
            description = format_data['description']
            eeg_format = EegFormat(name=format_name, description=description)
            session.merge(eeg_format)
            session.commit()      

        table = Table(title="[bold]EEG Formats[/bold]")
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Description", style="magenta")

        for format_data in config['eeg_formats']:
            table.add_row(
                format_data['name'],
                format_data['description']
            )

        console.print(table)
        console.print()


        
        for paradigm_data in config['eeg_paradigms']:
            paradigm_name = paradigm_data['name']
            description = paradigm_data['description']
            eeg_paradigm = EegParadigm(name=paradigm_name, description=description)
            session.merge(eeg_paradigm)
            session.commit()    

        table = Table(title="[bold]EEG Paradigms[/bold]")
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Description", style="magenta")

        for paradigm_data in config['eeg_paradigms']:
            table.add_row(
                paradigm_data['name'],
                paradigm_data['description']
            )

        console.print(table)
        console.print()
        for analysis_data in config['eeg_analyses']:
            analysis_name = analysis_data['name']
            analysis_category = analysis_data['category']
            analysis_description = analysis_data['description']
            analysis_valid_formats = json.dumps(analysis_data['valid_formats'])
            analysis_valid_paradigms = json.dumps(analysis_data['valid_paradigms'])
            analysis_parameters = json.dumps(analysis_data['parameters'])
            
            eeg_analysis = EegAnalyses(
                name=analysis_name,
                category=analysis_category,
                description=analysis_description,
                valid_formats=json.dumps(analysis_valid_formats),
                valid_paradigms=json.dumps(analysis_valid_paradigms),
                parameters=json.dumps(analysis_parameters)
            )
            session.merge(eeg_analysis)
            session.commit()
    


        for analysis_data in config['eeg_analyses']:
            table = Table(title=f"[bold]Analysis Name: {analysis_data['name']}[/bold]")
            table.add_column("Category", style="cyan", no_wrap=True)
            table.add_column("Description", style="magenta")
            table.add_column("Valid Formats", style="green")
            table.add_column("Valid Paradigms", style="yellow")
            table.add_column("Parameters", style="blue")

            table.add_row(
                analysis_data['category'],
                analysis_data['description'],
                str(analysis_data['valid_formats']),
                str(analysis_data['valid_paradigms']),
                str(analysis_data['parameters'])
            )

            console.print(table)
            console.print()

        logging.info("EEGFormat and EEGParadigm records generated successfully.")
        session.close()

def get_import_info(upload_id: str):
    """
    Retrieves the import information for the given upload_id.

    Args:
        upload_id (str): The upload ID to retrieve the import information for.

    Returns:
        dict: A dictionary containing the import information.
    """
    with get_db() as db:
        try:
            import_record = db.query(ImportCatalog).filter(ImportCatalog.upload_id == upload_id).first()
            if import_record:
                return {
                    "original_name": import_record.original_name,
                    "dataset_name": import_record.dataset_name,
                    "dataset_id": import_record.dataset_id,
                    "date_added": import_record.date_added,
                    "upload_id": import_record.upload_id,
                    "remove_import": import_record.remove_import,
                    "is_set_file": import_record.is_set_file,
                    "has_fdt_file": import_record.has_fdt_file,
                    "fdt_filename": import_record.fdt_filename,
                    "fdt_upload_id": import_record.fdt_upload_id,
                    "hash": import_record.hash,
                    "mne_load_error": import_record.mne_load_error,
                    "sample_rate": import_record.sample_rate,
                    "n_channels": import_record.n_channels,
                    "n_epochs": import_record.n_epochs,
                    "total_samples": import_record.total_samples
                }
            else:
                return {"error": f"No import record found for upload_id: {upload_id}"}
        except Exception as e:
            logging.error(f"Error retrieving import information for upload_id {upload_id}: {e}")
            return {"error": f"Error retrieving import information for upload_id {upload_id}"}


def generate_database_summary():
    """
    Generates a summary of the database tables and records.
    
    Args:
        session (sqlalchemy.orm.Session): The database session.
    
    Returns:
        dict: A dictionary containing the table names and record counts.
    """
    with get_db() as session:
        # Get the number of tables
        table_count = len(Base.metadata.tables)
        
        # Get the number of records in each table
        record_counts = {}
        for table in Base.metadata.tables.values():
            record_count = session.query(table).count()
            record_counts[table.name] = record_count
        
        # Create a rich table to display the information
        from rich.console import Console
        from rich.table import Table
        
        console = Console()
        table = Table(title="Database Summary")
        table.add_column("Table", style="cyan", no_wrap=True)
        table.add_column("Records", style="magenta", justify="right")
        
        for table_name, record_count in record_counts.items():
            table.add_row(table_name, str(record_count))
        
        console.print(table)

def get_eeg_formats():
    with get_db() as session:
        eeg_formats = session.query(EegFormat).all()
        return [
            {
                "id": eeg_format.id,
                "name": eeg_format.name,
                "description": eeg_format.description
            }
            for eeg_format in eeg_formats
        ]

def get_eeg_paradigms():
    with get_db() as session:
        eeg_paradigms = session.query(EegParadigm).all()
        return [
            {
                "id": eeg_paradigm.id,
                "name": eeg_paradigm.name,
                "description": eeg_paradigm.description
            }
            for eeg_paradigm in eeg_paradigms
        ]

def get_dataset_info():
    with get_db() as session:
        datasets = session.query(DatasetCatalog).all()
        return [
            {
                "dataset_id": dataset.dataset_id,
                "dataset_name": dataset.dataset_name,
                "description": dataset.description,
                "eeg_format": dataset.eeg_format.name if dataset.eeg_format else None,
                "eeg_paradigm": dataset.eeg_paradigm.name if dataset.eeg_paradigm else None
            }
            for dataset in datasets
        ]
