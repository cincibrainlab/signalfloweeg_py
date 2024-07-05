from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from bson import ObjectId
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from rich.console import Console
from rich.table import Table

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        json_schema = handler(core_schema)
        json_schema.update(type="string")
        return json_schema

class MongoBaseModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

    model_config = {
        "populate_by_name": True,
        "json_encoders": {ObjectId: str}
    }

class Startup(MongoBaseModel):
    sf_config_path: Optional[str] = None

class Users(MongoBaseModel):
    user_id: str
    username: Optional[str] = None
    email: Optional[str] = None

class ConfigDB(MongoBaseModel):
    database: Optional[str] = None
    frontend: Optional[str] = None
    api: Optional[str] = None
    users: Optional[str] = None
    folder_paths: Optional[str] = None
    eeg_formats: Optional[str] = None
    eeg_paradigms: Optional[str] = None
    eeg_analyses: Optional[str] = None

class DatasetCatalog(MongoBaseModel):
    dataset_name: str
    dataset_id: str
    description: Optional[str] = None

class EegFormat(MongoBaseModel):
    name: str
    description: Optional[str] = None

class EegParadigm(MongoBaseModel):
    name: str
    description: Optional[str] = None

class CatalogBase(MongoBaseModel):
    status: Optional[str] = None
    upload_id: str
    date_added: str
    original_name: str
    eeg_format: Optional[str] = None
    eeg_paradigm: Optional[str] = None
    is_set_file: bool
    has_fdt_file: bool
    fdt_filename: Optional[str] = None
    fdt_upload_id: Optional[str] = None
    upload_email: Optional[str] = None
    hash: str
    dataset_id: str

class UploadCatalog(CatalogBase):
    size: Optional[str] = None
    remove_upload: bool = False

class ImportCatalog(CatalogBase):
    remove_import: bool = False
    sample_rate: Optional[int] = None
    n_channels: Optional[int] = None
    n_epochs: Optional[int] = None
    total_samples: Optional[int] = None
    mne_load_error: bool = False

class AnalysisConfig(MongoBaseModel):
    function_name: str
    description: Optional[str] = None
    eeg_formats: str
    eeg_paradigms: str
    parameters: str
    version: str
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class AnalysisJobList(MongoBaseModel):
    job_id: str
    upload_id: str
    eeg_format_name: str
    eeg_paradigm_name: str
    eeg_analysis_name: str
    status: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    parameters: Optional[str] = None
    result: Optional[str] = None

class EegAnalyses(MongoBaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    valid_formats: Optional[str] = None
    valid_paradigms: Optional[str] = None
    parameters: Optional[str] = None

def get_db_url():
    # Implement this function to return the MongoDB connection string
    # For example:
    return "mongodb://localhost:3002"

def initialize_database(reset=False):
    db_url = get_db_url()
    db_name = "sfportal"  # Set your desired database name
    console = Console()

    console.print(
        "[bold]Initializing or resetting database with the following parameters:[/bold]"
    )
    console.print(f"Database URL: [green]{db_url}[/green]")
    console.print(f"Reset flag: [green]{reset}[/green]")

    client = MongoClient(db_url)

    try:
        # Check if the connection is successful
        client.server_info()
    except ServerSelectionTimeoutError:
        console.print("[bold red]Error: Unable to connect to the MongoDB server.[/bold red]")
        return

    db = client[db_name]

    if reset:
        client.drop_database(db_name)
        console.print(f"Database '{db_name}' dropped successfully.")

    # Create collections based on your models
    collections = [
        "startup", "users", "config", "dataset_catalog", "eeg_formats",
        "eeg_paradigms", "upload_catalog", "import_catalog", "analysis_config",
        "analysis_joblist", "eeg_analyses"
    ]

    for collection_name in collections:
        if collection_name not in db.list_collection_names():
            db.create_collection(collection_name)

    # Verify collections
    table_verification = Table(title="Collection Verification")
    table_verification.add_column("Collection Name", style="cyan")
    table_verification.add_column("Status", style="green")

    for collection_name in collections:
        if collection_name in db.list_collection_names():
            table_verification.add_row(collection_name, "Verified")
        else:
            table_verification.add_row(collection_name, "Not Found")

    console.print(table_verification)

    console.print(f"Database '{db_name}' initialized successfully.")