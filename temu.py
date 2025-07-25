import discord
from discord.ext import commands, tasks
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import asyncio
import time
import os

# ----------- Helper: Get headless browser configured for Render -----------

def get_browser():
    options = uc.ChromeOptions()
    # Adjust this path if needed based on your environment
    options.binary_location = "/usr/bin/google-chrome"  # Render’s Chrome path
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0")
    return uc.Chrome(options=options)

# ---------------- Discord bot setup ----------------

intents = discord.Intents.default()
intents.message_content = True  # Required for commands to work on latest discord.py versions
bot = commands.Bot(command_prefix="!", intents=intents)

# ----------- Game loops tracking -----------

game_loops = {
    "farm": False,
    "fish": False,
    "stack": False,
    "spin": False,
    "gift": False,
}

loop_tasks = {}

# ----------- Core commands -------------

@bot.command()
@commands.cooldown(1, 10, commands.BucketType.user)  # 10 seconds cooldown per user
async def claim(ctx, link: str):
    """Claim a Temu invite link"""
    await ctx.send("🚀 Opening Temu invite link...")
    try:
        browser = get_browser()
        browser.get(link)
        await asyncio.sleep(6)
        try:
            btn = browser.find_element(By.XPATH, "//button[contains(text(), 'Accept') or contains(text(), 'Join') or contains(text(), 'Open')]")
            btn.click()
            await ctx.send("✅ Successfully clicked the Temu invite!")
        except Exception:
            await ctx.send("⚠️ Button not found but page opened.")
        browser.quit()
    except Exception as e:
        await ctx.send(f"❌ Temu error: {e}")

@bot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def farm(ctx, link: str):
    """Play Temu Farmland game once"""
    await ctx.send("🌾 Starting Farmland...")
    try:
        browser = get_browser()
        browser.get(link)
        await asyncio.sleep(8)
        buttons = browser.find_elements(By.TAG_NAME, "button")
        clicked = False
        for btn in buttons:
            text = btn.text.lower()
            if any(word in text for word in ["water", "harvest", "grow", "start"]):
                btn.click()
                clicked = True
                await ctx.send(f"✅ Clicked '{btn.text}'")
                await asyncio.sleep(2)
        if not clicked:
            await ctx.send("⚠️ No action buttons found or already done.")
        browser.quit()
    except Exception as e:
        await ctx.send(f"❌ Farmland error: {e}")

@bot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def fish(ctx, link: str):
    """Play Temu Fishland game once"""
    await ctx.send("🐟 Starting Fishland...")
    try:
        browser = get_browser()
        browser.get(link)
        await asyncio.sleep(8)
        # Example fish game clicks - adjust XPath as needed for actual Fishland UI
        buttons = browser.find_elements(By.TAG_NAME, "button")
        clicked = False
        for btn in buttons:
            text = btn.text.lower()
            if "fish" in text or "catch" in text:
                btn.click()
                clicked = True
                await ctx.send(f"✅ Clicked '{btn.text}'")
                await asyncio.sleep(2)
        if not clicked:
            await ctx.send("⚠️ No fishing buttons found or already done.")
        browser.quit()
    except Exception as e:
        await ctx.send(f"❌ Fishland error: {e}")

@bot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def stack(ctx, link: str):
    """Play Temu Stack game once"""
    await ctx.send("🧱 Starting Stack...")
    try:
        browser = get_browser()
        browser.get(link)
        await asyncio.sleep(8)
        # Example Stack clicks - adjust XPath as needed
        buttons = browser.find_elements(By.TAG_NAME, "button")
        clicked = False
        for btn in buttons:
            text = btn.text.lower()
            if "stack" in text or "tap" in text:
                btn.click()
                clicked = True
                await ctx.send(f"✅ Clicked '{btn.text}'")
                await asyncio.sleep(2)
        if not clicked:
            await ctx.send("⚠️ No stack buttons found or already done.")
        browser.quit()
    except Exception as e:
        await ctx.send(f"❌ Stack error: {e}")

@bot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def spin(ctx, link: str):
    """Play Temu Spin game once"""
    await ctx.send("🎡 Starting Spin...")
    try:
        browser = get_browser()
        browser.get(link)
        await asyncio.sleep(8)
        buttons = browser.find_elements(By.TAG_NAME, "button")
        clicked = False
        for btn in buttons:
            text = btn.text.lower()
            if "spin" in text or "start" in text:
                btn.click()
                clicked = True
                await ctx.send(f"✅ Clicked '{btn.text}'")
                await asyncio.sleep(2)
        if not clicked:
            await ctx.send("⚠️ No spin buttons found or already done.")
        browser.quit()
    except Exception as e:
        await ctx.send(f"❌ Spin error: {e}")

@bot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def gift(ctx, link: str):
    """Play Temu 5-Gift game once"""
    await ctx.send("🎁 Starting 5-Gift game...")
    try:
        browser = get_browser()
        browser.get(link)
        await asyncio.sleep(8)
        # Example gift clicks - adjust XPath as needed
        buttons = browser.find_elements(By.TAG_NAME, "button")
        clicked = False
        for btn in buttons:
            text = btn.text.lower()
            if "gift" in text or "claim" in text:
                btn.click()
                clicked = True
                await ctx.send(f"✅ Clicked '{btn.text}'")
                await asyncio.sleep(2)
        if not clicked:
            await ctx.send("⚠️ No gift buttons found or already done.")
        browser.quit()
    except Exception as e:
        await ctx.send(f"❌ 5-Gift error: {e}")

@bot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def shein_claim(ctx, link: str):
    """Claim SHEIN invite or gift link"""
    await ctx.send("🎉 Starting SHEIN claim...")
    try:
        browser = get_browser()
        browser.get(link)
        await asyncio.sleep(6)
        try:
            btn = browser.find_element(By.XPATH, "//button[contains(text(), 'Accept') or contains(text(), 'Claim') or contains(text(), 'Open')]")
            btn.click()
            await ctx.send("✅ Successfully claimed SHEIN gift!")
        except Exception:
            await ctx.send("⚠️ Couldn’t find claim button but page opened.")
        browser.quit()
    except Exception as e:
        await ctx.send(f"❌ SHEIN error: {e}")

# ----------- Auto-loop background tasks -----------

async def auto_loop(ctx, game: str, link: str, interval=300):
    await ctx.send(f"⏲️ Auto-loop started for {game} every {interval} seconds.")
    try:
        while game_loops[game]:
            # Call the matching command function
            if game == "farm":
                await farm(ctx, link)
            elif game == "fish":
                await fish(ctx, link)
            elif game == "stack":
                await stack(ctx, link)
            elif game == "spin":
                await spin(ctx, link)
            elif game == "gift":
                await gift(ctx, link)
            else:
                await ctx.send(f"⚠️ Unknown game: {game}")
                break
            await asyncio.sleep(interval)
    except asyncio.CancelledError:
        await ctx.send(f"⏹️ Auto-loop stopped for {game}.")
    except Exception as e:
        await ctx.send(f"❌ Auto-loop error for {game}: {e}")

@bot.command()
async def start(ctx, game: str, link: str, interval: int = 300):
    """Start auto-loop for a game every [interval] seconds"""
    game = game.lower()
    if game not in game_loops:
        await ctx.send("❌ Invalid game name. Use farm, fish, stack, spin, gift.")
        return
    if game_loops[game]:
        await ctx.send(f"⚠️ Auto-loop for {game} already running.")
        return
    game_loops[game] = True
    task = bot.loop.create_task(auto_loop(ctx, game, link, interval))
    loop_tasks[game] = task
    await ctx.send(f"✅ Auto-loop started for {game} every {interval} seconds.")

@bot.command()
async def stop(ctx, game: str):
    """Stop auto-loop for a game"""
    game = game.lower()
    if game not in game_loops or not game_loops[game]:
        await ctx.send(f"⚠️ No running auto-loop for {game}.")
        return
    game_loops[game] = False
    task = loop_tasks.get(game)
    if task:
        task.cancel()
    await ctx.send(f"🛑 Auto-loop stopped for {game}.")

# ----------- On Ready -----------

@bot.event
async def on_ready():
    print(f"🤖 Bot online as {bot.user}")
    print("✅ Ready to accept commands for Temu & SHEIN games!")

# ----------- Run bot -----------

if __name__ == "__main__":
    TOKEN = os.getenv("DISCORD_TOKEN")
    if not TOKEN:
        print("❌ ERROR: DISCORD_TOKEN env var not set.")
        exit