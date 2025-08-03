import discord
from discord.ext import commands
import os
from pyppeteer import launch
from asyncio import sleep
import asyncio
import random

REFERRAL_LINKS = [
    "https://temu.com/a/VeHhz9bwz5DB1Fk",
    "https://onelink.shein.com/15/4vzpagy20nbj",
    "https://onelink.shein.com/15/4vzqhnqesl4x",
    "https://onelink.shein.com/15/4vzqljtlysyj",
    "https://onelink.shein.com/15/4vzqo6j35pna"
]

async def visit_link(link):
    browser = await launch(headless=True, args=["--no-sandbox", "--disable-setuid-sandbox"])
    page = await browser.newPage()
    await page.setUserAgent(random.choice([
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        "Mozilla/5.0 (Linux; Android 10)"
    ]))
    await page.goto(link)
    await sleep(random.randint(4, 7))
    await page.evaluate('window.scrollBy(0, document.body.scrollHeight)')
    await sleep(random.randint(2, 5))
    await browser.close()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.command()
async def start(ctx):
    await ctx.send("🚀 Starting referral booster...")
    for link in REFERRAL_LINKS:
        try:
            await visit_link(link)
            await ctx.send(f"✅ Visited: {link}")
        except Exception as e:
            await ctx.send(f"❌ Error with {link}: {e}")

def setup_bot():
    TOKEN = os.getenv("DISCORD_TOKEN")
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("❌ DISCORD_TOKEN not set.")