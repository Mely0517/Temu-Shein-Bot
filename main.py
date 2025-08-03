import os
import discord
from discord.ext import commands
from temu import boost_temu
from shein import boost_shein
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}!")
    channel_id = os.getenv("DISCORD_CHANNEL_ID")
    if channel_id:
        channel = bot.get_channel(int(channel_id))
        if channel:
            await channel.send("🚀 Bot is online and ready to boost Temu/SHEIN links!")

@bot.command()
async def temu(ctx, link: str = None):
    await ctx.send("🟠 Starting Temu boost...")
    await boost_temu(link)
    await ctx.send("✅ Temu boost complete!")

@bot.command()
async def shein(ctx, link: str = None):
    await ctx.send("🟣 Starting SHEIN boost...")
    await boost_shein(link)
    await ctx.send("✅ SHEIN boost complete!")

def setup_bot():
    token = os.getenv("DISCORD_TOKEN")
    if token:
        bot.run(token)
    else:
        print("❌ DISCORD_TOKEN not found in environment variables.")