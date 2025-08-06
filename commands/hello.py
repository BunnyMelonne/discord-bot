import discord
from discord import app_commands
from discord.ext import commands

class HelloButton(discord.ui.View):
    def __init__(self, user):
        super().__init__(timeout=None)
        self.user = user

    @discord.ui.button(label="Dire bonjour 👋", style=discord.ButtonStyle.primary)
    async def say_hello(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f"Salut {self.user.mention} ! 👋", ephemeral=True)

class Hello(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="hello", description="Affiche un bouton pour dire bonjour")
    async def hello(self, interaction: discord.Interaction):
        view = HelloButton(interaction.user)
        await interaction.response.send_message("Clique sur le bouton ci-dessous :", view=view)

async def setup(bot):
    await bot.add_cog(Hello(bot))
    await bot.tree.sync()
