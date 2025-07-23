import discord
from discord.ext import commands
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time
import os

# Set up Discord bot
intents = discord.Intents.default()
intents.messages = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.command()
async def claim(ctx, link: str):
    print("🛠️ Received claim command")
    await ctx.send(f"🚀 Visiting your Temu link...")

    try:
        options = uc.ChromeOptions()
        options.binary_location = "/usr/bin/google-chrome"  # 👈 REQUIRED for Render

        # Safe headless flags for cloud deployment
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("user-agent=Mozilla/5.0")

        # Launch undetected Chrome
        browser = uc.Chrome(options=options)
        browser.get(link)

        print(f"🔗 Opened link: {link}")
        time.sleep(6)  # Give page time to load

        try:
            btn = browser.find_element(By.XPATH, "//button[contains(text(), 'Accept') or contains(text(), 'Join') or contains(text(), 'Open')]")
            btn.click()
            await ctx.send("✅ Successfully clicked the Temu link!")
            print("✅ Button clicked successfully.")
        except Exception as click_error:
            await ctx.send("⚠️ Couldn’t find the Accept/Join button, but the page was opened.")
            print(f"⚠️ Button not found: {click_error}")

        browser.quit()
        print("🧹 Browser closed cleanly.")

    except Exception as e:
        await ctx.send(f"❌ Error: {e}")
        print(f"❌ Exception occurred: {e}")

@bot.event
async def on_ready():
    print(f"🤖 Bot online as {bot.user}")
    print("Ready to auto-accept Temu links!")
