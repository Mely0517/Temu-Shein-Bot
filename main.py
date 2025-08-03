import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

from temu import start_temu
from shein import start_shein

load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.command()
async def temu(ctx, link: str = None):
    await ctx.send("🚀 Starting Temu boost...")
    await start_temu(link, ctx)

@bot.command()
async def shein(ctx, link: str = None):
    await ctx.send("🚀 Starting SHEIN boost...")
    await start_shein(link, ctx)

if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ DISCORD_BOT_TOKEN not set.")