from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import signalfloweeg.portal as portal

import logging

from rich.console import Console
from rich.table import Table

db_url = "postgresql://sfportal:sfportal@localhost:3002/sfportal"
engine = create_engine(db_url, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def get_db():
    # Now connect to the new or existing database
    engine = create_engine(db_url, echo=False)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        portal.models.initialize_database()  # Create tables if they don't exist
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


def get_upload_catalog():
    with get_db() as session:
        upload_catalog = session.query(portal.models.UploadCatalog).all()
        return [
            {
                "upload_id": upload.upload_id,
                "fdt_id": upload.fdt_upload_id,
                "original_name": upload.original_name,
                "eeg_format": upload.eeg_format,
                "is_set_file": upload.is_set_file,
                "has_fdt_file": upload.has_fdt_file,
                "fdt_filename": upload.fdt_filename,
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
            import_record = (
                db.query(portal.models.ImportCatalog)
                .filter(portal.models.ImportCatalog.upload_id == upload_id)
                .first()
            )
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
                    "total_samples": import_record.total_samples,
                }
            else:
                return {"error": f"No import record found for upload_id: {upload_id}"}
        except Exception as e:
            logging.error(
                f"Error retrieving import information for upload_id {upload_id}: {e}"
            )
            return {
                "error": f"Error retrieving import information for upload_id {upload_id}"
            }


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

        base_tables = portal.models.Base.metadata.tables

        # Get the number of records in each table
        record_counts = {}
        for table in base_tables.values():
            record_count = session.query(table).count()
            record_counts[table.name] = record_count

        console = Console()
        table = Table(title="Database Summary")
        table.add_column("Table", style="cyan", no_wrap=True)
        table.add_column("Records", style="magenta", justify="right")

        for table_name, record_count in record_counts.items():
            table.add_row(table_name, str(record_count))

        console.print(table)


def get_eligible_files():
    with get_db() as session:
        # Query the ImportCatalog table to find eligible files
        eligible_files = (
            session.query(portal.models.ImportCatalog)
            .filter(portal.models.ImportCatalog.status == "IMPORTED")
            .filter(portal.models.ImportCatalog.mne_load_error.is_(False))
            .all()
        )

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
                str(file.total_samples),
            )

        console.print(table)

        return eligible_files

