from sqlalchemy import Column, Integer, String, Text, Boolean
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database, drop_database
from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from rich.console import Console
from rich.table import Table
from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import inspect

from signalfloweeg.portal.db_connection import get_db_url

Base = declarative_base()

console = Console()

class Startup(Base):
    __tablename__ = "startup_table"
    id = Column(Integer, primary_key=True, default=1)
    sf_config_path = Column(String, nullable=True)
    __table_args__ = ({"sqlite_autoincrement": True},)

class Users(Base):
    __tablename__ = "users"
    id = None
    user_id = Column(String, primary_key=True)
    username = Column(String, unique=True, nullable=True)
    email = Column(String, unique=True, nullable=True)
    hashed_password = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=True)

class ConfigDB(Base):
    __tablename__ = "config"
    id = Column(Integer, primary_key=True, default=1)
    database = Column(String, nullable=True)
    frontend = Column(String, nullable=True)
    api = Column(String, nullable=True)
    users = Column(Text, nullable=True)
    folder_paths = Column(Text, nullable=True)
    eeg_formats = Column(Text, nullable=True)
    eeg_paradigms = Column(Text, nullable=True)
    eeg_analyses = Column(Text, nullable=True)

    __table_args__ = ({"sqlite_autoincrement": True},)

class DatasetCatalog(Base):
    __tablename__ = "dataset_catalog"
    dataset_name = Column(String)
    dataset_id = Column(String, primary_key=True)
    description = Column(Text)

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
    
class CatalogBase(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True)
    status = Column(String)
    upload_id = Column(String, unique=True)
    date_added = Column(String)
    original_name = Column(String)
    eeg_format = Column(String)
    eeg_paradigm = Column(String)
    is_set_file = Column(Boolean)
    has_fdt_file = Column(Boolean)
    fdt_filename = Column(String)
    fdt_upload_id = Column(String)
    upload_email = Column(String)    
    hash = Column(String)

    @declared_attr
    def dataset_id(cls):
        # Defines a foreign key field, allowing subclass-specific customization
        return Column(String, ForeignKey("dataset_catalog.dataset_id"))

    @declared_attr
    def dataset(cls):
        backref_name = f"{cls.__name__.lower()}_entries"
        # Defines a relationship, dynamically linked to the subclass's foreign key
        return relationship("DatasetCatalog", backref=backref(backref_name, cascade="all, delete-orphan"))

    @hybrid_property
    def dataset_name(self):
        return self.dataset.dataset_name if self.dataset else None

    @hybrid_property
    def dataset_description(self):
        return self.dataset.description if self.dataset else None

# Explanation of changes:
# @declared_attr: Used here to ensure that the foreign key and relationship are set up correctly for each subclass,
# allowing SQLAlchemy to manage the inheritance and linkage dynamically.
# This method allows each subclass that inherits from CatalogBase to have its specific linkage to the DatasetCatalog,
# facilitating correct ORM behavior across different inheriting models.

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
    remove_import = Column(Boolean)
    sample_rate = Column(Integer)
    n_channels = Column(Integer)
    n_epochs = Column(Integer)
    total_samples = Column(Integer)
    mne_load_error = Column(Boolean)


class AnalysisConfig(Base):
    __tablename__ = "analysis_configs"
    id = Column(String, primary_key=True)
    function_name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    eeg_formats = Column(String, nullable=False)
    eeg_paradigms = Column(String, nullable=False)
    parameters = Column(String, nullable=False)
    version = Column(String, nullable=False)
    active = Column(Boolean, default=True)  # New field to mark if active or not
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AnalysisJobList(Base):
    __tablename__ = "analysis_joblist"
    id = Column(Integer, primary_key=True)
    job_id = Column(String)
    upload_id = Column(String, ForeignKey("import_catalog.upload_id"))
    eeg_format_name = Column(String)
    eeg_paradigm_name = Column(String)
    eeg_analysis_name = Column(String)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    parameters = Column(String)
    result = Column(String)
    

class EegAnalyses(Base):
    __tablename__ = "eeg_analyses"
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
        print(conn.url)
        console.print("Database sfportal created.")

    Base.metadata.create_all(conn)
    inspector = inspect(conn)
    created_tables = inspector.get_table_names()
    #created_tables = conn.dialect.get_table_names(conn)

    table_verification = Table(title="Table Verification")
    table_verification.add_column("Table Name", style="cyan")
    table_verification.add_column("Status", style="green")
    table_verification.add_column("Fields", style="magenta")
    for table in created_tables:
        table_fields = ", ".join([column.name for column in Base.metadata.tables[table].columns])
        table_verification.add_row(
            table, "Verified", f"Table name: {table}, Fields: {table_fields}"
        )
    console.print(table_verification)

if __name__ == "__main__":
    reset = True
    initialize_database(reset)
