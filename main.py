import os
import discord
from discord.ext import commands
from temu import setup_bot  # This is your full Temu + SHEIN game logic

intents = discord.Intents.default()
intents.message_content = True  # Required to read messages for commands

bot = commands.Bot(command_prefix='!', intents=intents)

# Call the setup function from temu.py to load all commands
setup_bot(bot)

@bot.event
async def on_ready():
    print(f"✅ Bot is online as {bot.user}")

# Start the bot with your token from environment variable
if __name__ == "__main__":
    TOKEN = os.getenv("DISCORD_TOKEN")
    if TOKEN is None:
        print("❌ DISCORD_TOKEN not set in environment variables.")
    else:
        bot.run(TOKEN)
