from shutil import copy
import os
from signalfloweeg.portal.db_connection import get_database
from signalfloweeg.portal.models import UploadCatalog, ImportCatalog
from signalfloweeg.portal.portal_utils import add_status_code
from signalfloweeg.portal.upload_catalog import get_upload_and_fdt_upload_id
from signalfloweeg.portal.signal_utils import get_core_eeg_info

async def update_import_catalog():
    db = await get_database()
    upload_catalog = db.upload_catalog
    import_catalog = db.import_catalog

    set_files = await upload_catalog.find({"is_set_file": True}).to_list(None)
    for file in set_files:
        # Check if the record already exists in the ImportCatalog
        existing_record = await import_catalog.find_one({"upload_id": file["upload_id"]})
        if existing_record:
            print(f"\033[93mRecord already exists in ImportCatalog with ID: {existing_record['upload_id']}\033[0m")
        else:
            set_dest_path, fdt_dest_path = await copy_import_files(file["upload_id"])
            core_info = get_core_eeg_info(set_dest_path)
            print(f"Before ImportCatalog creation: eeg_format={file['eeg_format']}, eeg_paradigm={file['eeg_paradigm']}")
            import_record = {
                "original_name": file["original_name"],
                "dataset_id": file["dataset_id"],
                "eeg_format": file["eeg_format"],
                "eeg_paradigm": file["eeg_paradigm"],
                "upload_email": file["upload_email"],
                "date_added": file["date_added"],
                "upload_id": file["upload_id"],
                "remove_import": file["remove_upload"],
                "is_set_file": file["is_set_file"],
                "has_fdt_file": file["has_fdt_file"],
                "fdt_filename": file["fdt_filename"],
                "fdt_upload_id": file["fdt_upload_id"],
                "hash": file["hash"],
                "mne_load_error": core_info['mne_load_error'],
                "sample_rate": core_info['sample_rate'],
                "n_channels": core_info['n_channels'],
                "n_epochs": core_info['n_epochs'],
                "total_samples": core_info['total_samples'],
                "status": add_status_code(201)
            }
            await import_catalog.insert_one(import_record)
            print(f"\033[92mRecord added in ImportCatalog with ID: {import_record['upload_id']}\033[0m")
            await clean_import_files(file["upload_id"])

    print(f"Transferred {len(set_files)} SET files from UploadCatalog to ImportCatalog.")

async def clean_import_files(upload_id):
    import_file_paths = await get_upload_and_fdt_upload_id(upload_id)
    set_dest_path = import_file_paths['set_import_path']
    fdt_dest_path = import_file_paths['fdt_import_path']

    if os.path.exists(set_dest_path):
        os.remove(set_dest_path)
        print(f"Removed SET file {set_dest_path}")
    if fdt_dest_path and os.path.exists(fdt_dest_path):
        os.remove(fdt_dest_path)
        print(f"Removed FDT file {fdt_dest_path}")

async def update_core_eeg_info():
    db = await get_database()
    import_catalog = db.import_catalog
    async for record in import_catalog.find({"is_set_file": True}):
        set_dest_path, fdt_dest_path = await copy_import_files(record["upload_id"])
        core_eeg_info = get_core_eeg_info(set_dest_path)
        await import_catalog.update_one({"_id": record["_id"]}, {"$set": {"core_eeg_info": core_eeg_info}})

async def get_first_upload_id():
    db = await get_database()
    import_catalog = db.import_catalog
    first_import_record = await import_catalog.find_one()
    return first_import_record["upload_id"] if first_import_record else None

async def get_import_ids():
    db = await get_database()
    import_catalog = db.import_catalog
    import_records = await import_catalog.find({}, {"upload_id": 1}).to_list(None)
    
    from rich.console import Console
    from rich.table import Table
    
    console = Console()
    table = Table(title="Import Catalog Upload IDs")
    table.add_column("Upload ID", style="cyan", no_wrap=True)
    
    for record in import_records:
        table.add_row(record["upload_id"])
    
    console.print(table)
    
    return {"upload_ids": [record["upload_id"] for record in import_records]}

async def get_upload_id_by_record_number(record_number=None):
    db = await get_database()
    import_catalog = db.import_catalog
    if record_number is not None:
        try:
            record = await import_catalog.find().skip(record_number - 1).limit(1).next()
            if record:
                return record["upload_id"]
            else:
                print(f"No record found for record number: {record_number}")
                return None
        except Exception as e:
            print(f"Error retrieving upload_id for record number {record_number}: {e}")
            return None
    else:
        try:
            records = await import_catalog.find().to_list(None)
            if records:
                print("Available records:")
                for i, record in enumerate(records, 1):
                    print(f"Record Number: {i}, Upload ID: {record['upload_id']}")
            else:
                print("No records found.")
        except Exception as e:
            print(f"Error retrieving records: {e}")

async def generate_joblist():
    db = await get_database()
    import_catalog = db.import_catalog
    
    # Query the ImportCatalog to find eligible files
    eligible_files = await import_catalog.find({
        "status": add_status_code(201),
        "mne_load_error": False
    }).to_list(None)

    from rich.console import Console
    from rich.table import Table

    console = Console()
    table = Table(title="Eligible Files for Processing")
    table.add_column("Upload ID", style="cyan", no_wrap=True)
    table.add_column("Dataset Name", style="magenta", no_wrap=True)
    table.add_column("EEG Format", style="yellow", no_wrap=True)
    table.add_column("EEG Paradigm", style="blue", no_wrap=True)

    for file in eligible_files:
        table.add_row(file["upload_id"], file.get("dataset_name", "N/A"), file["eeg_format"], file["eeg_paradigm"])

    console.print(table)

async def copy_import_files(upload_id):
    # Copy the SET and FDT files to the import path
    import_file_paths = await get_upload_and_fdt_upload_id(upload_id)
    set_dest_path = import_file_paths['set_import_path']
    fdt_dest_path = import_file_paths['fdt_import_path']
    set_src_path = import_file_paths['set_upload_path']
    fdt_src_path = import_file_paths['fdt_upload_path']

    if set_src_path:
        copy(set_src_path, set_dest_path)
        print(f"Copied SET file {set_src_path} to {set_dest_path}")
    
    if fdt_src_path:
        copy(fdt_src_path, fdt_dest_path)
        print(f"Copied FDT file {fdt_src_path} to {fdt_dest_path}")
    return set_dest_path, fdt_dest_path