from signalfloweeg.portal.db_connection import get_database
import uuid
import logging

async def clear_table_dataset():
    logging.debug("Attempting to clear dataset information from the database.")
    db = await get_database()
    result = await db.dataset_catalog.delete_many({})
    logging.info(f"Dataset information cleared successfully. Deleted {result.deleted_count} documents.")

async def clear_table(table_name):
    logging.debug(f"Attempting to drop and recreate {table_name} collection in the database.")
    db = await get_database()
    await db[table_name].drop()
    logging.info(f"{table_name} collection dropped successfully.")

async def delete_dataset_info(dataset_id):
    db = await get_database()
    result = await db.dataset_catalog.delete_one({"dataset_id": dataset_id})
    if result.deleted_count == 1:
        logging.info(f"Dataset with ID {dataset_id} deleted successfully.")
    else:
        logging.warning(f"No dataset found with ID {dataset_id}.")

async def get_info():
    db = await get_database()
    datasets = await db.dataset_catalog.find().to_list(None)
    return [
        {
            "id": str(dataset["_id"]),
            "name": dataset["dataset_name"],
            "description": dataset.get("description"),
            "eeg_format": dataset.get("eeg_format"),
            "eeg_paradigm": dataset.get("eeg_paradigm")
        }
        for dataset in datasets
    ]

async def add_dataset_catalog(dataset_catalog_entry):
    print(f"📊 Adding dataset: {dataset_catalog_entry}")
    db = await get_database()
    existing_dataset = await db.dataset_catalog.find_one({"dataset_id": dataset_catalog_entry["dataset_id"]})
    if not existing_dataset:
        result = await db.dataset_catalog.insert_one(dataset_catalog_entry)
        return {
            "id": str(result.inserted_id),
            "name": dataset_catalog_entry["dataset_name"],
            "description": dataset_catalog_entry.get("description")
        }
    else:
        return {
            "id": str(existing_dataset["_id"]),
            "name": existing_dataset["dataset_name"],
            "description": existing_dataset.get("description")
        }

async def update_dataset(dataset_catalog_entry):
    db = await get_database()
    result = await db.dataset_catalog.update_one(
        {"dataset_id": dataset_catalog_entry["dataset_id"]},
        {"$set": {
            "dataset_name": dataset_catalog_entry["dataset_name"],
            "description": dataset_catalog_entry.get("description")
        }}
    )
    if result.modified_count == 1:
        return await db.dataset_catalog.find_one({"dataset_id": dataset_catalog_entry["dataset_id"]})
    else:
        return {"error": "Dataset not found"}
