import discord
from discord import app_commands
from discord.ext import commands, tasks

class JobCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.my_loop.start()

    @tasks.loop(seconds=60)
    async def my_loop(self):
        channel = self.bot.get_channel(1316242941055991848)
        if channel:
            await channel.send("Le job a été exécuté ✅")

    @my_loop.before_loop
    async def before_my_loop(self):
        await self.bot.wait_until_ready()

    @app_commands.command(name="startjob", description="Démarre la boucle du job")
    async def startjob(self, interaction: discord.Interaction):
        if not self.my_loop.is_running():
            self.my_loop.start()
            await interaction.response.send_message("La boucle du job a démarré !", ephemeral=True)
        else:
            await interaction.response.send_message("La boucle tourne déjà.", ephemeral=True)

    @app_commands.command(name="stopjob", description="Arrête la boucle du job")
    async def stopjob(self, interaction: discord.Interaction):
        if self.my_loop.is_running():
            self.my_loop.cancel()
            await interaction.response.send_message("La boucle du job a été arrêtée.", ephemeral=True)
        else:
            await interaction.response.send_message("La boucle n'était pas en cours.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(JobCog(bot))
