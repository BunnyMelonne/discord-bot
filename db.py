from pymongo import MongoClient
import os
from dotenv import load_dotenv
import logging

# Configure le logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Charger les variables d'environnement du fichier .env
load_dotenv()

# Lire l'URI depuis les variables d'environnement
mongo_uri = os.getenv("MONGO_URI")

# Initialiser le client MongoDB
client = MongoClient(mongo_uri)

# Choisir la base de données et une collection
db = client["my_discord_bot"]  # Tu peux changer le nom
users_collection = db["users"]  # Une collection pour stocker les utilisateurs

# Fonction utilitaire pour tester la connexion
def test_connection():
    try:
        client.admin.command("ping")
        logger.info("✅ Connexion MongoDB réussie !")
    except Exception as e:
        logger.error("❌ Connexion MongoDB échouée : %s", e)
