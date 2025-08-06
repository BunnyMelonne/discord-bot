import discord
from discord import app_commands
from discord.ext import commands

class TimeoutView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)
        self.message = None

    async def on_timeout(self):
        try:
            if self.message:
                await self.message.edit(view=None)
        except discord.errors.NotFound:
            pass

class MultiButtonView(TimeoutView):
    def __init__(self, user):
        super().__init__()
        self.user = user

    @discord.ui.button(label="Dire bonjour 👋", style=discord.ButtonStyle.primary)
    async def say_hello(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            f"Salut {self.user.mention} ! 👋", ephemeral=True
        )

    @discord.ui.button(label="Dire au revoir 👋", style=discord.ButtonStyle.secondary)
    async def say_bye(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            f"Au revoir {self.user.mention} ! 👋", ephemeral=True
        )

    @discord.ui.button(label="Supprimer le message ❌", style=discord.ButtonStyle.danger)
    async def delete_message(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.message.delete()

class Hello(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="multibutton", description="Teste plusieurs boutons avec timeout")
    async def multibutton(self, interaction: discord.Interaction):
        view = MultiButtonView(interaction.user)
        await interaction.response.send_message("Choisis une option :", view=view)
        sent_message = await interaction.original_response()
        view.message = sent_message

async def setup(bot):
    await bot.add_cog(Hello(bot))
