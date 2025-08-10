import os
import logging
import discord
from discord.ext import commands
from dotenv import load_dotenv
from keep_alive import keep_alive
from db import check_mongodb_connection
from extensions import EXTENSIONS

# === Chargement variables d'environnement ===
load_dotenv()
TOKEN = os.getenv("TOKEN")

# === Configuration logs ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === Intents & Bot ===
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# === Événements ===
@bot.event
async def setup_hook():
    try:
        for ext in EXTENSIONS:
            await bot.load_extension(ext)
            logger.info(f"Extension chargée : {ext}")
        logger.info("✅ Toutes les extensions ont été chargées avec succès.")
    except Exception:
        logger.exception("❌ Erreur lors du chargement des extensions.")

@bot.event
async def on_ready():
    logger.info(f"🤖 Bot connecté en tant que {bot.user}")
    await check_mongodb_connection()

@bot.event
async def on_disconnect():
    logger.warning("⚠️ Bot déconnecté de Discord.")

@bot.event
async def on_resumed():
    logger.info("🔄 Session Discord reprise avec succès.")

# === Keep Alive (pour Render / Repl.it) ===
keep_alive()

# === Lancement du bot ===
if TOKEN:
    try:
        bot.run(TOKEN)
    except discord.LoginFailure:
        logger.error("❌ TOKEN invalide. Vérifie ton .env ou tes variables Render.")
else:
    logger.error("❌ TOKEN non trouvé. Vérifie ton .env ou tes variables Render.")
