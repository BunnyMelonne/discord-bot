import discord
from discord import app_commands
from discord.ext import commands

class FeedbackModal(discord.ui.Modal, title="Envoyer un feedback"):
    sujet = discord.ui.TextInput(label="Sujet", placeholder="Le sujet de ton message", max_length=50)
    message = discord.ui.TextInput(label="Message", style=discord.TextStyle.paragraph, placeholder="Écris ton message ici...", max_length=500)

    def __init__(self):
        super().__init__()

    async def on_submit(self, interaction: discord.Interaction):
        # Tu peux ici traiter les données (par ex. envoyer dans un channel, base, etc.)
        sujet = self.sujet.value
        message = self.message.value
        await interaction.response.send_message(f"Merci pour ton feedback !\n**Sujet:** {sujet}\n**Message:** {message}", ephemeral=True)

class Modals(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="feedback", description="Envoie un feedback au bot.")
    async def feedback(self, interaction: discord.Interaction):
        modal = FeedbackModal()
        await interaction.response.send_modal(modal)

async def setup(bot):
    await bot.add_cog(Modals(bot))
