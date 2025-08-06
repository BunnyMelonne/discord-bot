import discord
from discord.ext import commands
from discord import app_commands

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="sync_local", description="Synchronise les commandes sur ce serveur uniquement (dev)")
    @commands.guild_only()
    async def sync_local(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("⛔ Tu dois être admin pour faire ça.", ephemeral=True)
            return

        synced = await self.bot.tree.sync(guild=interaction.guild)
        await interaction.response.send_message(
            f"✅ {len(synced)} commande(s) synchronisées localement sur **{interaction.guild.name}**.",
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(Admin(bot))
