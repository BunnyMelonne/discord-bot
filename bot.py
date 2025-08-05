import discord
from discord.ext import commands
from dotenv import load_dotenv
from keep_alive import keep_alive
import os

# Charge les variables d'environnement depuis .env (en local) ou Render (en prod)
load_dotenv()

# Initialisation des intents (autorise la lecture des messages)
intents = discord.Intents.default()
intents.message_content = True

# Création du bot
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot connecté en tant que {bot.user}")

@bot.command()
async def ping(ctx):
    await ctx.send("Pong !")

# Démarrage du serveur Flask pour Render
keep_alive()

# Démarrage du bot Discord
token = os.getenv("TOKEN")
if token:
    bot.run(token)
else:
    print("❌ ERREUR : TOKEN non trouvé. Vérifie ton .env ou tes variables Render.")
