import discord
from discord.ext import commands
import os
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import asyncio
import random
import time

REFERRAL_LINKS = [
    "https://temu.com/a/VeHhz9bwz5DB1Fk",
    "https://onelink.shein.com/15/4vzpagy20nbj",
    "https://onelink.shein.com/15/4vzqhnqesl4x",
    "https://onelink.shein.com/15/4vzqljtlysyj",
    "https://onelink.shein.com/15/4vzqo6j35pna"
]

def get_browser():
    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    user_agent = random.choice([
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        "Mozilla/5.0 (Linux; Android 10)"
    ])
    options.add_argument(f"user-agent={user_agent}")
    return uc.Chrome(options=options)

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
            browser = get_browser()
            browser.get(link)
            await asyncio.sleep(random.randint(4, 8))
            browser.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
            await asyncio.sleep(random.randint(3, 6))
            browser.quit()
            await ctx.send(f"✅ Visited: {link}")
        except Exception as e:
            await ctx.send(f"❌ Error with {link}: {e}")

def setup_bot():
    TOKEN = os.getenv("DISCORD_TOKEN")
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("❌ DISCORD_TOKEN not set.")
