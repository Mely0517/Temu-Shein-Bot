import discord
from discord.ext import commands
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time
import os

# === Bot Setup ===
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# === Headless Browser Setup ===
def get_browser():
    options = uc.ChromeOptions()
    options.binary_location = "/opt/render/project/.render/chrome/opt/google/chrome"  # Chrome path for Render
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0")
    return uc.Chrome(options=options)

# === TEMU Commands ===
@bot.command()
async def claim(ctx, link: str):
    await ctx.send("🚀 Visiting your Temu link...")
    try:
        browser = get_browser()
        browser.get(link)
        time.sleep(6)
        try:
            btn = browser.find_element(By.XPATH, "//button[contains(text(), 'Accept') or contains(text(), 'Join') or contains(text(), 'Open')]")
            btn.click()
            await ctx.send("✅ Clicked the Temu button!")
        except:
            await ctx.send("⚠️ Button not found, but page opened.")
        browser.quit()
    except Exception as e:
        await ctx.send(f"❌ Temu error: {e}")

@bot.command()
async def farm(ctx, link: str):
    await ctx.send("🌾 Loading Temu Farmland...")
    try:
        browser = get_browser()
        browser.get(link)
        time.sleep(8)
        clicked = False
        for btn in browser.find_elements(By.XPATH, "//button"):
            text = btn.text.lower()
            if any(w in text for w in ["water", "harvest", "grow", "start"]):
                btn.click()
                await ctx.send(f"✅ Clicked '{btn.text}' in Farmland!")
                clicked = True
                time.sleep(2)
        if not clicked:
            await ctx.send("⚠️ No Farmland buttons found.")
        browser.quit()
    except Exception as e:
        await ctx.send(f"❌ Farmland error: {e}")

@bot.command()
async def fish(ctx, link: str):
    await ctx.send("🐟 Loading Temu Fishland...")
    try:
        browser = get_browser()
        browser.get(link)
        time.sleep(8)
        clicked = False
        for btn in browser.find_elements(By.XPATH, "//button"):
            text = btn.text.lower()
            if any(w in text for w in ["feed", "help", "start", "collect", "claim"]):
                btn.click()
                await ctx.send(f"✅ Clicked '{btn.text}' in Fishland!")
                clicked = True
                time.sleep(2)
        if not clicked:
            await ctx.send("⚠️ No Fishland buttons found.")
        browser.quit()
    except Exception as e:
        await ctx.send(f"❌ Fishland error: {e}")

@bot.command()
async def stack(ctx, link: str):
    await ctx.send("🧱 Loading Temu Stack game...")
    try:
        browser = get_browser()
        browser.get(link)
        time.sleep(8)
        clicked = False
        for btn in browser.find_elements(By.XPATH, "//button"):
            text = btn.text.lower()
            if any(w in text for w in ["stack", "drop", "start", "continue", "play"]):
                btn.click()
                await ctx.send(f"✅ Clicked '{btn.text}' in Stack game!")
                clicked = True
                time.sleep(2)
        if not clicked:
            await ctx.send("⚠️ No Stack buttons found.")
        browser.quit()
    except Exception as e:
        await ctx.send(f"❌ Stack game error: {e}")

@bot.command()
async def spin(ctx, link: str):
    await ctx.send("🎰 Loading Temu Spin game...")
    try:
        browser = get_browser()
        browser.get(link)
        time.sleep(8)
        clicked = False
        for btn in browser.find_elements(By.XPATH, "//button"):
            text = btn.text.lower()
            if any(w in text for w in ["spin", "play", "start", "go", "try"]):
                btn.click()
                await ctx.send(f"✅ Clicked '{btn.text}' in Spin game!")
                clicked = True
                time.sleep(2)
        if not clicked:
            await ctx.send("⚠️ No Spin buttons found.")
        browser.quit()
    except Exception as e:
        await ctx.send(f"❌ Spin game error: {e}")

@bot.command()
async def gifts(ctx, link: str):
    await ctx.send("🎁 Loading Temu 5-Gift game...")
    try:
        browser = get_browser()
        browser.get(link)
        time.sleep(8)
        clicked = False
        for btn in browser.find_elements(By.XPATH, "//button"):
            text = btn.text.lower()
            if any(w in text for w in ["open", "pack", "accept", "choose", "claim"]):
                btn.click()
                await ctx.send(f"✅ Clicked '{btn.text}' in 5-Gift Game!")
                clicked = True
                time.sleep(2)
        if not clicked:
            await ctx.send("⚠️ No 5-Gift buttons found.")
        browser.quit()
    except Exception as e:
        await ctx.send(f"❌ 5-Gift game error: {e}")

# === SHEIN Command ===
@bot.command()
async def shein_claim(ctx, link: str):
    await ctx.send("🛍️ Visiting your SHEIN link...")
    try:
        browser = get_browser()
        browser.get(link)
        time.sleep(6)
        try:
            btn = browser.find_element(By.XPATH, "//button[contains(text(), 'Accept') or contains(text(), 'Join') or contains(text(), 'Claim') or contains(text(), 'Open')]")
            btn.click()
            await ctx.send("✅ SHEIN link clicked successfully!")
        except:
            await ctx.send("⚠️ Couldn’t find a clickable button, but page was opened.")
        browser.quit()
    except Exception as e:
        await ctx.send(f"❌ SHEIN error: {e}")

# === On Ready ===
@bot.event
async def on_ready():
    print(f"🤖 Bot online as {bot.user}")
    print("✅ Ready to accept Temu & SHEIN links!")