from sqlalchemy import Column, Integer, String, Text, Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class EEGFileCatalog(Base):
    __tablename__ = 'eeg_file_catalog'
    id = Column(Integer, primary_key=True)
    filename = Column(String)
    dataset_name = Column(String)
    dataset_id = Column(String)   
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

class AnalysisCatalog(Base):
    __tablename__ = 'analysis_catalog'
    upload_id = Column(String, primary_key=True)  # Override 'upload_id' as the primary key

class DatasetCatalog(Base):
    __tablename__ = 'dataset_catalog'
    id = Column(Integer, primary_key=True)
    dataset_name = Column(String)
    dataset_id = Column(String, unique=True)
    description = Column(Text)
    eeg_format = Column(Integer)
    is_event_related = Column(Integer)

class EegFormat(Base):
    __tablename__ = 'eeg_format'
    id = Column(Integer, autoincrement=True, unique=True)
    name = Column(String, unique=True, primary_key=True)
    description = Column(Text)

class EegParadigm(Base):
    __tablename__ = 'eeg_paradigm'
    id = Column(Integer, autoincrement=True, unique=True)
    name = Column(String, unique=True, primary_key=True )
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
