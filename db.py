from pymongo import MongoClient
import os
from dotenv import load_dotenv
import logging
import certifi

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Chargement des variables d'environnement
load_dotenv()

# Récupération de l'URI MongoDB
mongo_uri = os.getenv("MONGO_URI")

# Connexion sécurisée à MongoDB avec certificat
client = MongoClient(mongo_uri, tls=True, tlsCAFile=certifi.where())

# Accès à la base de données et à la collection
db = client["my_discord_bot"]
users_collection = db["users"]

# Fonction de test de connexion (à appeler au démarrage si tu veux)
def test_connection():
    try:
        client.admin.command("ping")
        logger.info("✅ Connexion MongoDB réussie !")
    except Exception as e:
        logger.error("❌ Connexion MongoDB échouée : %s", e)
