import discord
from discord.ext import commands
from discord import app_commands
from db import users_collection
import logging

logger = logging.getLogger(__name__)

class DropdownView(discord.ui.View):
    def __init__(self, users_collection):
        super().__init__()
        self.users_collection = users_collection

    @discord.ui.select(
        placeholder="Choisis une option...",
        options=[
            discord.SelectOption(label="Option 1", description="Ceci est la 1ère option", emoji="1️⃣"),
            discord.SelectOption(label="Option 2", description="Ceci est la 2ème option", emoji="2️⃣"),
            discord.SelectOption(label="Option 3", description="Ceci est la 3ème option", emoji="3️⃣"),
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        choice = select.values[0]
        user_id = interaction.user.id

        try:
            result = await self.users_collection.update_one(
                {"user_id": user_id},
                {"$set": {"last_choice": choice}},
                upsert=True
            )
            logger.info(f"User {user_id} choice saved in DB. Matched: {result.matched_count}, Modified: {result.modified_count}")
        except Exception as e:
            logger.error(f"Failed to save choice for user {user_id}: {e}")

        await interaction.response.send_message(f"Tu as choisi : {choice} !", ephemeral=True)

class Menu(commands.Cog):
    def __init__(self, bot, users_collection):
        self.bot = bot
        self.users_collection = users_collection

    @app_commands.command(name="menu", description="Commande avec un menu déroulant")
    async def menu(self, interaction: discord.Interaction):
        view = DropdownView(self.users_collection)
        await interaction.response.send_message("Choisis une option dans le menu :", view=view)

async def setup(bot):
    await bot.add_cog(Menu(bot, users_collection))
