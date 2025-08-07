import discord
from discord.ext import commands
from discord import app_commands
import time
import platform

start_time = time.time()

# === Paramètres personnalisés ===
BOT_VERSION = "1.0.0"
CREATOR = "Melonne#998191350807797830"
INVITE_URL = "https://discord.com/oauth2/authorize?client_id=1402212878710476881&permissions=8&scope=bot"

class Status(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="status", description="Affiche les informations sur le bot")
    async def status(self, interaction: discord.Interaction):
        await interaction.response.defer()  # Accusé de réception rapide

        uptime_seconds = int(time.time() - start_time)
        hours, remainder = divmod(uptime_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        latency = round(self.bot.latency * 1000)
        guild_count = len(self.bot.guilds)
        user_count = sum(1 for g in self.bot.guilds for m in g.members if not m.bot)
        command_count = len(self.bot.tree.get_commands())
        python_version = platform.python_version()
        discord_version = discord.__version__
        os_name = platform.system()

        embed = discord.Embed(
            title="📡 Statut du bot",
            description="Voici les informations sur le bot.",
            color=discord.Color.blurple()
        )
        embed.add_field(name="👤 Connecté en tant que", value=f"{self.bot.user}", inline=False)
        embed.add_field(name="📡 Ping", value=f"{latency} ms", inline=True)
        embed.add_field(name="⏱️ Uptime", value=f"{hours}h {minutes}m {seconds}s", inline=True)
        embed.add_field(name="🛠️ Version", value=BOT_VERSION, inline=True)
        embed.add_field(name="📦 discord.py", value=discord_version, inline=True)
        embed.add_field(name="⚙️ Python", value=python_version, inline=True)
        embed.add_field(name="💻 Système", value=os_name, inline=True)
        embed.add_field(name="🧑‍🤝‍🧑 Serveurs", value=f"{guild_count}", inline=True)
        embed.add_field(name="👥 Utilisateurs", value=f"{user_count}", inline=True)
        embed.add_field(name="📜 Commandes", value=f"{command_count}", inline=True)
        embed.add_field(name="🧑 Créateur", value=CREATOR, inline=False)
        embed.add_field(name="🔗 Lien d'invitation", value=f"[Clique ici]({INVITE_URL})", inline=False)
        embed.set_footer(text="BotRonron 🐱")

        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Status(bot))
