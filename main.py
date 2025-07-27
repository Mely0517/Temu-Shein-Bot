import os
import discord
from discord.ext import commands
from temu import setup_bot
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True  # Needed to read messages
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

setup_bot(bot)

bot.run(os.getenv("DISCORD_TOKEN"))
