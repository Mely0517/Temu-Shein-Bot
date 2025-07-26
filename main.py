import discord
from discord.ext import commands
from temu import setup_bot  # Full Temu + SHEIN logic

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

setup_bot(bot)

if __name__ == "__main__":
    bot.run(os.getenv("DISCORD_TOKEN"))
