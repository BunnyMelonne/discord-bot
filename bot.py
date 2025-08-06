import discord
from discord.ext import commands
from dotenv import load_dotenv
from keep_alive import keep_alive
import os

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def setup_hook():
    await bot.load_extension("commands.status")
    await bot.load_extension("commands.hello")

@bot.event
async def on_ready():
    print(f"Bot connecté en tant que {bot.user}")

@bot.command()
async def ping(ctx):
    await ctx.send("Pong !")

keep_alive()

token = os.getenv("TOKEN")
if token:
    bot.run(token)
else:
    print("❌ ERREUR : TOKEN non trouvé. Vérifie ton .env ou tes variables Render.")
