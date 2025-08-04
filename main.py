import discord
from discord.ext import commands
import os
from shein import boost_shein_link
from temu import boost_temu_link

TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}!")

@bot.command()
async def boost(ctx, link: str):
    if "shein.com" in link:
        await ctx.send(f"🚀 Starting SHEIN boost for: {link}")
        await boost_shein_link(link, ctx.channel)
    elif "temu.com" in link:
        await ctx.send(f"🚀 Starting TEMU boost for: {link}")
        await boost_temu_link(link, ctx.channel)
    else:
        await ctx.send("❌ Unsupported link format. Please send a valid SHEIN or TEMU link.")

bot.run(TOKEN)