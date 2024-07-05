from signalfloweeg.portal.db_connection import get_database
from signalfloweeg.portal.portal_utils import (
    create_file_hash,
    add_status_code,
    load_config,
)
from sqlalchemy.exc import IntegrityError

import logging
import json
import os
import datetime
from shutil import move
import glob

config = load_config()
UPLOAD_PATH = config["folder_paths"]["uploads"]
INFO_PATH = config["folder_paths"]["info_archive"]
IMPORT_PATH = config["folder_paths"]["import"]

async def process_new_uploads(upload_dir):
    async def update_upload_catalog(info_files):
        await ingest_info_files(info_files)
        await align_fdt_files()
        await delete_uploads_and_save_info_files()

    def find_info_files(upload_dir):
        info_files = glob.glob(os.path.join(upload_dir, "*.info"))
        logging.info(f"Detected {len(info_files)} .info files in {upload_dir}.")
        return info_files

    logging.info(f"Scanning upload directory: {upload_dir}")
    info_files = find_info_files(upload_dir)
    await update_upload_catalog(info_files)
    logging.info("Upload and import catalogs updated.")

async def ingest_info_files(info_files):
    def extract_metadata(info_file, folder_path=UPLOAD_PATH):
        with open(info_file, "r") as f:
            file_metadata = json.load(f)
            upload_catalog_entry = {
                "status": add_status_code(200),
                "dataset_id": file_metadata["MetaData"].get("datasetId", "NA"),
                "remove_upload": False,
                "upload_id": file_metadata.get("ID", "NA"),
                "date_added": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "size": file_metadata.get("Size", "NA"),
                "original_name": file_metadata["MetaData"].get("filename", "NA"),
                "hash": create_file_hash(
                    os.path.join(
                        folder_path,
                        os.path.basename(file_metadata["Storage"].get("Path", "")),
                    )
                ),
                "eeg_format": file_metadata["MetaData"].get("eegFormat", "NA"),
                "eeg_paradigm": file_metadata["MetaData"].get("eegParadigm", "NA"),
                "upload_email": file_metadata["MetaData"].get("emailSelection", "NA"),
            }
            dataset_catalog_entry = {
                "dataset_id": file_metadata["MetaData"].get("datasetId", "NA"),
                "dataset_name": file_metadata["MetaData"].get("datasetName", "NA"),
                "description": "",
            }
        return upload_catalog_entry, dataset_catalog_entry
    db = await get_database()
    for info_file in info_files:
        upload_catalog_entry, dataset_catalog_entry = extract_metadata(info_file)
        dataset_result = await add_dataset_catalog(dataset_catalog_entry)
        upload_result = await add_upload_catalog(upload_catalog_entry)
        print(f"Added dataset with ID: {dataset_result['dataset_id']}")
        print(f"Added upload with ID: {upload_result['upload_id']}")

async def add_dataset_catalog(dataset_catalog_entry):
    print(f"📊 Adding dataset: {dataset_catalog_entry}")
    db = await get_database()
    try:
        result = await db.dataset_catalog.update_one(
            {"dataset_id": dataset_catalog_entry['dataset_id']},
            {"$set": dataset_catalog_entry},
            upsert=True
        )
        logging.info(f"Dataset added to database with ID: {dataset_catalog_entry['dataset_id']}")
    except Exception as e:
        logging.error(f"Error adding dataset: {str(e)}")
        raise e
    return dataset_catalog_entry

async def add_upload_catalog(upload_catalog_entry):
    print(f"📁 Adding upload_catalog: {upload_catalog_entry}")
    db = await get_database()
    try:
        result = await db.upload_catalog.update_one(
            {"upload_id": upload_catalog_entry['upload_id']},
            {"$set": upload_catalog_entry},
            upsert=True
        )
        logging.info(f"Metadata added to database for file: {upload_catalog_entry['original_name']}")
    except Exception as e:
        logging.error(f"Error adding upload: {str(e)}")
        raise e
    return upload_catalog_entry

async def align_fdt_files(folder_path=UPLOAD_PATH):
    db = await get_database()
    async for row in db.upload_catalog.find():
        if row['original_name'].endswith(".set"):
            update_data = {"is_set_file": True}
            fdt_filename = row['original_name'].replace(".set", ".fdt")
            fdt_file = await db.upload_catalog.find_one({"original_name": {"$regex": f"^{fdt_filename}$", "$options": "i"}})
            if fdt_file:
                update_data.update({
                    "has_fdt_file": True,
                    "fdt_filename": fdt_filename,
                    "fdt_upload_id": fdt_file['upload_id']
                })
            else:
                update_data.update({
                    "has_fdt_file": False,
                    "fdt_filename": fdt_filename,
                    "fdt_upload_id": None
                })
            await db.upload_catalog.update_one({"_id": row['_id']}, {"$set": update_data})

async def delete_uploads_and_save_info_files():
    db = await get_database()
    async for row in db.upload_catalog.find({"remove_upload": True}):
        os.remove(os.path.join(UPLOAD_PATH, row['original_name']))
        move(
            os.path.join(UPLOAD_PATH, row['upload_id'] + ".info"),
            os.path.join(INFO_PATH, row['upload_id'] + ".info"),
        )
        await db.upload_catalog.delete_one({"_id": row['_id']})

async def get_upload_and_fdt_upload_id(upload_id):
    db = await get_database()
    file_record = await db.upload_catalog.find_one({"upload_id": upload_id})
    if not file_record:
        raise ValueError(f"Upload ID {upload_id} not found in the database.")
    set_upload_path = os.path.join(UPLOAD_PATH, upload_id)
    fdt_upload_path = os.path.join(UPLOAD_PATH, file_record['fdt_upload_id']) if file_record.get('fdt_upload_id') else None
    set_import_path = os.path.join(IMPORT_PATH, file_record['original_name'])
    fdt_import_path = os.path.join(IMPORT_PATH, file_record['fdt_filename']) if file_record.get('fdt_filename') else None
    return {
        "upload_id": upload_id,
        "fdt_upload_id": file_record['fdt_upload_id'],
        "set_upload_path": set_upload_path,
        "fdt_upload_path": fdt_upload_path,
        "set_import_path": set_import_path,
        "fdt_import_path": fdt_import_path
    }

