import discord
from discord.ext import commands
import time

start_time = time.time()

class Status(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def status(self, ctx):
        uptime_seconds = int(time.time() - start_time)
        hours, remainder = divmod(uptime_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        latency = round(self.bot.latency * 1000)

        embed = discord.Embed(
            title="📡 Statut du bot",
            color=discord.Color.blurple()
        )
        embed.add_field(name="Connecté en tant que", value=f"{self.bot.user}", inline=False)
        embed.add_field(name="Ping", value=f"{latency} ms", inline=True)
        embed.add_field(name="Uptime", value=f"{hours}h {minutes}m {seconds}s", inline=True)
        embed.set_footer(text="BotRonron 🐱")

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Status(bot))
