from pymongo import AsyncMongoClient
import os
from dotenv import load_dotenv
import logging
import certifi

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

mongo_uri = os.getenv("MONGO_URI")
if not mongo_uri:
    logger.error("❌ MONGO_URI non défini dans les variables d'environnement.")

client = AsyncMongoClient(
    mongo_uri,
    tls=True,
    tlsCAFile=certifi.where()
)

db = client["my_discord_bot"]
users_collection = db["users"]

async def check_mongodb_connection():
    try:
        await db.command("ping")
        logger.info("✅ Connexion MongoDB réussie (PyMongo Async) !")
    except Exception as e:
        logger.error(f"❌ Connexion MongoDB échouée : {e}")
