import logging
from rich.console import Console
from rich.table import Table
from signalfloweeg.portal.db_connection import get_database


async def generate_database_summary():
    """
    Generates a summary of the database collections and records.

    Returns:
        dict: A dictionary containing the collection names and record counts.
    """
    db = await get_database()
    console = Console()
    table = Table(title="Database Summary (DB Utilities)")
    table.add_column("Collection", style="cyan", no_wrap=True)
    table.add_column("Records", style="green", justify="right")

    json_summary = {}

    collections = await db.list_collection_names()
    for collection_name in collections:
        record_count = await db[collection_name].count_documents({})
        table.add_row(collection_name, str(record_count))
        json_summary[collection_name] = record_count

    console.print(table)
    return json_summary

async def drop_all_collections():
    success = False
    try:
        db = await get_database()
        collections = await db.list_collection_names()
        for collection in collections:
            await db[collection].drop()
        logging.info("All collections dropped successfully.")
        success = True
    except Exception as e:
        logging.error(f"Failed to drop all collections: {e}")
    finally:
        return {"success": success, "message": "All collections dropped successfully." if success else "Failed to drop all collections."}

async def drop_collection(collection_name):
    success = False
    try:
        logging.warning(f"Initiating drop_collection function for {collection_name}.")
        await generate_database_summary()
        db = await get_database()
        await db[collection_name].drop()
        logging.info(f"Collection {collection_name} dropped successfully.")
        success = True
    except Exception as e:
        logging.error(f"Failed to drop collection {collection_name}: {e}")
    finally:
        return {"success": success, "message": f"Collection {collection_name} dropped successfully." if success else f"Failed to drop collection {collection_name}."}
