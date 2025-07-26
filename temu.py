import discord
from discord.ext import commands, tasks
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import asyncio
import os
import json
import re

TOKEN = os.getenv("DISCORD_TOKEN")
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

REFERRAL_LINKS = {
    "temu": "https://temu.com/s/your-code",
    "shein": "https://onelink.shein.com/15/your-code"
}

STATS_FILE = "stats.json"
AUTO_SHARE_CHANNEL_ID = 123456789012345678  # Replace with your real channel ID
game_loops = {"farm": False, "fish": False, "stack": False, "spin": False, "gift": False}
loop_tasks = {}
auto_sharing = False

# --- Browser Setup for Render ---
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

# --- Helpers ---
def load_stats():
    if not os.path.exists(STATS_FILE):
        return {}
    with open(STATS_FILE, "r") as f:
        return json.load(f)

def save_stats(data):
    with open(STATS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def increment_stat(stat):
    stats = load_stats()
    stats[stat] = stats.get(stat, 0) + 1
    save_stats(stats)

async def claim_game(link, ctx):
    try:
        browser = get_browser()
        browser.get(link)
        await asyncio.sleep(8)
        try:
            button = browser.find_element(By.TAG_NAME, "button")
            button.click()
            await asyncio.sleep(2)
            await ctx.send("🎉 Button clicked successfully!")
        except Exception:
            await ctx.send("⚠️ Couldn’t find a button, but page opened.")
        browser.quit()
        increment_stat("claims")
    except Exception as e:
        await ctx.send(f"❌ Error: {e}")

def detect_game_type(link):
    if "temu" in link:
        if "spin" in link: return "spin"
        if "stack" in link: return "stack"
        if "fish" in link: return "fish"
        if "farm" in link: return "farm"
        if "gift" in link: return "gift"
        return "temu"
    elif "shein" in link:
        return "shein"
    return "unknown"

# --- Discord Commands ---
@bot.event
async def on_ready():
    print(f"✅ Bot is ready. Logged in as {bot.user}")
    if AUTO_SHARE_CHANNEL_ID and auto_sharing:
        share_links.start()

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    match = re.search(r'(https?://[^\s]+)', message.content)
    if match:
        link = match.group(1)
        game_type = detect_game_type(link)
        await message.channel.send(f"🎮 Detected {game_type} link... claiming!")
        await claim_game(link, message.channel)
    await bot.process_commands(message)

@bot.command()
async def farm(ctx):
    await loop_or_once("farm", ctx)

@bot.command()
async def fish(ctx):
    await loop_or_once("fish", ctx)

@bot.command()
async def stack(ctx):
    await loop_or_once("stack", ctx)

@bot.command()
async def spin(ctx):
    await loop_or_once("spin", ctx)

@bot.command()
async def gift(ctx):
    await loop_or_once("gift", ctx)

@bot.command()
async def shein(ctx):
    await claim_game(REFERRAL_LINKS["shein"], ctx)

@bot.command()
async def temu(ctx):
    await claim_game(REFERRAL_LINKS["temu"], ctx)

@bot.command()
async def stats(ctx):
    stats = load_stats()
    msg = "\n".join(f"📊 {k}: {v}" for k, v in stats.items()) or "No data yet."
    await ctx.send(f"📈 Stats:\n{msg}")

@bot.command()
async def start_share(ctx):
    global auto_sharing
    auto_sharing = True
    share_links.start()
    await ctx.send("📢 Auto sharing started!")

@bot.command()
async def stop_share(ctx):
    global auto_sharing
    auto_sharing = False
    share_links.stop()
    await ctx.send("🚫 Auto sharing stopped.")

# --- Loop Helpers ---
async def loop_or_once(game, ctx):
    if not game_loops[game]:
        game_loops[game] = True
        await ctx.send(f"🔁 Starting {game} auto loop...")
        async def loop_func():
            while game_loops[game]:
                await claim_game(REFERRAL_LINKS["temu"], ctx)
                await asyncio.sleep(45)
        loop_tasks[game] = asyncio.create_task(loop_func())
    else:
        game_loops[game] = False
        loop_tasks[game].cancel()
        await ctx.send(f"⏹️ Stopped {game} loop.")

# --- Auto Share Task ---
@tasks.loop(minutes=60)
async def share_links():
    channel = bot.get_channel(AUTO_SHARE_CHANNEL_ID)
    if channel:
        await channel.send(f"🥳 10 free items from SHEIN await — don’t miss out!\n{REFERRAL_LINKS['shein']}")
        await channel.send(f"🎁 Temu prize game link:\n{REFERRAL_LINKS['temu']}")
        increment_stat("shared")



