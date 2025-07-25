import discord
from discord.ext import commands
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time
import os

# === Discord Bot Setup ===
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# === Chrome Browser Setup ===
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

# === !claim ===
@bot.command()
async def claim(ctx, link: str):
    print("📥 Claiming Temu invite")
    await ctx.send("🚀 Visiting your Temu link...")

    try:
        browser = get_browser()
        browser.get(link)
        time.sleep(6)

        try:
            btn = browser.find_element(By.XPATH, "//button[contains(text(), 'Accept') or contains(text(), 'Join') or contains(text(), 'Open')]")
            btn.click()
            await ctx.send("✅ Successfully clicked the Temu link!")
        except:
            await ctx.send("⚠️ Couldn't find Accept/Join button, but link opened.")

        browser.quit()

    except Exception as e:
        await ctx.send(f"❌ Error: {e}")

# === !farm ===
@bot.command()
async def farm(ctx, link: str):
    print("🌾 Automating Farmland")
    await ctx.send("🌱 Visiting your Farmland...")

    try:
        browser = get_browser()
        browser.get(link)
        time.sleep(8)

        clicked = False
        for btn in browser.find_elements(By.XPATH, "//button"):
            text = btn.text.lower()
            if any(word in text for word in ["water", "harvest", "grow", "start"]):
                btn.click()
                clicked = True
                await ctx.send(f"✅ Clicked '{btn.text}' in Farmland!")
                time.sleep(2)

        if not clicked:
            await ctx.send("⚠️ No buttons found. Game might be complete or not loaded.")

        browser.quit()

    except Exception as e:
        await ctx.send(f"❌ Farmland error: {e}")

# === !fish ===
@bot.command()
async def fish(ctx, link: str):
    print("🐟 Automating Fishland")
    await ctx.send("🐠 Visiting your Fishland...")

    try:
        browser = get_browser()
        browser.get(link)
        time.sleep(8)

        clicked = False
        for btn in browser.find_elements(By.XPATH, "//button"):
            text = btn.text.lower()
            if any(word in text for word in ["feed", "help", "start", "claim", "collect"]):
                btn.click()
                clicked = True
                await ctx.send(f"✅ Clicked '{btn.text}' in Fishland!")
                time.sleep(2)

        if not clicked:
            await ctx.send("⚠️ No Fishland actions found.")

        browser.quit()

    except Exception as e:
        await ctx.send(f"❌ Fishland error: {e}")

# === !stack ===
@bot.command()
async def stack(ctx, link: str):
    print("🧱 Automating Stack Game")
    await ctx.send("🧱 Visiting your Stack Game...")

    try:
        browser = get_browser()
        browser.get(link)
        time.sleep(8)

        clicked = False
        for btn in browser.find_elements(By.XPATH, "//button"):
            text = btn.text.lower()
            if any(word in text for word in ["start", "play", "drop", "stack", "continue"]):
                btn.click()
                clicked = True
                await ctx.send(f"✅ Clicked '{btn.text}' in Stack!")
                time.sleep(2)

        if not clicked:
            await ctx.send("⚠️ No Stack game buttons found.")

        browser.quit()

    except Exception as e:
        await ctx.send(f"❌ Stack error: {e}")

# === !spin ===
@bot.command()
async def spin(ctx, link: str):
    print("🎰 Automating Spin Game")
    await ctx.send("🎰 Visiting your Spin Game...")

    try:
        browser = get_browser()
        browser.get(link)
        time.sleep(8)

        clicked = False
        for btn in browser.find_elements(By.XPATH, "//button"):
            text = btn.text.lower()
            if any(word in text for word in ["spin", "start", "play", "go", "try again"]):
                btn.click()
                clicked = True
                await ctx.send(f"✅ Clicked '{btn.text}' in Spin Game!")
                time.sleep(2)

        if not clicked:
            await ctx.send("⚠️ No Spin actions found.")

        browser.quit()

    except Exception as e:
        await ctx.send(f"❌ Spin error: {e}")

# === !gifts ===
@bot.command()
async def gifts(ctx, link: str):
    print("🎁 Automating 5-Gift Game")
    await ctx.send("🎁 Visiting your 5-Gift Game...")

    try:
        browser = get_browser()
        browser.get(link)
        time.sleep(8)

        clicked = False
        for btn in browser.find_elements(By.XPATH, "//button"):
            text = btn.text.lower()
            if any(word in text for word in ["open", "pack", "accept", "choose", "claim"]):
                btn.click()
                clicked = True
                await ctx.send(f"✅ Clicked '{btn.text}' in 5-Gift Game!")
                time.sleep(2)

        if not clicked:
            await ctx.send("⚠️ No 5-Gift actions found.")

        browser.quit()

    except Exception as e:
        await ctx.send(f"❌ Gift error: {e}")

# === Bot Ready ===
@bot.event
async def on_ready():
    print(f"🤖 Bot online as {bot.user}")
    print("✅ Ready for Temu games: claim, farm, fish, stack, spin, gifts!")

