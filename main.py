import discord
from discord.ext import commands
import os
from temu import setup_bot

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

setup_bot(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(bot.start(os.getenv("DISCORD_TOKEN")))
