
from signalfloweeg.portal.db_connection import get_session
from signalfloweeg.portal.models import DatasetCatalog, UploadCatalog
from signalfloweeg.portal.portal_utils import create_file_hash, add_status_code, load_config
from signalfloweeg.portal.dataset_catalog import add_dataset

from sqlalchemy.exc import IntegrityError

import logging
import json
import os
import datetime
from shutil import move
from sqlalchemy import func
import glob

config = load_config()
UPLOAD_PATH = config['folder_paths']['uploads']
INFO_PATH = config['folder_paths']['info_archive']
IMPORT_PATH = config['folder_paths']['import']

def find_info_files(upload_dir):
    info_files = glob.glob(os.path.join(upload_dir, "*.info"))
    logging.info(f"Detected {len(info_files)} .info files in {upload_dir}.")
    return info_files

def process_new_uploads(upload_dir):
    logging.info(f"Scanning upload directory: {upload_dir}")
    info_files = find_info_files(upload_dir)
    update_upload_catalog(info_files)
    logging.info("Upload and import catalogs updated.")

def update_upload_catalog(info_files):
    ingest_info_files(info_files)
    align_fdt_files()
    delete_uploads_and_save_info_files()

def extract_metadata(info_file, folder_path=UPLOAD_PATH):
    with open(info_file, 'r') as f:
        file_metadata = json.load(f)
    row = {
        'status': add_status_code(200),
        'dataset_name': file_metadata['MetaData'].get('datasetName', 'NA'),
        'dataset_id': file_metadata['MetaData'].get('datasetId', 'NA'),
        'remove_upload': False,
        'upload_id': file_metadata.get('ID', 'NA'),
        'date_added': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'size': file_metadata.get('Size', 'NA'),
        'original_name': file_metadata['MetaData'].get('filename', 'NA'),
        'hash': create_file_hash(os.path.join(folder_path, os.path.basename(file_metadata['Storage'].get('Path', '')))),
        'eeg_format': file_metadata['MetaData'].get('eegFormat', 'NA'),
        'eeg_paradigm': file_metadata['MetaData'].get('eegParadigm', 'NA'),
        'upload_email': file_metadata['MetaData'].get('emailSelection', 'NA'),
    }
    return row

def align_fdt_files(folder_path=UPLOAD_PATH):
    with get_session() as session:
        for row in session.query(UploadCatalog).all():
            if row.original_name.endswith('.set'):
                row.is_set_file = True
                fdt_filename = row.original_name.replace('.set', '.fdt')
                fdt_file = session.query(UploadCatalog).filter(func.lower(UploadCatalog.original_name) == func.lower(fdt_filename)).first()
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


def ingest_info_files(info_files):
    with get_session() as session:
        # Function to add metadata to the database
        for info_file in info_files:
            row = extract_metadata(info_file)

            dataset_entry = DatasetCatalog(
                dataset_id=row['dataset_id'],
                dataset_name=row['dataset_name'],
                description=''
                )
            
            add_dataset(dataset_entry)
            
            eeg_file = UploadCatalog(**row)
            try:
                session.merge(eeg_file)
                session.commit()
            except IntegrityError as e:
                logging.warning(f"Warning: Duplicate upload_id detected for file: {eeg_file.original_name}")
                print("Error:", str(e))
                    
            logging.info(f"Metadata added to database for file: {row['original_name']}")
        session.close()

def get_upload_and_fdt_upload_id(upload_id):
    with get_session() as session:
        file_record = session.query(UploadCatalog).filter(UploadCatalog.upload_id == upload_id).first()
        # get upload paths
        set_upload_path = os.path.join(UPLOAD_PATH, upload_id)
        fdt_upload_path = os.path.join(UPLOAD_PATH, file_record.fdt_upload_id) if file_record.fdt_upload_id else None
        # get destination paths
        set_import_path = os.path.join(IMPORT_PATH, file_record.original_name)
        fdt_import_path = os.path.join(IMPORT_PATH, file_record.fdt_filename) if file_record.fdt_upload_id else None
        # create results dictionary
        results = {
            'upload_id': upload_id,
            'fdt_upload_id': file_record.fdt_upload_id,
            'set_upload_path': set_upload_path,
            'fdt_upload_path': fdt_upload_path,
            'set_import_path': set_import_path,
            'fdt_import_path': fdt_import_path
        }
        session.commit()
        session.close()
    
    return results
    
def delete_uploads_and_save_info_files():
    with get_session() as session:
        for row in session.query(UploadCatalog).all():
            if row.remove_upload:
                os.remove(os.path.join(UPLOAD_PATH, row.original_name))
                move(os.path.join(UPLOAD_PATH, row.upload_id + '.info'), os.path.join(INFO_PATH, row.upload_id + '.info'))
                session.delete(row)
                session.commit()
        session.close()