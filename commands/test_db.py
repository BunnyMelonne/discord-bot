from discord.ext import commands
from db import users_collection
from datetime import datetime

class TestDB(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="testdb")
    async def test_db(self, ctx):
        try:
            # On essaye d'insérer un doc temporaire (avec un champ timestamp pour ne pas écraser)
            from datetime import datetime
            result = users_collection.insert_one({"test": "ok", "timestamp": datetime.utcnow()})
            await ctx.send(f"✅ DB ok, id doc inséré : {result.inserted_id}")
        except Exception as e:
            await ctx.send(f"❌ Erreur DB : {e}")

async def setup(bot):
    await bot.add_cog(TestDB(bot))
