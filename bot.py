import os
from discord import Object
import discord
from discord.ext import commands
from dotenv import load_dotenv
from keep_alive import keep_alive
import logging
from db import test_connection

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logging.getLogger("discord.gateway").setLevel(logging.DEBUG)

GUILD_ID = 1014974215952281672

@bot.tree.command(name="ping", description="Renvoie Pong !")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong !")

@bot.event
async def setup_hook():
    try:
        # Charger les extensions
        await bot.load_extension("commands.status")
        await bot.load_extension("commands.hello")
        await bot.load_extension("commands.avatar")
        await bot.load_extension("commands.test_db")
        await bot.load_extension("commands.menu")

        if os.getenv("ENV") == "dev":
            guild = Object(id=GUILD_ID)
            await bot.tree.sync(guild=guild)
            logger.info(f"✅ Commandes synchronisées localement sur le serveur {GUILD_ID}")
        else:
            await bot.tree.sync()
            logger.info("✅ Commandes synchronisées globalement.")

    except Exception as e:
        logger.error(f"❌ Erreur lors du chargement des extensions ou sync : {e}")

@bot.event
async def on_ready():
    logger.info(f"🤖 Bot connecté en tant que {bot.user}")
    await test_connection()

@bot.event
async def on_disconnect():
    logger.warning("⚠️ Bot déconnecté de Discord.")

@bot.event
async def on_resumed():
    logger.info("🔄 Session Discord reprise avec succès.")

# Lance le serveur Flask pour Render
keep_alive()

# Démarre le bot Discord
token = os.getenv("TOKEN")
if token:
    bot.run(token)
else:
    logger.error("❌ ERREUR : TOKEN non trouvé. Vérifie ton .env ou tes variables Render.")
