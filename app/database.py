import logging
import os

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("uvicorn")


class Database:
    client: AsyncIOMotorClient | None = None
    db: AsyncIOMotorDatabase | None = None


db_connection = Database()


async def connect_to_mongo():
    uri = os.getenv("MONGO_DB_URL")

    db_connection.client = AsyncIOMotorClient(uri)

    db_connection.db = db_connection.client[os.getenv("DB_NAME", "feedback_db_default")]

    try:
        await db_connection.client.admin.command("ping")
        logger.info("Connexion etablie")
    except Exception as e:
        logger.info(f"Erreur de connection: {e}")


async def close_mongo_connection():
    if db_connection.client:
        db_connection.client.close()
        logger.info("Fermeture")


async def create_indexes():
    collection = db_connection.db.get_collection("feedbacks")

    await collection.create_index([("created_at", -1)])

    await collection.create_index(
        [
            ("content", "text"),
            ("keywords", "text"),
            ("company_name", "text"),
            ("username", "text"),
        ],
        default_language="french",
        weights={"content": 10, "keywords": 8, "company_name": 3, "username": 2},
    )

    logger.info("Index créés : created_at + texte")
