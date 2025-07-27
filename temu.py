import discord
from discord.ext import commands, tasks
import os
import re
import time
import json
import random
import asyncio
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

shared_links = []
rewards_db_path = "rewards.json"

# === Load or Init Rewards DB ===
if os.path.exists(rewards_db_path):
    with open(rewards_db_path, "r") as f:
        rewards_data = json.load(f)
else:
    rewards_data = {}

# === Headless Chrome Setup ===
def get_browser():
    options = uc.ChromeOptions()
    options.binary_location = "/usr/bin/google-chrome"
    options.add_argument("--headless=new")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")
    return uc.Chrome(options=options)

# === Platform Sharing ===
def generate_share_message(link):
    return {
        "reddit": f"Help me win free stuff! 🛍️ Click this link: {link}",
        "twitter": f"🎁 Just played this game! Claim yours here 👉 {link}",
        "whatsapp": f"Check this out! 🚨 Free items: {link}"
    }

# === Button Clicker ===
def click_buttons(driver, keywords):
    try:
        buttons = driver.find_elements(By.TAG_NAME, "button")
        for btn in buttons:
            if any(kw.lower() in btn.text.lower() for kw in keywords):
                btn.click()
                time.sleep(2)
                return True
    except Exception:
        pass
    return False

# === Game Detectors ===
def detect_temu_game(link):
    if "fish" in link: return "Fishland"
    if "farm" in link: return "Farm"
    if "stack" in link: return "Stack"
    if "spin" in link: return "Spin"
    if "gift" in link: return "5-Gift Game"
    return "Temu Game"

def detect_shein_game(link):
    if "10 free items" in link or "4vv" in link: return "10 Free Items"
    if "50" in link: return "$50 Off"
    if "freebie" in link or "gift" in link: return "Free Gift Grab"
    if "1000" in link: return "$1000 Prize"
    return "SHEIN Game"

# === Auto-Play Handler ===
def auto_play_game(link, user_id=None):
    try:
        driver = get_browser()
        driver.get(link)
        time.sleep(3)

        if "temu.com" in link:
            game_type = detect_temu_game(link)
        elif "shein.com" in link:
            game_type = detect_shein_game(link)
        else:
            driver.quit()
            return "❌ Unsupported link"

        success = False
        for _ in range(5):
            if click_buttons(driver, ["Go", "Play", "Invite", "Collect", "Get", "Join"]):
                success = True
            time.sleep(random.uniform(1.5, 3.5))

        title = driver.title
        if user_id:
            if str(user_id) not in rewards_data:
                rewards_data[str(user_id)] = []
            rewards_data[str(user_id)].append({"type": game_type, "title": title, "link": link})
            with open(rewards_db_path, "w") as f:
                json.dump(rewards_data, f, indent=2)

        driver.quit()
        return f"✅ Played {game_type} | {title}" if success else f"⚠️ Opened {game_type} but no button found."

    except Exception as e:
        return f"❌ Error: {str(e)}"

# === COMMAND: !claim <link> ===
@bot.command()
async def claim(ctx, link: str):
    await ctx.send("🔄 Processing your link...")
    result = auto_play_game(link, user_id=ctx.author.id)
    await ctx.send(result)

# === Game Shortcuts ===
@bot.command()
async def farm(ctx): await claim(ctx, "https://temu.com/s/farm-invite-link")

@bot.command()
async def fish(ctx): await claim(ctx, "https://temu.com/s/fishland-invite-link")

@bot.command()
async def stack(ctx): await claim(ctx, "https://temu.com/s/stack-invite-link")

@bot.command()
async def spin(ctx): await claim(ctx, "https://temu.com/s/spin-invite-link")

@bot.command()
async def gift(ctx): await claim(ctx, "https://temu.com/s/5-gift-invite-link")

@bot.command()
async def shein(ctx): await claim(ctx, "https://shein.com/your-game-link")

# === View Your Rewards ===
@bot.command()
async def myitems(ctx):
    user_id = str(ctx.author.id)
    items = rewards_data.get(user_id, [])
    if not items:
        await ctx.send("🪣 No claimed items yet.")
    else:
        msg = "\n".join([f"{x['type']} - {x['title']}" for x in items[-10:]])
        await ctx.send(f"📦 Your recent items:\n{msg}")

# === Leaderboard ===
@bot.command()
async def leaderboard(ctx):
    ranking = sorted(rewards_data.items(), key=lambda x: len(x[1]), reverse=True)
    msg = "\n".join([f"<@{uid}>: {len(entries)} items" for uid, entries in ranking[:5]])
    await ctx.send(f"🏆 Leaderboard:\n{msg}")

# === Add Link to Auto-Play Queue ===
@bot.command()
async def addlink(ctx, link: str):
    shared_links.append(link)
    await ctx.send("✅ Link added to auto-play queue.")

# === Auto-Loop ===
@bot.command()
async def loop(ctx):
    if not auto_loop.is_running():
        auto_loop.start()
        await ctx.send("🔁 Auto-loop every 30 minutes started.")
    else:
        await ctx.send("♻️ Auto-loop already running.")

@tasks.loop(minutes=30)
async def auto_loop():
    for link in shared_links:
        result = auto_play_game(link)
        print(f"[LOOP] {result}")

# === Scheduled DMs (Every Hour) ===
@tasks.loop(hours=1)
async def send_scheduled_dms():
    for user_id, entries in rewards_data.items():
        user = await bot.fetch_user(int(user_id))
        if user:
            try:
                await user.send(f"🕐 Reminder: You have {len(entries)} items. Share your links to earn more!")
            except:
                continue

# === Setup Bot (called from main.py) ===
def setup_bot():
    @bot.event
    async def on_ready():
        print(f"✅ Logged in as {bot.user}")
        if not send_scheduled_dms.is_running():
            send_scheduled_dms.start()
        if not auto_loop.is_running():
            auto_loop.start()
    return bot
