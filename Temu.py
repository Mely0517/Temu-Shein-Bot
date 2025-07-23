import discord
from discord.ext import commands
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time
import os

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.messages = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.command()
async def claim(ctx, link: str):
    await ctx.send(f"🚀 Visiting your Temu link...")

    try:
        options = uc.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("user-agent=Mozilla/5.0")

        browser = uc.Chrome(options=options)
        browser.get(link)

        time.sleep(6)  # wait for Temu page to load

        try:
            btn = browser.find_element(By.XPATH, "//button[contains(text(), 'Accept') or contains(text(), 'Join') or contains(text(), 'Open')]")
            btn.click()
            await ctx.send("✅ Successfully clicked the Temu link!")
        except:
            await ctx.send("⚠️ Couldn’t find the Accept/Join button, but the page was opened.")

        browser.quit()

    except Exception as e:
        await ctx.send(f"❌ Error: {e}")

@bot.event
async def on_ready():
    print(f"🤖 Bot online as {bot.user}")
    print("Ready to auto-accept Temu links!")

