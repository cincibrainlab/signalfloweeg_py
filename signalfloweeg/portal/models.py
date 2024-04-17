from sqlalchemy import Column, Integer, String, Text, Boolean
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database, drop_database
from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from rich.console import Console
from rich.table import Table
from signalfloweeg.portal.db_connection import get_db_url

Base = declarative_base()

console = Console()


class ConfigDB(Base):
    __tablename__ = "config"
    id = Column(Integer, primary_key=True, default=1)
    database = Column(String, nullable=False)
    frontend = Column(String, nullable=False)
    api = Column(String, nullable=False)
    folder_paths = Column(Text, nullable=False)
    eeg_formats = Column(Text, nullable=False)
    eeg_paradigms = Column(Text, nullable=False)
    eeg_analyses = Column(Text, nullable=False)

    __table_args__ = ({"sqlite_autoincrement": True},)


class CatalogBase(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True)
    status = Column(String)
    upload_id = Column(String, unique=True)
    date_added = Column(String)
    original_name = Column(String)
    dataset_name = Column(String)
    dataset_id = Column(String)
    eeg_format = Column(String)
    eeg_paradigm = Column(String)
    is_set_file = Column(Boolean)
    has_fdt_file = Column(Boolean)
    fdt_filename = Column(String)
    fdt_upload_id = Column(String)
    hash = Column(String)


class UploadCatalog(CatalogBase):
    __tablename__ = "upload_catalog"
    id = None  # Disable the 'id' column for UploadCatalog
    upload_id = Column(
        String, primary_key=True
    )  # Override 'upload_id' as the primary key
    size = Column(String)
    remove_upload = Column(Boolean)


class ImportCatalog(CatalogBase):
    __tablename__ = "import_catalog"
    id = None  # Disable the 'id' column for UploadCatalog
    upload_id = Column(
        String, primary_key=True
    )  # Override 'upload_id' as the primary key
    remove_import = Column(Boolean, name="remove")
    sample_rate = Column(Integer)
    n_channels = Column(Integer)
    n_epochs = Column(Integer)
    total_samples = Column(Integer)
    mne_load_error = Column(Boolean)


class AnalysisJobList(Base):
    __tablename__ = "analysis_joblist"

    id = Column(Integer, primary_key=True)
    job_id = Column(String)
    upload_id = Column(String, ForeignKey("import_catalog.upload_id"))
    eeg_format_id = Column(Integer, ForeignKey("eeg_format.id"))
    eeg_paradigm_id = Column(Integer, ForeignKey("eeg_paradigm.id"))
    analysis_id = Column(Integer, ForeignKey("eeg_analysis.id"))
    status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    parameters = Column(String)
    result = Column(String)

    eeg_format = relationship("EegFormat")
    eeg_paradigm = relationship("EegParadigm")
    analysis = relationship("EegAnalyses")


class DatasetCatalog(Base):
    __tablename__ = "dataset_catalog"
    dataset_name = Column(String)
    dataset_id = Column(String, primary_key=True)
    description = Column(Text)
    eeg_format_id = Column(Integer, ForeignKey("eeg_format.id"))
    eeg_paradigm_id = Column(Integer, ForeignKey("eeg_paradigm.id"))

    eeg_format = relationship("EegFormat")
    eeg_paradigm = relationship("EegParadigm")


class EegFormat(Base):
    __tablename__ = "eeg_format"
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String, unique=True)
    description = Column(Text)


class EegParadigm(Base):
    __tablename__ = "eeg_paradigm"
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String, unique=True)
    description = Column(Text)


class EegAnalyses(Base):
    __tablename__ = "eeg_analysis"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(Text)
    category = Column(String)
    valid_formats = Column(String)
    valid_paradigms = Column(String)
    parameters = Column(String)  # JSON string to store analysis parameters


def initialize_database(reset=False):
    db_url = get_db_url()

    console.print(
        "[bold]Initializing or resetting database with the following parameters:[/bold]"
    )
    console.print(f"Database URL: [green]{db_url}[/green]")
    console.print(f"Reset flag: [green]{reset}[/green]")

    conn = create_engine(db_url, echo=False)
    from rich import print as rich_print

    db_status = {"force_reset": reset, "database_exists": database_exists(conn.url)}

    rich_print("[bold magenta]Database Status:[/bold magenta]", db_status)

    if db_status["force_reset"]:
        if db_status["database_exists"]:
            drop_database(conn.url)
            console.print("Database dropped successfully.")
        else:
            console.print("Database does not exist, no need to drop.")

    if db_status["database_exists"] and not db_status["force_reset"]:
        console.print("Database sfportal present.")
    else:
        create_database(conn.url)
        console.print("Database sfportal created.")

    Base.metadata.create_all(conn)
    created_tables = conn.dialect.get_table_names(conn)

    table_verification = Table(title="Table Verification")
    table_verification.add_column("Table Name", style="cyan")
    table_verification.add_column("Status", style="green")
    table_verification.add_column("Message", style="magenta")
    for table in created_tables:
        table_verification.add_row(
            table, "Verified", f"Table {table} verified successfully."
        )
    console.print(table_verification)


if __name__ == "__main__":
    reset = True
    initialize_database(reset)
