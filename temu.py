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
item_tracker = []
rewards_file = "rewards.json"
user_stats = {}

# === Headless Chrome Setup ===
def get_browser():
    options = uc.ChromeOptions()
    options.binary_location = "/usr/bin/google-chrome"
    options.add_argument("--headless=new")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")
    return uc.Chrome(options=options)

# === Load/Save Rewards ===
def save_rewards():
    with open(rewards_file, "w") as f:
        json.dump(user_stats, f, indent=2)

def load_rewards():
    global user_stats
    if os.path.exists(rewards_file):
        with open(rewards_file, "r") as f:
            user_stats = json.load(f)

load_rewards()

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
    if "50" in link: return "$50 Off Game"
    if "freebie" in link or "gift" in link: return "Free Gift Grab"
    if "1000" in link: return "$1000 Prize"
    return "SHEIN Game"

# === Auto-play Handler ===
def auto_play_game(link, user=None):
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
        item_tracker.append({"link": link, "title": title, "type": game_type})
        if user:
            user_stats.setdefault(str(user.id), {"name": user.name, "count": 0})
            user_stats[str(user.id)]["count"] += 1
            save_rewards()
        driver.quit()

        if success:
            return f"✅ Played {game_type} | {title}"
        else:
            return f"⚠️ Page opened, but no button found."

    except Exception as e:
        return f"❌ Error: {str(e)}"

# === Core Command: !claim <link> ===
@bot.command()
async def claim(ctx, link: str):
    await ctx.send("🔄 Processing link...")
    result = auto_play_game(link, ctx.author)
    await ctx.send(result)

# === Shortcuts ===
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
async def shein(ctx): await claim(ctx, "https://onelink.shein.com/15/your-shein-game-link")

# === Leaderboard ===
@bot.command()
async def leaderboard(ctx):
    if not user_stats:
        await ctx.send("📊 No stats yet.")
    else:
        top = sorted(user_stats.items(), key=lambda x: x[1]["count"], reverse=True)[:10]
        msg = "\n".join([f"{i+1}. {v['name']} - {v['count']} wins" for i, (k, v) in enumerate(top)])
        await ctx.send(f"🏆 Leaderboard:\n{msg}")

# === My Recent Items ===
@bot.command()
async def myitems(ctx):
    user_id = str(ctx.author.id)
    count = user_stats.get(user_id, {}).get("count", 0)
    if count == 0:
        await ctx.send("🪣 No items claimed yet.")
    else:
        await ctx.send(f"📦 You’ve claimed {count} items!")

# === Share to Platforms ===
@bot.command()
async def share(ctx, platform: str):
    platforms = {
        "reddit": "📣 Share on Reddit coming soon!",
        "x": "🐦 Share on X/Twitter coming soon!",
        "whatsapp": "💬 Share on WhatsApp coming soon!"
    }
    await ctx.send(platforms.get(platform.lower(), "❌ Unknown platform."))

# === Auto-loop Play ===
@tasks.loop(minutes=30)
async def auto_loop():
    for link in shared_links:
        result = auto_play_game(link)

@bot.command()
async def addlink(ctx, link: str):
    shared_links.append(link)
    await ctx.send("✅ Link added to auto-play list.")

@bot.command()
async def loop(ctx):
    if not auto_loop.is_running():
        auto_loop.start()
        await ctx.send("🔁 Auto-loop started every 30 minutes.")
    else:
        await ctx.send("🔁 Auto-loop is already running.")

# === Scheduled DMs to Users ===
@tasks.loop(hours=6)
async def send_scheduled_dms():
    for user_id in user_stats:
        try:
            user = await bot.fetch_user(int(user_id))
            await user.send("🎁 Reminder: Use `!claim <link>` to win more Temu/SHEIN rewards!")
        except Exception:
            continue

# === Setup Bot + Event Hook ===
def setup_bot():
    @bot.event
    async def on_ready():
        print(f"✅ Logged in as {bot.user}")
        if not send_scheduled_dms.is_running():
            send_scheduled_dms.start()
    return bot
