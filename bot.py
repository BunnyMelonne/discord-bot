import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from keep_alive import keep_alive
import os
import logging

load_dotenv()

GUILD_ID = 1014974215952281672

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Configure le logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Slash command ping
@bot.tree.command(name="ping", description="Renvoie Pong !")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong !")

@bot.event
async def setup_hook():
    try:
        # Charger les extensions
        await bot.load_extension("commands.status")
        await bot.load_extension("commands.hello")
        await bot.tree.sync()
        logger.info("✅ Commandes slash globales synchronisées.")
        
    except Exception as e:
        logger.error(f"❌ Erreur lors du chargement des extensions ou sync : {e}")

@bot.event
async def on_ready():
    logger.info(f"🤖 Bot connecté en tant que {bot.user}")

# Lance le serveur Flask pour Render
keep_alive()

# Démarre le bot Discord
token = os.getenv("TOKEN")
if token:
    bot.run(token)
else:
    logger.error("❌ ERREUR : TOKEN non trouvé. Vérifie ton .env ou tes variables Render.")
