from signalfloweeg.portal.db_connection import get_session
from signalfloweeg.portal.models import DatasetCatalog, UploadCatalog
from signalfloweeg.portal.portal_utils import (
    create_file_hash,
    add_status_code,
    load_config,
)
# from signalfloweeg.portal.dataset_catalog import add_dataset_catalog

from sqlalchemy.exc import IntegrityError

import logging
import json
import os
import datetime
from shutil import move
from sqlalchemy import func
import glob

config = load_config()
UPLOAD_PATH = config["folder_paths"]["uploads"]
INFO_PATH = config["folder_paths"]["info_archive"]
IMPORT_PATH = config["folder_paths"]["import"]


def process_new_uploads(upload_dir):
    def update_upload_catalog(info_files):
        ingest_info_files(info_files)
        align_fdt_files()
        delete_uploads_and_save_info_files()

    def find_info_files(upload_dir):
        info_files = glob.glob(os.path.join(upload_dir, "*.info"))
        logging.info(f"Detected {len(info_files)} .info files in {upload_dir}.")
        return info_files

    logging.info(f"Scanning upload directory: {upload_dir}")
    info_files = find_info_files(upload_dir)
    update_upload_catalog(info_files)
    logging.info("Upload and import catalogs updated.")


def ingest_info_files(info_files):
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

    for info_file in info_files:
        upload_catalog_entry, dataset_catalog_entry = extract_metadata(info_file)
        dataset_result = add_dataset_catalog(dataset_catalog_entry)
        upload_result = add_upload_catalog(upload_catalog_entry)
        print(f"Added dataset with ID: {dataset_result['dataset_id']}")
        print(f"Added upload with ID: {upload_result['upload_id']}")
def add_dataset_catalog(dataset_catalog_entry):
    print(f"📊 Adding dataset: {dataset_catalog_entry}")
    with get_session() as session:
        dataset = DatasetCatalog(**dataset_catalog_entry)
        try:
            session.merge(dataset)
            session.commit()
            logging.info(f"Dataset added to database with ID: {dataset_catalog_entry['dataset_id']}")
        except IntegrityError as e:
            session.rollback()  # Rollback the session to avoid PendingRollbackError in future transactions
            logging.warning(
                f"Warning: Duplicate dataset_id detected for dataset: {dataset_catalog_entry['dataset_id']}"
            )
            print("Error:", str(e))
        except Exception as e:
            session.rollback()  # Rollback the session to avoid PendingRollbackError in future transactions
            raise e
    return dataset_catalog_entry

def add_upload_catalog(upload_catalog_entry):
    print(f"📁 Adding upload_catalog: {upload_catalog_entry}")
    with get_session() as session:
        eeg_file = UploadCatalog(**upload_catalog_entry)
        try:
            session.merge(eeg_file)
            session.commit()
            logging.info(f"Metadata added to database for file: {upload_catalog_entry['original_name']}")
        except IntegrityError as e:
            session.rollback()  # Rollback the session to avoid PendingRollbackError in future transactions
            logging.warning(
                f"Warning: Duplicate upload_id detected for file: {upload_catalog_entry['original_name']}"
            )
            print("Error:", str(e))
        except Exception as e:
            session.rollback()  # Rollback the session to avoid PendingRollbackError in future transactions
            raise e
        finally:
            session.close()  # Ensure the session is closed after the operation
    return upload_catalog_entry


def align_fdt_files(folder_path=UPLOAD_PATH):
    with get_session() as session:
        for row in session.query(UploadCatalog).all():
            if row.original_name.endswith(".set"):
                row.is_set_file = True
                fdt_filename = row.original_name.replace(".set", ".fdt")
                fdt_file = (
                    session.query(UploadCatalog)
                    .filter(
                        func.lower(UploadCatalog.original_name)
                        == func.lower(fdt_filename)
                    )
                    .first()
                )
                if fdt_file:
                    row.has_fdt_file = True
                    row.fdt_filename = fdt_filename
                    row.fdt_upload_id = fdt_file.upload_id
                    print(fdt_file.upload_id)
                else:
                    row.has_fdt_file = False
                    row.fdt_filename = fdt_filename
                    row.fdt_upload_id = None
            session.merge(row)
        session.commit()
        session.close()


def delete_uploads_and_save_info_files():
    with get_session() as session:
        for row in session.query(UploadCatalog).all():
            if row.remove_upload:
                os.remove(os.path.join(UPLOAD_PATH, row.original_name))
                move(
                    os.path.join(UPLOAD_PATH, row.upload_id + ".info"),
                    os.path.join(INFO_PATH, row.upload_id + ".info"),
                )
                session.delete(row)
                session.commit()
        session.close()


def get_upload_and_fdt_upload_id(upload_id):
    # This function retrieves the upload and corresponding FDT file paths and IDs for a given upload_id.
    # It is used in the import_catalog.py module to manage file paths during the import process,
    # ensuring that both the SET and FDT files are correctly handled and their paths are updated in the ImportCatalog.
    with get_session() as session:
        file_record = (
            session.query(UploadCatalog)
            .filter(UploadCatalog.upload_id == upload_id)
            .first()
        )
        # get upload paths
        set_upload_path = os.path.join(UPLOAD_PATH, upload_id)
        fdt_upload_path = (
            os.path.join(UPLOAD_PATH, file_record.fdt_upload_id)
            if file_record.fdt_upload_id
            else None
        )
        # get destination paths
        set_import_path = os.path.join(IMPORT_PATH, file_record.original_name)
        fdt_import_path = (
            os.path.join(IMPORT_PATH, file_record.fdt_filename)
            if file_record.fdt_upload_id
            else None
        )
        # create results dictionary
        results = {
            "upload_id": upload_id,
            "fdt_upload_id": file_record.fdt_upload_id,
            "set_upload_path": set_upload_path,
            "fdt_upload_path": fdt_upload_path,
            "set_import_path": set_import_path,
            "fdt_import_path": fdt_import_path,
        }
        session.commit()
        session.close()

    return results
