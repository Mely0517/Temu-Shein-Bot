import os
import discord
from discord.ext import commands
from temu import setup_bot  # Your full Temu + SHEIN bot logic

intents = discord.Intents.default()
intents.message_content = True  # Required to read messages for commands

bot = commands.Bot(command_prefix='!', intents=intents)

# Load commands and events from temu.py
setup_bot(bot)

@bot.event
async def on_ready():
    print(f"✅ Bot is online as {bot.user}")

if __name__ == "__main__":
    TOKEN = os.getenv("DISCORD_TOKEN")
    if not TOKEN:
        print("❌ DISCORD_TOKEN environment variable not set!")
    else:
        bot.run(TOKEN)

