import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv
from temu import visit_temu_referral
from shein import visit_shein_referral

load_dotenv()

TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}!")

@bot.command()
async def boost(ctx, *, link: str):
    if "temu.com" in link:
        await ctx.send("🚀 Boosting TEMU link...")
        await visit_temu_referral(link)
        await ctx.send("✅ TEMU visit complete.")
    elif "shein.com" in link:
        await ctx.send("🚀 Boosting SHEIN link...")
        await visit_shein_referral(link)
        await ctx.send("✅ SHEIN visit complete.")
    else:
        await ctx.send("⚠️ Invalid link. Please send a Temu or SHEIN referral link.")

bot.run(TOKEN)