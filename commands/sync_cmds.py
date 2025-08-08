import os
import discord
from discord import Object
from discord.ext import commands
from discord import app_commands

GUILD_ID = 1014974215952281672

class SyncCmds(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="sync_commands", description="Resynchronise les commandes slash du bot")
    async def resync(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        try:
            if os.getenv("ENV") == "dev":
                guild = Object(id=GUILD_ID)
                await self.bot.tree.sync(guild=guild)
                message = f"✅ Commandes synchronisées localement sur le serveur {GUILD_ID}."
            else:
                await self.bot.tree.sync()
                message = "✅ Commandes synchronisées globalement."

            await interaction.followup.send(message, ephemeral=True)

        except Exception as e:
            await interaction.followup.send(f"❌ Erreur lors de la synchronisation : {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(SyncCmds(bot))
