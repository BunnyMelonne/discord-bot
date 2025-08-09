import motor.motor_asyncio
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

client = motor.motor_asyncio.AsyncIOMotorClient(mongo_uri, tls=True, tlsCAFile=certifi.where())
db = client["my_discord_bot"]
users_collection = db["users"]

async def test_connection():
    try:
        await client.admin.command("ping")
        logger.info("✅ Connexion MongoDB réussie !")
    except Exception as e:
        logger.error(f"❌ Connexion MongoDB échouée : {e}")