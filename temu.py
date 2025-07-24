import discord
from discord.ext import commands
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time
import os

# Set up Discord bot with correct intent
intents = discord.Intents.default()
intents.message_content = True  # ✅ This is what lets the bot read !commands
bot = commands.Bot(command_prefix="!", intents=intents)

# === !claim Command ===
@bot.command()
async def claim(ctx, link: str):
    print("📥 Received claim command")
    await ctx.send("🚀 Visiting your Temu link...")

    try:
        options = uc.ChromeOptions()
        options.binary_location = "/usr/bin/google-chrome"
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("user-agent=Mozilla/5.0")

        browser = uc.Chrome(options=options)
        browser.get(link)

        print(f"🔗 Opened link: {link}")
        time.sleep(6)  # Give page time to load

        try:
            btn = browser.find_element(By.XPATH, "//button[contains(text(), 'Accept') or contains(text(), 'Join') or contains(text(), 'Open')]")
            btn.click()
            await ctx.send("✅ Successfully clicked the Temu link!")
            print("✅ Button clicked.")
        except Exception as e:
            await ctx.send("⚠️ Couldn’t find the Accept/Join button, but the page was opened.")
            print(f"⚠️ Button not found: {e}")

        browser.quit()
        print("🧹 Browser closed.")

    except Exception as e:
        await ctx.send(f"❌ Error: {e}")
        print(f"❌ Exception: {e}")

# === !farm Command ===
@bot.command()
async def farm(ctx, link: str):
    print("🚜 Starting Farmland automation")
    await ctx.send("🌾 Loading your Farmland...")

    try:
        options = uc.ChromeOptions()
        options.binary_location = "/usr/bin/google-chrome"
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("user-agent=Mozilla/5.0")

        browser = uc.Chrome(options=options)
        browser.get(link)
        time.sleep(8)

        try:
            # Look for buttons like "Water", "Harvest", "Grow"
            buttons = browser.find_elements(By.XPATH, "//button")
            clicked = False

            for btn in buttons:
                text = btn.text.lower()
                if any(word in text for word in ["water", "harvest", "grow", "start"]):
                    btn.click()
                    clicked = True
                    await ctx.send(f"✅ Clicked '{btn.text}' in Farmland!")
                    print(f"✅ Clicked button: {btn.text}")
                    time.sleep(2)

            if not clicked:
                await ctx.send("⚠️ No action buttons found. Game may already be completed or link is invalid.")
                print("⚠️ No clickable buttons.")

        except Exception as e:
            await ctx.send(f"❌ Failed to interact with Farmland: {e}")
            print(f"❌ Interaction error: {e}")

        browser.quit()
        print("🧹 Browser closed.")

    except Exception as e:
        await ctx.send(f"❌ Browser error: {e}")
        print(f"❌ Browser launch error: {e}")

# === On Ready ===
@bot.event
async def on_ready():
    print(f"🤖 Bot online as {bot.user}")
    print("✅ Ready to accept Temu links and play Farmland!")
