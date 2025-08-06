import discord
from discord import app_commands
from discord.ext import commands

class Hello(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Slash command simple nommée /hello
    @app_commands.command(name="hello", description="Dis bonjour")
    async def hello(self, interaction: discord.Interaction):
        await interaction.response.send_message("Salut ! 👋")

async def setup(bot):
    await bot.add_cog(Hello(bot))
    # Important : synchroniser les commandes slash
    await bot.tree.sync()
