from signalfloweeg.portal.db_connection import get_database

async def get_eeg_formats():
    db = await get_database()
    eeg_formats = await db.eeg_formats.find().to_list(length=None)
    return [
        {
            "id": str(eeg_format["_id"]),
            "name": eeg_format["name"],
            "description": eeg_format.get("description")
        }
        for eeg_format in eeg_formats
    ]

async def get_eeg_paradigms():
    db = await get_database()
    eeg_paradigms = await db.eeg_paradigms.find().to_list(length=None)
    return [
        {
            "id": str(eeg_paradigm["_id"]),
            "name": eeg_paradigm["name"],
            "description": eeg_paradigm.get("description")
        }
        for eeg_paradigm in eeg_paradigms
    ]

async def get_emails():
    db = await get_database()
    users = await db.users.find().to_list(length=None)
    return [
        {
            "id": str(user["_id"]),
            "name": user.get("email")
        }
        for user in users
    ]

async def get_upload_catalog():
    db = await get_database()
    file_catalog = await db.upload_catalog.find().to_list(length=None)
    return [
        {
            "upload_id": upload_record["upload_id"],
            "fdt_upload_id": upload_record.get("fdt_upload_id"),
            "original_name": upload_record["original_name"],
            "eeg_format": upload_record.get("eeg_format"),
            "is_set_file": upload_record.get("is_set_file"),
            "has_fdt_file": upload_record.get("has_fdt_file"),
            "fdt_filename": upload_record.get("fdt_filename"),
            "dataset_id": upload_record.get("dataset_id"),
            "dataset_name": upload_record.get("dataset_name"),
            "dataset_description": upload_record.get("dataset_description"),
            "eeg_paradigm": upload_record.get("eeg_paradigm"),
            "status": upload_record.get("status"),
            "date_added": upload_record.get("date_added"),
            "hash": upload_record.get("hash"),
            "size": upload_record.get("size"),
            "remove_upload": upload_record.get("remove_upload"),
            "upload_email": upload_record.get("upload_email")
        }
        for upload_record in file_catalog
    ]

async def get_import_catalog():
    db = await get_database()
    import_catalog = await db.import_catalog.find().to_list(length=None)
    return [
        {
            "upload_id": import_record["upload_id"],
            "original_name": import_record["original_name"],
            "is_set_file": import_record.get("is_set_file"),
            "has_fdt_file": import_record.get("has_fdt_file"),
            "fdt_filename": import_record.get("fdt_filename"),
            "fdt_upload_id": import_record.get("fdt_upload_id"),
            "dataset_id": import_record.get("dataset_id"),
            "dataset_name": import_record.get("dataset_name"),
            "dataset_description": import_record.get("dataset_description"),
            "eeg_format": import_record.get("eeg_format"),
            "eeg_paradigm": import_record.get("eeg_paradigm"),
            "status": import_record.get("status"),
            "date_added": import_record.get("date_added"),
            "remove_import": import_record.get("remove_import"),
            "hash": import_record.get("hash"),
            "sample_rate": import_record.get("sample_rate"),
            "n_channels": import_record.get("n_channels"),
            "n_epochs": import_record.get("n_epochs"),
            "total_samples": import_record.get("total_samples"),
            "mne_load_error": import_record.get("mne_load_error"),
            "upload_email": import_record.get("upload_email")
        }
        for import_record in import_catalog
    ]

async def get_dataset_catalog():
    db = await get_database()
    dataset_catalog = await db.dataset_catalog.find().to_list(length=None)
    return [
        {
            "dataset_name": dataset["dataset_name"],
            "dataset_id": dataset["dataset_id"],
            "description": dataset.get("description")
        }
        for dataset in dataset_catalog
    ]

async def get_dataset_stats():
    db = await get_database()
    dataset_catalog = await db.dataset_catalog.find().to_list(length=None)
    
    # Count number of import_catalog records associated with each dataset_id
    import_counts = await db.import_catalog.aggregate([
        {"$group": {"_id": "$dataset_id", "file_count": {"$sum": 1}}}
    ]).to_list(length=None)
    
    # Convert list of dicts into a dict for quick lookup
    count_dict = {item["_id"]: item["file_count"] for item in import_counts}
    
    return [
        {
            "dataset_name": dataset["dataset_name"],
            "dataset_id": dataset["dataset_id"],
            "description": dataset.get("description"),
            "file_count": count_dict.get(dataset["dataset_id"], 0)
        }
        for dataset in dataset_catalog
    ]

async def add_dataset(dataset_entry):
    db = await get_database()
    result = await db.dataset_catalog.insert_one(dataset_entry)
    return str(result.inserted_id)

async def update_dataset(dataset_entry):
    db = await get_database()
    result = await db.dataset_catalog.update_one(
        {"dataset_id": dataset_entry["dataset_id"]},
        {"$set": dataset_entry}
    )
    return result.modified_count > 0

async def merge_datasets(dataset_id1, dataset_id2):
    db = await get_database()
    
    # Get the datasets
    dataset1 = await db.dataset_catalog.find_one({"dataset_id": dataset_id1})
    dataset2 = await db.dataset_catalog.find_one({"dataset_id": dataset_id2})
    
    if not dataset1 or not dataset2:
        return False, "One or both datasets not found"
    
    # Merge dataset information
    merged_dataset = {
        "dataset_id": dataset_id1,
        "dataset_name": f"{dataset1['dataset_name']} + {dataset2['dataset_name']}",
        "description": f"{dataset1.get('description', '')} | {dataset2.get('description', '')}"
    }
    
    # Update the first dataset with merged information
    await db.dataset_catalog.update_one(
        {"dataset_id": dataset_id1},
        {"$set": merged_dataset}
    )
    
    # Update all records in import_catalog and upload_catalog
    for collection in [db.import_catalog, db.upload_catalog]:
        await collection.update_many(
            {"dataset_id": dataset_id2},
            {"$set": {"dataset_id": dataset_id1}}
        )
    
    # Delete the second dataset
    await db.dataset_catalog.delete_one({"dataset_id": dataset_id2})
    
    return True, "Datasets merged successfully"
