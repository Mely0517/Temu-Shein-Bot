# temu.py

import discord
from discord.ext import commands, tasks
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import asyncio
import os
import json
import re

# ---------- CONFIG ----------

STATS_FILE = "stats.json"
REFERRAL_LINKS = {
    "temu": "https://temu.com/s/your-temu-ref",
    "shein": "https://onelink.shein.com/15/your-shein-ref"
}
AUTO_SHARE_CHANNEL_ID = 123456789012345678  # Replace with your actual Discord channel ID

# Tracks active game loops
game_loops = {"farm": False, "fish": False, "stack": False, "spin": False, "gift": False}
loop_tasks = {}
auto_sharing = False

# ---------- BROWSER SETUP ----------

def get_browser():
    options = uc.ChromeOptions()
    options.binary_location = "/usr/bin/google-chrome"
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0")
    return uc.Chrome(options=options)

# ---------- STATS ----------

def load_stats():
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE) as f:
            return json.load(f)
    return {}

def save_stats(stats):
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f, indent=2)

def increment_stat(link_type):
    stats = load_stats()
    stats[link_type] = stats.get(link_type, 0) + 1
    save_stats(stats)

# ---------- CORE CLAIM FUNCTION ----------

async def claim_link(link, user=None, channel=None):
    browser = None
    try:
        browser = get_browser()
        browser.get(link)
        await asyncio.sleep(5)

        # Try clicking any available claim buttons
        buttons = browser.find_elements(By.TAG_NAME, "button")
        clicked = False
        for button in buttons:
            text = button.text.lower()
            if any(keyword in text for keyword in ["receive", "claim", "accept", "help", "invite", "free", "join"]):
                button.click()
                clicked = True
                break

        if clicked:
            increment_stat("shein" if "shein.com" in link else "temu")
            if user:
                await user.send(f"✅ Link claimed: {link}")
            elif channel:
                await channel.send(f"✅ Link claimed: {link}")
        else:
            if user:
                await user.send(f"⚠️ Couldn’t find a button, but page opened.")
            elif channel:
                await channel.send(f"⚠️ Couldn’t find a button, but page opened.")

    except Exception as e:
        msg = f"❌ Error claiming link:\n```\n{str(e)}\n```"
        if user:
            await user.send(msg)
        elif channel:
            await channel.send(msg)
    finally:
        if browser:
            browser.quit()

# ---------- LINK DETECTION ----------

def detect_game_type(url):
    if "temu.com" in url:
        if "fishland" in url: return "fish"
        if "farm" in url: return "farm"
        if "stack" in url: return "stack"
        if "spin" in url: return "spin"
        if "gift" in url: return "gift"
        return "temu"
    elif "shein.com" in url:
        return "shein"
    return None

# ---------- DISCORD SETUP ----------

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot is online as {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Auto-detect links in messages
    links = re.findall(r'(https?://\S+)', message.content)
    for link in links:
        if "temu.com" in link or "shein.com" in link:
            await claim_link(link, user=message.author)
    await bot.process_commands(message)

# ---------- GAME COMMANDS ----------

@bot.command()
async def farm(ctx): await claim_link(REFERRAL_LINKS["temu"], ctx.author)
@bot.command()
async def fish(ctx): await claim_link(REFERRAL_LINKS["temu"], ctx.author)
@bot.command()
async def stack(ctx): await claim_link(REFERRAL_LINKS["temu"], ctx.author)
@bot.command()
async def spin(ctx): await claim_link(REFERRAL_LINKS["temu"], ctx.author)
@bot.command()
async def gift(ctx): await claim_link(REFERRAL_LINKS["temu"], ctx.author)
@bot.command()
async def shein(ctx): await claim_link(REFERRAL_LINKS["shein"], ctx.author)

@bot.command()
async def stats(ctx):
    stats = load_stats()
    await ctx.send(f"📊 Stats:\n" + "\n".join(f"{k}: {v}" for k, v in stats.items()))

# ---------- START BOT ----------

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    TOKEN = os.getenv("DISCORD_TOKEN")
    bot.run(TOKEN)
