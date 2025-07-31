import discord
from discord.ext import commands
import os
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import asyncio
import random
import time

# === User Agent Rotation ===
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (Linux; Android 10)",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_2 like Mac OS X)",
    "Mozilla/5.0 (iPad; CPU OS 13_6 like Mac OS X)"
]

# === Referral Links ===
REFERRAL_LINKS = [
    "https://temu.com/a/VeHhz9bwz5DB1Fk",
    "https://onelink.shein.com/15/4vqj870",  # Add more SHEIN links here
]

# === Browser Config ===
def get_browser():
    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f"user-agent={random.choice(USER_AGENTS)}")
    return uc.Chrome(options=options)

# === Bot Setup ===
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.command()
async def launch(ctx):
    await ctx.send("🎯 Starting bot automation...")
    for link in REFERRAL_LINKS:
        try:
            browser = get_browser()
            browser.get(link)
            await asyncio.sleep(random.uniform(4, 6))

            # Scroll simulation
            browser.execute_script("window.scrollBy(0, 500);")
            await asyncio.sleep(random.uniform(2, 3))
            browser.execute_script("window.scrollBy(0, 800);")
            await asyncio.sleep(random.uniform(1, 2))

            await ctx.send(f"✅ Simulated activity for {link}")
            browser.quit()
        except Exception as e:
            await ctx.send(f"❌ Error with {link}: {e}")

def setup_bot():
    TOKEN = os.getenv("DISCORD_TOKEN")
    if not TOKEN:
        print("❌ DISCORD_TOKEN is missing")
        return
    bot.run(TOKEN)
