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
from datetime import datetime, timedelta

# === Globals ===
shared_links = []
item_tracker = []
user_rewards = {}  # Multi-user rewards tracking
user_dms_schedule = {}  # Scheduled DM times

REWARDS_DB_FILE = "rewards.json"

# === Load/Save Rewards DB ===
def load_rewards_db():
    global user_rewards
    if os.path.exists(REWARDS_DB_FILE):
        with open(REWARDS_DB_FILE, "r") as f:
            user_rewards = json.load(f)
    else:
        user_rewards = {}

def save_rewards_db():
    with open(REWARDS_DB_FILE, "w") as f:
        json.dump(user_rewards, f, indent=4)

# === Headless Chrome Setup for Render ===
def get_browser():
    options = uc.ChromeOptions()
    options.binary_location = "/usr/bin/google-chrome"
    options.add_argument("--headless=new")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")
    return uc.Chrome(options=options)

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

# === Auto-play Handler ===
def auto_play_game(link, user_id):
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
        for i in range(5):
            if click_buttons(driver, ["Go", "Play", "Invite", "Collect", "Get"]):
                success = True
            time.sleep(random.uniform(1.5, 3.5))

        title = driver.title
        driver.quit()

        # Track user rewards
        if str(user_id) not in user_rewards:
            user_rewards[str(user_id)] = []
        user_rewards[str(user_id)].append({
            "link": link,
            "title": title,
            "type": game_type,
            "time": datetime.utcnow().isoformat()
        })
        save_rewards_db()

        # Track globally for leaderboard
        item_tracker.append({"user": user_id, "link": link, "title": title, "type": game_type, "time": datetime.utcnow().isoformat()})

        if success:
            return f"✅ Played {game_type} | {title}"
        else:
            return f"⚠️ Couldn’t find a button, but page opened."

    except Exception as e:
        return f"❌ Error: {str(e)}"

# === Game Detectors ===
def detect_temu_game(link):
    if "fish" in link:
        return "Fishland"
    if "farm" in link:
        return "Farm"
    if "stack" in link:
        return "Stack"
    if "spin" in link:
        return "Spin"
    if "gift" in link:
        return "5-Gift Game"
    return "Temu Game"

def detect_shein_game(link):
    if "10 free items" in link or re.search(r"4vv\w+", link):
        return "10 Free Items"
    if "50" in link:
        return "$50 Off Game"
    if "freebie" in link or "gift" in link:
        return "Free Gift Grab"
    if "1000" in link:
        return "$1000 Prize"
    return "SHEIN Game"

# === Platform Sharing Placeholder ===
async def share_to_platforms(message):
    # Here you can integrate API calls or webhooks to share message to Reddit, X (Twitter), WhatsApp, etc.
    # For now, just print or log
    print(f"Sharing to platforms: {message}")

# === Core Command: !claim <link> ===
async def claim_command(ctx, link: str):
    await ctx.send("🔄 Processing link...")
    result = auto_play_game(link, ctx.author.id)
    await ctx.send(result)
    await share_to_platforms(f"{ctx.author} just played: {link}")

# === Commands Setup ===
def setup_bot(bot):
    load_rewards_db()

    @bot.command()
    async def claim(ctx, link: str):
        await claim_command(ctx, link)

    @bot.command()
    async def farm(ctx): await claim_command(ctx, "https://temu.com/s/farm-invite-link")
    @bot.command()
    async def fish(ctx): await claim_command(ctx, "https://temu.com/s/fishland-invite-link")
    @bot.command()
    async def stack(ctx): await claim_command(ctx, "https://temu.com/s/stack-invite-link")
    @bot.command()
    async def spin(ctx): await claim_command(ctx, "https://temu.com/s/spin-invite-link")
    @bot.command()
    async def gift(ctx): await claim_command(ctx, "https://temu.com/s/5-gift-invite-link")

    @bot.command()
    async def shein(ctx): await claim_command(ctx, "https://onelink.shein.com/15/your-shein-game-link")

    # Show recent claimed items for user
    @bot.command()
    async def myitems(ctx):
        uid = str(ctx.author.id)
        rewards = user_rewards.get(uid, [])
        if not rewards:
            await ctx.send("🪣 No items claimed yet.")
        else:
            msg = "\n".join([f"{r['type']} - {r['title']} ({r['time']})" for r in rewards[-10:]])
            await ctx.send(f"📦 Your recent claimed items:\n{msg}")

    # Leaderboard command
    @bot.command()
    async def leaderboard(ctx):
        # Count rewards per user
        counts = {}
        for uid, rewards in user_rewards.items():
            counts[uid] = len(rewards)
        # Sort descending
        sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        # Format message top 10
        msg = "🏆 Leaderboard - Top Claimers:\n"
        for i, (uid, count) in enumerate(sorted_counts[:10], 1):
            user = await bot.fetch_user(int(uid))
            msg += f"{i}. {user.name} - {count} items\n"
        await ctx.send(msg)

    # Add link for auto-loop playing
    @bot.command()
    async def addlink(ctx, link: str):
        shared_links.append(link)
        await ctx.send("✅ Link added to auto-play list.")

    # Start auto-loop every 30 min
    @tasks.loop(minutes=30)
    async def auto_loop():
        for link in shared_links:
            for uid in user_rewards.keys():
                result = auto_play_game(link, uid)
                print(result)

    @bot.command()
    async def loop(ctx):
        auto_loop.start()
        await ctx.send("🔁 Auto-loop started every 30 minutes.")

    # Scheduled DMs to users
    @tasks.loop(minutes=1)
    async def send_scheduled_dms():
        now = datetime.utcnow()
        for user_id, send_time in list(user_dms_schedule.items()):
            if now >= send_time:
                user = await bot.fetch_user(int(user_id))
                if user:
                    rewards = user_rewards.get(str(user_id), [])
                    msg = f"📢 Your reward summary:\nTotal items claimed: {len(rewards)}"
                    await user.send(msg)
                # Schedule next DM 24h later
                user_dms_schedule[user_id] = now + timedelta(hours=24)

    @bot.command()
    async def schedule_dm(ctx, hour: int, minute: int):
        # Schedule DM to user at next hour:minute UTC
        now = datetime.utcnow()
        send_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if send_time < now:
            send_time += timedelta(days=1)
        user_dms_schedule[str(ctx.author.id)] = send_time
        await ctx.send(f"✅ Scheduled daily DM at {hour:02d}:{minute:02d} UTC.")

    # Auto-join teams (simplified example)
    @bot.command()
    async def join_team(ctx, team_name: str):
        # Normally here you'd automate joining a team on the platform via browser or API
        await ctx.send(f"✅ Attempting to join team '{team_name}'. (Feature requires platform integration)")

    # Start DM scheduler
    send_scheduled_dms.start()

