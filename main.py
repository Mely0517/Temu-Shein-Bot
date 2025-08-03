import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from temu import boost_temu
from shein import boost_shein

load_dotenv()

TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.command()
async def temu(ctx, link=None):
    await ctx.send("🚀 Starting Temu boost...")
    await boost_temu(ctx, link)

@bot.command()
async def shein(ctx, link=None):
    await ctx.send("🚀 Starting SHEIN boost...")
    await boost_shein(ctx, link)

bot.run(TOKEN)