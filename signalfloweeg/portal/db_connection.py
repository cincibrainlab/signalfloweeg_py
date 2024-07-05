from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
from rich.console import Console

MONGO_URL = "mongodb://localhost:3002"
DATABASE_NAME = "sfportal"

client = AsyncIOMotorClient(MONGO_URL, server_api=ServerApi('1'))
db = client[DATABASE_NAME]
console = Console()

async def get_database():
    return db

async def get_database_url():
    return MONGO_URL

async def is_database_connected():
    try:
        db = await get_database()
        await db.command('ping')
        return True
    except Exception:
        console.print("❌ Failed to connect to the database")
        return False

async def delete_database():
    await client.drop_database(DATABASE_NAME)

