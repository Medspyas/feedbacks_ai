import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("uvicorn")

class Database:
    client: AsyncIOMotorClient = None
    db = None

db_connection = Database()

async def connect_to_mongo():
    uri = os.getenv("MONGO_DB_URL")

    db_connection.client = AsyncIOMotorClient(uri)

    db_connection.db = db_connection.client[os.getenv("DB_NAME", "feedback_db_default")] 

    try:
        await db_connection.client.admin.command('ping')
        logger.info("Connexion etablie")
    except Exception as e:
        logger.info(f"Erreur de connection: {e}")

async def close_mongo_connection():
    if db_connection.client:
        db_connection.client.close()
        logger.info("Fermeture")