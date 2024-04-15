from sqlalchemy import (
    Column, Integer, String, Text, Boolean, 
    ForeignKey, DateTime
)
from sqlalchemy.orm import (
    declarative_base, relationship
)
from sqlalchemy import create_engine
from datetime import datetime
from sqlalchemy_utils import database_exists, create_database, drop_database

import signalfloweeg.portal as portal

Base = declarative_base()

class EEGFileCatalog(Base):
    __tablename__ = 'eeg_file_catalog'
    id = Column(Integer, primary_key=True)
    filename = Column(String)
    dataset_name = Column(String)
    dataset_id = Column(String)
    eeg_format = Column(String)
    eeg_paradigm = Column(String)   
    storage = Column(Text, unique=True)
    upload_id = Column(String, unique=True)
    size = Column(String)
    hash = Column(String)
    has_fdt_file = Column(Boolean)
    fdt_filename = Column(String)
    set_filename = Column(String)
    status = Column(String)
    remove_upload = Column(Boolean)

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

    __tablename__ = 'upload_catalog'
    id = None  # Disable the 'id' column for UploadCatalog
    upload_id = Column(String, primary_key=True)  # Override 'upload_id' as the primary key
    size = Column(String)
    remove_upload = Column(Boolean)
    
class ImportCatalog(CatalogBase):
    __tablename__ = 'import_catalog'
    id = None  # Disable the 'id' column for UploadCatalog
    upload_id = Column(String, primary_key=True)  # Override 'upload_id' as the primary key
    remove_import = Column(Boolean, name='remove')
    sample_rate = Column(Integer)
    n_channels = Column(Integer)
    n_epochs = Column(Integer)
    total_samples = Column(Integer)
    mne_load_error = Column(Boolean)

class AnalysisJobList(Base):
    __tablename__ = 'analysis_joblist'
    
    id = Column(Integer, primary_key=True)
    job_id = Column(String)
    upload_id = Column(String, ForeignKey('import_catalog.upload_id'))
    eeg_format_id = Column(Integer, ForeignKey('eeg_format.id'))
    eeg_paradigm_id = Column(Integer, ForeignKey('eeg_paradigm.id'))
    analysis_id = Column(Integer, ForeignKey('eeg_analysis.id'))
    status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    parameters = Column(String)
    result = Column(String)
    
    eeg_format = relationship("EegFormat")
    eeg_paradigm = relationship("EegParadigm")
    analysis = relationship("EegAnalyses")

class DatasetCatalog(Base):
    __tablename__ = 'dataset_catalog'
    dataset_name = Column(String)
    dataset_id = Column(String, primary_key=True)
    description = Column(Text)
    eeg_format_id = Column(Integer, ForeignKey('eeg_format.id'))
    eeg_paradigm_id = Column(Integer, ForeignKey('eeg_paradigm.id'))
    
    eeg_format = relationship("EegFormat")
    eeg_paradigm = relationship("EegParadigm")

class EegFormat(Base):
    __tablename__ = 'eeg_format'
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String, unique=True)
    description = Column(Text)

class EegParadigm(Base):
    __tablename__ = 'eeg_paradigm'
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String, unique=True )
    description = Column(Text)

class EegAnalyses(Base):
    __tablename__ = 'eeg_analysis'   
    id = Column(Integer, primary_key=True)    
    name = Column(String)
    description = Column(Text)
    category = Column(String)
    valid_formats = Column(String)
    valid_paradigms = Column(String)
    parameters = Column(String)  # JSON string to store analysis parameters

def create_tables(db_url, reset=False):
    # Create the database engine
    engine = create_engine(db_url, echo=False)

    if reset:
        # Drop the database if reset is True
        if database_exists(engine.url):
            drop_database(engine.url)
            print("Database sfportal dropped.")

    # Check if the database exists, and create it if it doesn't
    if not database_exists(engine.url):
        create_database(engine.url)
        print("Database sfportal created.")
    else:
        print("Database sfportal already exists.")

    # Create the tables
    try:
        Base.metadata.create_all(engine)
        print("Tables created successfully.")
    except Exception as e:
        print("Error occurred during table creation:", e)
        
def initialize_database():
    from rich.console import Console
    console = Console()

    config = portal.portal_utils.load_config()
    db_url = config["database"]["url"]
    initialize_db = config["database"]["initialize"]

    console.print("[bold]Initializing or resetting database with the following parameters:[/bold]")
    console.print(f"Database URL: [green]{db_url}[/green]")
    console.print(f"Reset flag: [green]{initialize_db}[/green]")

    create_tables(db_url=db_url, reset=initialize_db)

if __name__ == "__main__":
    initialize_database()
