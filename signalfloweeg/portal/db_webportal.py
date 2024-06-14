from signalfloweeg.portal.db_connection import get_session
from signalfloweeg.portal.models import (
    EegFormat,
    EegParadigm,
    Users,
    UploadCatalog,
    ImportCatalog,
    DatasetCatalog
    )
from sqlalchemy.sql import func

def get_eeg_formats():
    with get_session() as session:
        eeg_formats = session.query(EegFormat).all()
        return [
            {
                "id": eeg_format.id,
                "name": eeg_format.name,
                "description": eeg_format.description
            }
            for eeg_format in eeg_formats
        ]


def get_eeg_paradigms():
    with get_session() as session:
        eeg_paradigms = session.query(EegParadigm).all()
        return [
            {
                "id": eeg_paradigm.id,
                "name": eeg_paradigm.name,
                "description": eeg_paradigm.description
            }
            for eeg_paradigm in eeg_paradigms
        ]

def get_emails():
    with get_session() as session:
        users = session.query(Users).all()
        return [
            {
                "id": user.user_id,
                "name": user.email
            }
            for user in users
        ]

# Webforms: Files Tab
def get_upload_catalog():
    with get_session() as session:
        file_catalog = session.query(UploadCatalog).all()
        return [
            {
                "upload_id": upload_record.upload_id,
                "fdt_upload_id": upload_record.fdt_upload_id,
                "original_name": upload_record.original_name,
                "eeg_format": upload_record.eeg_format,
                "is_set_file": upload_record.is_set_file,
                "has_fdt_file": upload_record.has_fdt_file,
                "fdt_filename": upload_record.fdt_filename,
                "dataset_id": upload_record.dataset_id,
                "dataset_name": upload_record.dataset_name,
                "dataset_description": upload_record.dataset_description,
                "eeg_paradigm": upload_record.eeg_paradigm,
                "status": upload_record.status,
                "date_added": upload_record.date_added,
                "hash": upload_record.hash,
                "size": upload_record.size,
                "remove_upload": upload_record.remove_upload,
                "upload_email": upload_record.upload_email
            }
            for upload_record in file_catalog
        ]
def get_import_catalog():
    with get_session() as session:
        import_catalog = session.query(ImportCatalog).all()
        return [
            {
                "upload_id": import_record.upload_id,
                "original_name": import_record.original_name,
                "is_set_file": import_record.is_set_file,
                "has_fdt_file": import_record.has_fdt_file,
                "fdt_filename": import_record.fdt_filename,
                "fdt_upload_id": import_record.fdt_upload_id,  # Updated key to fdt_upload_id
                "dataset_id": import_record.dataset_id,
                "dataset_name": import_record.dataset_name,
                "dataset_description": import_record.dataset_description,
                "eeg_format": import_record.eeg_format,
                "eeg_paradigm": import_record.eeg_paradigm,
                "status": import_record.status,
                "date_added": import_record.date_added,
                "remove_import": import_record.remove_import,
                "hash": import_record.hash,
                "sample_rate": import_record.sample_rate,  # Added sample_rate
                "n_channels": import_record.n_channels,  # Added n_channels
                "n_epochs": import_record.n_epochs,  # Added n_epochs
                "total_samples": import_record.total_samples,  # Added total_samples
                "mne_load_error": import_record.mne_load_error,  # Added mne_load_error
                "upload_email": import_record.upload_email
            }
            for import_record in import_catalog
        ]

def get_dataset_catalog():
    with get_session() as session:
        dataset_catalog = session.query(DatasetCatalog).all()
        return [
            {
                "dataset_name": dataset.dataset_name,
                "dataset_id": dataset.dataset_id,
                "description": dataset.description
            }
            for dataset in dataset_catalog
        ]

def get_dataset_stats():
    with get_session() as session:
        # Query to get all datasets
        dataset_catalog = session.query(DatasetCatalog).all()
        # Query to count number of import_catalog records associated with each dataset_id
        import_counts = session.query(
            ImportCatalog.dataset_id, 
            func.count(ImportCatalog.dataset_id).label('file_count')
        ).group_by(ImportCatalog.dataset_id).all()
        # Convert list of tuples into a dictionary for quick lookup
        count_dict = {dataset_id: count for dataset_id, count in import_counts}
        
        return [
            {
                "dataset_name": dataset.dataset_name,
                "dataset_id": dataset.dataset_id,
                "description": dataset.description,
                "file_count": count_dict.get(dataset.dataset_id, 0)  # Default to 0 if no records found
            }
            for dataset in dataset_catalog
        ]

def merge_two_datasets(dataset_id1, dataset_id2):
    with get_session() as session:
        # Query to get all import_catalog records with dataset_id1
        records1 = session.query(ImportCatalog).filter(ImportCatalog.dataset_id == dataset_id1).all()
        # Query to get all import_catalog records with dataset_id2
        records2 = session.query(ImportCatalog).filter(ImportCatalog.dataset_id == dataset_id2).all()
        
        # Update all records with dataset_id2 to dataset_id1
        for record in records2:
            record.dataset_id = dataset_id1
        
        session.commit()
        return len(records2)

if __name__ == "__main__":
    print(get_eeg_formats())
    print(get_eeg_paradigms())
    print(get_emails())