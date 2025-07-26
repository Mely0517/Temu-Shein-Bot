import discord
from discord.ext import commands
from temu import setup_bot  # This now returns the configured bot

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
bot = setup_bot(bot)  # Corrected to match temu.py function

if __name__ == "__main__":
    import os
    bot.run(os.getenv("DISCORD_TOKEN"))
