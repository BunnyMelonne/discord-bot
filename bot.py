import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path="config")
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot connecté en tant que {bot.user}")

@bot.command()
async def ping(ctx):
    await ctx.send("Pong !")

bot.run(os.getenv("TOKEN"))