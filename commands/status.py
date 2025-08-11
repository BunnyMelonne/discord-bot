import discord
from discord.ext import commands
from discord import app_commands
import time
import platform
import datetime

# Constantes
START_TIME  = time.time()
BOT_VERSION = "1.0.0"
CREATOR     = "<@998191350807797830>"
INVITE_URL  = "https://discord.com/oauth2/authorize?client_id=1402212878710476881&permissions=8&scope=bot"

class Status(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="status", description="Affiche les informations sur le bot")
    async def status(self, interaction: discord.Interaction):
        await interaction.response.defer()

        # Calcul uptime
        uptime_seconds = int(time.time() - START_TIME)
        uptime_str     = str(datetime.timedelta(seconds=uptime_seconds))

        # Infos système & bot
        latency         = round(self.bot.latency * 1000)
        guild_count     = len(self.bot.guilds)
        user_count      = len({m.id for g in self.bot.guilds for m in g.members if not m.bot})
        command_count   = len(self.bot.tree.get_commands())
        python_version  = platform.python_version()
        discord_version = discord.__version__
        os_name         = platform.system()
        start_dt        = datetime.datetime.fromtimestamp(START_TIME).strftime("%Y-%m-%d %H:%M:%S")

        # Création embed
        embed = discord.Embed(
            title="📡 Statut du bot",
            description="Voici les informations sur le bot.",
            color=discord.Color.blurple()
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(text=f"Demandé par {interaction.user}", icon_url=interaction.user.display_avatar.url)

        fields = [
            ("📡 Ping", f"{latency} ms"),
            ("⏱️ Uptime", uptime_str),
            ("🕒 Démarré le", start_dt),
            ("🛠️ Version", BOT_VERSION),
            ("📦 discord.py", discord_version),
            ("⚙️ Python", python_version),
            ("💻 Système", os_name),
            ("🧑‍🤝‍🧑 Serveurs", guild_count),
            ("👥 Utilisateurs", user_count),
            ("📜 Commandes", command_count),
            ("🧑 Créateur", CREATOR),
            ("🔗 Lien d'invitation", f"[Clique ici]({INVITE_URL})"),
        ]

        for name, value in fields:
            embed.add_field(name=name, value=str(value), inline=True)

        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Status(bot))
