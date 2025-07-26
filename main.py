import discord
from discord.ext import commands
import asyncio
from temu import setup_bot

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

setup_bot(bot)

@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user.name}')

if __name__ == "__main__":
    asyncio.run(bot.start(os.getenv("DISCORD_TOKEN")))
