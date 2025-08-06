import discord
from discord.ext import commands
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

@bot.event
async def setup_hook():
    # Chargement des extensions
    await bot.load_extension("commands.status")
    await bot.load_extension("commands.hello")

    # Sync locale des commandes slash sur le serveur spécifié
    guild = discord.Object(id=GUILD_ID)
    await bot.tree.sync(guild=guild)
    logger.info(f"Commandes slash synchronisées sur le serveur {GUILD_ID}.")

@bot.event
async def on_ready():
    logger.info(f"Bot connecté en tant que {bot.user}")

@bot.command()
async def ping(ctx):
    await ctx.send("Pong !")

keep_alive()

token = os.getenv("TOKEN")
if token:
    bot.run(token)
else:
    logger.error("❌ ERREUR : TOKEN non trouvé. Vérifie ton .env ou tes variables Render.")
