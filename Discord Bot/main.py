
import discord
from discord.ext import commands
import os

TOKEN = os.getenv("ALTOBOT_TOKEN")
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="/", intents=intents)

# Load all cogs
async def load_cogs():
    await bot.add_cog(ModerationCog(bot))
    await bot.add_cog(AIChatCog(bot))
    await bot.add_cog(ImageEditCog(bot))
    await bot.add_cog(VerificationCog(bot))
    await bot.add_cog(DownloaderCog(bot))
    await bot.add_cog(E621Cog(bot))
    await bot.add_cog(StatsCog(bot))

@bot.event
async def on_ready():
    await load_cogs()
    print("Bot ready!")

if __name__ == "__main__":
    bot.run(TOKEN)
