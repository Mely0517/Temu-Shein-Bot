import discord
from discord.ext import commands, tasks
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import asyncio
import os
import json
from datetime import datetime

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ------------- Headless Browser Setup -------------
def get_browser():
    options = uc.ChromeOptions()
    options.binary_location = "/usr/bin/google-chrome"
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return uc.Chrome(options=options)

# ------------- Auto Save Rewards -------------
REWARDS_FILE = "rewards.json"

def log_reward(user, platform, game, amount="1"):
    data = {}
    if os.path.exists(REWARDS_FILE):
        with open(REWARDS_FILE, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                pass
    user_id = str(user.id)
    if user_id not in data:
        data[user_id] = {"username": user.name, "rewards": []}
    data[user_id]["rewards"].append({
        "platform": platform,
        "game": game,
        "amount": amount,
        "timestamp": str(datetime.utcnow())
    })
    with open(REWARDS_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ------------- Temu Claim Gift Command -------------
@bot.command(name="claim")
async def claim(ctx):
    await ctx.send("🎁 Claiming your Temu gift now...")
    try:
        browser = get_browser()
        browser.get("https://temu.com/s/your-temu-invite-link")
        await asyncio.sleep(5)
        browser.quit()
        log_reward(ctx.author, "Temu", "gift")
        await ctx.send("✅ Gift claimed successfully!")
    except Exception as e:
        await ctx.send(f"❌ Error claiming gift: {e}")

# ------------- Leaderboard -------------
@bot.command(name="leaderboard")
async def leaderboard(ctx):
    if not os.path.exists(REWARDS_FILE):
        await ctx.send("No rewards have been claimed yet.")
        return
    with open(REWARDS_FILE, "r") as f:
        data = json.load(f)
    leaderboard_data = [(info["username"], len(info["rewards"])) for uid, info in data.items()]
    leaderboard_data.sort(key=lambda x: x[1], reverse=True)
    leaderboard_msg = "\n".join([f"🥇 {name}: {count} rewards" for name, count in leaderboard_data[:10]])
    await ctx.send(f"🏆 **Leaderboard:**\n{leaderboard_msg}")

# ------------- Scheduled DMs -------------
@tasks.loop(hours=24)
async def send_scheduled_dms():
    await bot.wait_until_ready()
    for guild in bot.guilds:
        for member in guild.members:
            if not member.bot:
                try:
                    await member.send("🎯 Don’t forget to share your Temu/SHEIN links today for more rewards!")
                except:
                    continue

# ------------- Setup Function -------------
def setup_bot():
    send_scheduled_dms.start()
