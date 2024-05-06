from signalfloweeg.portal.db_connection import get_session

from signalfloweeg.portal.models import (
    DatasetCatalog
)
import signalfloweeg.portal.models as models
import uuid

import logging

# Generic Function Names Suggestions:
# 1. clear_table() - Generic function to clear any specified table.
# 2. delete_info() - Generic function to delete information based on a specific condition.
# 3. get_info() - Generic function to retrieve information from any specified table.
# 4. add_info() - Generic function to add information to any specified table.
# 5. update_info() - Generic function to update information in any specified table.
# 6. find_by_id() - Generic function to find a record by its ID.
# 7. find_by_attribute() - Generic function to find records by a specific attribute.
# 8. list_all() - Generic function to list all records from any specified table.
# 9. count_records() - Generic function to count the number of records in any specified table.
# 10. exists() - Generic function to check if a record exists based on specific conditions.


def clear_table_dataset():
    logging.debug("Attempting to clear dataset information from the database.")
    with get_session() as session:
        session.query(DatasetCatalog).delete(synchronize_session=False)
        session.commit()
    logging.info("Dataset information cleared successfully.")

def clear_table(table_name):
    logging.debug(f"Attempting to drop and recreate {table_name} table in the database.")
    with get_session() as session:
        table_class = getattr(models, table_name)
        table_class.__table__.drop(session.bind)
        table_class.__table__.create(session.bind)
        session.commit()
    logging.info(f"{table_name} table dropped and recreated successfully.")

def delete_dataset_info(dataset_id):
    with get_session() as session:
        session.query(DatasetCatalog).filter(DatasetCatalog.dataset_id == dataset_id).delete()
        session.commit()

def get_info():
    with get_session() as session:
        datasets = session.query(DatasetCatalog).all()
        return [
            {
                "id": dataset.dataset_id,
                "name": dataset.dataset_name,
                "description": dataset.description,
                "eeg_format": dataset.eeg_format.name if dataset.eeg_format else None,
                "eeg_paradigm": dataset.eeg_paradigm.name if dataset.eeg_paradigm else None
            }
            for dataset in datasets
        ]

def add_dataset_catalog(dataset_catalog_entry: DatasetCatalog):
    print(f"📊 Adding dataset: {dataset_catalog_entry}")
    with get_session() as session:
        # Check if a dataset with the provided ID already exists
        existing_dataset = session.query(DatasetCatalog).filter_by(dataset_id=dataset_catalog_entry["dataset_id"]).first()
        if not existing_dataset:
            # Create a new dataset entry if it does not exist
            session.add(dataset_catalog_entry)
            session.commit()

        # Return the dataset details whether it was newly created or already existed
        return {
            "id": dataset_catalog_entry.dataset_id,
            "name": dataset_catalog_entry.dataset_name,
            "description": dataset_catalog_entry.description
        }

def update_dataset(dataset_catalog_entry: DatasetCatalog):
    with get_session() as session:
        # Fetch the existing dataset by ID
        existing_dataset = session.query(DatasetCatalog).filter_by(dataset_id=dataset_catalog_entry.dataset_id).first()
        if existing_dataset:
            # Update the existing dataset entry
            existing_dataset.dataset_name = dataset_catalog_entry.dataset_name
            existing_dataset.description = dataset_catalog_entry.description
            session.commit()
            return existing_dataset
        else:
            # If the dataset does not exist, return an error message
            return {"error": "Dataset not found"}


