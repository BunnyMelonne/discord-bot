import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional

class Avatar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="avatar", description="Affiche l'avatar d'un utilisateur")
    @app_commands.describe(user="L'utilisateur dont tu veux voir l'avatar")
    async def avatar(self, interaction: discord.Interaction, user: Optional[discord.abc.User] = None):
        user = user or interaction.user
        embed = discord.Embed(
            title=f"Avatar de {user.display_name}",
            color=discord.Color.blurple()
        )
        embed.set_image(url=user.display_avatar.url)
        embed.set_footer(text=f"ID : {user.id}")
        embed.add_field(name="Lien direct", value=f"[Télécharger]({user.display_avatar.url})", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=False)

async def setup(bot):
    await bot.add_cog(Avatar(bot))
