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
async def boost(ctx, link: str):
    try:
        if "temu.com" in link:
            await ctx.send(f"🟡 Starting Temu boost for: {link}")
            await boost_temu(link)
            await ctx.send("✅ Temu boost completed.")
        elif "shein.com" in link:
            await ctx.send(f"🟡 Starting SHEIN boost for: {link}")
            await boost_shein(link)
            await ctx.send("✅ SHEIN boost completed.")
        else:
            await ctx.send("❌ Invalid link. Please send a valid Temu or SHEIN link.")
    except Exception as e:
        await ctx.send(f"❌ Error with {link}: {e}")

bot.run(TOKEN)