import discord
from discord import app_commands
from discord.ext import commands

class Avatar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="avatar", description="Affiche l'avatar d'un utilisateur")
    @app_commands.describe(user="L'utilisateur dont tu veux voir l'avatar")
    async def avatar(self, interaction: discord.Interaction, user: discord.User = None):
        user = user or interaction.user
        await interaction.response.send_message(f"Avatar de {user.mention} : {user.display_avatar.url}")

async def setup(bot):
    await bot.add_cog(Avatar(bot))
