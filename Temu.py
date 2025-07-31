import discord
from discord.ext import commands
import os
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import asyncio

# Set up the Chrome browser
def get_browser():
    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    return uc.Chrome(options=options)

# Configure Discord bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.command()
async def temu(ctx):
    await ctx.send("🟠 Opening Temu referral page...")
    try:
        browser = get_browser()
        browser.get("https://temu.com")
        await asyncio.sleep(5)
        await ctx.send("✅ Temu loaded successfully!")
        browser.quit()
    except Exception as e:
        await ctx.send(f"❌ Temu error: {e}")

def setup_bot():
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("❌ DISCORD_TOKEN not found in environment.")
        return
    bot.run(token)
