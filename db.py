from pymongo import MongoClient
import os
from dotenv import load_dotenv
import logging
import certifi  # <-- ajoute ça

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

mongo_uri = os.getenv("MONGO_URI")

# Ajout du paramètre tlsCAFile pour forcer le certificat racine
client = MongoClient(mongo_uri, tlsCAFile=certifi.where())

db = client["my_discord_bot"]
users_collection = db["users"]

def test_connection():
    try:
        client.admin.command("ping")
        logger.info("✅ Connexion MongoDB réussie !")
    except Exception as e:
        logger.error("❌ Connexion MongoDB échouée : %s", e)
