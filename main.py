import discord
from discord.ext import commands
from temu import setup_bot
import os

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

setup_bot(bot)

if __name__ == "__main__":
    bot.run(os.getenv("DISCORD_TOKEN"))
