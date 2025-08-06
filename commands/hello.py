import discord
from discord import app_commands
from discord.ext import commands

class TimeoutView(discord.ui.View):
    def __init__(self, user):
        super().__init__(timeout=30)  # timeout en secondes
        self.user = user
        self.message = None  # Pour garder la référence au message envoyé

    async def on_timeout(self):
        # Désactive tous les boutons quand le timeout arrive
        for child in self.children:
            child.disabled = True
        
        # Met à jour le message avec les boutons désactivés
        if self.message:
            await self.message.edit(view=self)

class MultiButtonView(TimeoutView):
    def __init__(self, user):
        super().__init__(user)

    @discord.ui.button(label="Dire bonjour 👋", style=discord.ButtonStyle.primary)
    async def say_hello(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            f"Salut {self.user.mention} ! 👋", 
            ephemeral=True
        )

    @discord.ui.button(label="Dire au revoir 👋", style=discord.ButtonStyle.secondary)
    async def say_bye(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            f"Au revoir {self.user.mention} ! 👋", 
            ephemeral=True
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
        # Enregistre le message dans la vue pour pouvoir l'éditer plus tard
        message = await interaction.response.send_message("Choisis une option :", view=view)
        # Comme interaction.response.send_message() ne renvoie pas directement le message,
        # il faut utiliser fetch_message après (ou response deferred + followup)
        # Ici on doit récupérer le message envoyé :
        sent_message = await interaction.original_response()
        view.message = sent_message

async def setup(bot):
    await bot.add_cog(Hello(bot))
    await bot.tree.sync()
