from temu import setup_bot
from discord.ext import commands
import os

bot = commands.Bot(command_prefix="!")

setup_bot(bot)

bot.run(os.getenv("DISCORD_TOKEN"))
