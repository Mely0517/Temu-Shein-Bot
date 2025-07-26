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
def auto_play_game(link):
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
        item_tracker.append({"link": link, "title": title, "type": game_type})
        driver.quit()

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
    if "10 free items" in link or "4vv" in link:
        return "10 Free Items"
    if "50" in link:
        return "$50 Off Game"
    if "freebie" in link or "gift" in link:
        return "Free Gift Grab"
    if "1000" in link:
        return "$1000 Prize"
    return "SHEIN Game"

# === Core Command: !claim <link> ===
@bot.command()
async def claim(ctx, link: str):
    await ctx.send("🔄 Processing link...")
    result = auto_play_game(link)
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

# === Add SHEIN shortcut examples (optional links) ===
@bot.command()
async def shein(ctx): await claim(ctx, "https://onelink.shein.com/15/your-shein-game-link")

# === Track Claimed Items ===
@bot.command()
async def myitems(ctx):
    if not item_tracker:
        await ctx.send("🪣 No items claimed yet.")
    else:
        msg = "\n".join([f"{item['type']} - {item['title']}" for item in item_tracker[-10:]])
        await ctx.send(f"📦 Recent claimed:\n{msg}")

# === Smart Auto-Looping ===
@tasks.loop(minutes=30)
async def auto_loop():
    if shared_links:
        for link in shared_links:
            result = auto_play_game(link)
            print(result)

@bot.command()
async def addlink(ctx, link: str):
    shared_links.append(link)
    await ctx.send("✅ Link added to auto-play list.")

@bot.command()
async def loop(ctx):
    auto_loop.start()
    await ctx.send("🔁 Auto-loop started every 30 minutes.")

def setup_bot():
    return bot
