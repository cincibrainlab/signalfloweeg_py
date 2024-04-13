from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from signalfloweeg.portal.models import Base, EegFormat, EegParadigm, UploadCatalog, ImportCatalog, EegAnalyses, DatasetCatalog
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
 
def get_engine_and_session():
    engine = create_engine(db_url)
    print(f"Database URL: {db_url}")
    print(f"Engine: {engine}")  
    Session = sessionmaker(bind=engine)
    session = Session()
    return engine, session

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
        
        # Generate EEGFormat records
        for format_data in config['eeg_formats']:
            format_name = format_data['name']
            description = format_data['description']
            
            # Check if the record already exists
            existing_record = session.query(EegFormat).filter_by(name=format_name).first()
            
            # If the record does not exist, create and add it
            if not existing_record:
                eeg_format = EegFormat(name=format_name, description=description)
                session.add(eeg_format)
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

        # Generate EEGParadigm records
        for paradigm_data in config['eeg_paradigms']:
            paradigm_name = paradigm_data['name']
            description = paradigm_data['description']
            
            # Check if the record already exists
            existing_record = session.query(EegParadigm).filter_by(name=paradigm_name).first()
            
            # If the record does not exist, create and add it
            if not existing_record:
                eeg_paradigm = EegParadigm(name=paradigm_name, description=description)
                session.add(eeg_paradigm)
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

def get_upload_catalog():
    with get_db() as session:
        upload_catalog = session.query(UploadCatalog).all()
        return [
            {
                "upload_id": upload.upload_id,
                "fdt_id": upload.fdt_upload_id,
                "original_name": upload.original_name,
                "eeg_format": upload.eeg_format,
                "is_set_file": upload.is_set_file,
                "has_fdt_file": upload.has_fdt_file,
                "fdt_filename": upload.fdt_filename
            }
            for upload in upload_catalog
        ]


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
        print(f"Database URL: {db_url}")
        print(f"Engine: {engine}")
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




def get_eligible_files():
    from rich.console import Console
    from rich.table import Table

    with get_db() as session:
        # Query the ImportCatalog table to find eligible files
        eligible_files = session.query(ImportCatalog).\
            filter(ImportCatalog.status == 'IMPORTED').\
            filter(ImportCatalog.mne_load_error.is_(False)).\
            all()

        console = Console()

        table = Table(title="Eligible Files")
        table.add_column("Upload ID", style="cyan", no_wrap=True)
        table.add_column("Dataset Name", style="magenta")
        table.add_column("Sample Rate", style="green")
        table.add_column("EEG Format", style="yellow")
        table.add_column("EEG Paradigm", style="yellow")
        table.add_column("Number of Channels", style="red")
        table.add_column("Number of Epochs", style="blue")
        table.add_column("Total Samples", style="magenta")

        for file in eligible_files:
            console.print(file)
            table.add_row(
                file.upload_id,
                file.dataset_name,
                str(file.sample_rate),
                file.eeg_format if file.eeg_format else "N/A",
                file.eeg_paradigm if file.eeg_paradigm else "N/A",
                str(file.n_channels),
                str(file.n_epochs),
                str(file.total_samples)
            )

        console.print(table)

        return eligible_files

        # Iterate over the eligible files
       # for file in eligible_files:
            # Get the eeg_format and eeg_paradigm values
        #    eeg_format = file.eeg_format
        #    eeg_paradigm = file.eeg_paradigm
            
