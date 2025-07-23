# Your Temu invite/referral link
TEMU_REFERRAL_LINK = "https://temu.com/a/VeHhz9bwz5DB1Fk"
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_BOT_TOKEN')
TEMU_REFERRAL_LINK = "https://temu.com/a/VeHhz9bwz5DB1Fk"

intents = discord.Intents.default()
intents.message_content = True  # Enable command reading
bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user}!')

@bot.command()
async def boostme(ctx):
    await ctx.send(f"🚀 Boosting your Temu link...\n🔗 {TEMU_REFERRAL_LINK}")
    # TODO: Add auto-clicking code here later
    await ctx.send("✅ Help sent!")

bot.run(TOKEN)


