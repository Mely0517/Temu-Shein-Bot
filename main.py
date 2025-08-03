import discord
from discord.ext import commands
import os
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
async def boost(ctx, url: str):
    await ctx.send(f"🎯 Starting boost for: {url}")
    try:
        if "temu.com" in url:
            await boost_temu(url)
        elif "shein.com" in url:
            await boost_shein(url)
        else:
            await ctx.send("⚠️ Unsupported link.")
            return
        await ctx.send("✅ Boost complete!")
    except Exception as e:
        await ctx.send(f"❌ Error with {url}: {str(e)}")

bot.run(TOKEN)