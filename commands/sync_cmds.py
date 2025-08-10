import os
import discord
from discord.ext import commands
from discord import app_commands
import logging

logger = logging.getLogger(__name__)

OWNER_ID = 998191350807797830

class SyncCmds(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="sync_commands", description="Synchronise toutes les commandes slash (globalement)")
    async def resync(self, interaction: discord.Interaction):
        if interaction.user.id != OWNER_ID:
            await interaction.response.send_message("❌ Tu n'as pas la permission d'utiliser cette commande.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)

        try:
            synced = await self.bot.tree.sync()
            logger.info(f"[SYNC] Commandes : {[cmd.name for cmd in synced]} | Total : {len(synced)}")
            await interaction.followup.send(f"✅ {len(synced)} commandes synchronisées globalement.", ephemeral=True)

        except Exception as e:
            logger.error(f"Erreur lors de la synchronisation : {e}", exc_info=True)
            await interaction.followup.send(f"❌ Erreur : {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(SyncCmds(bot))
