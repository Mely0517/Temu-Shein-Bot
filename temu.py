import discord
from discord.ext import commands
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import asyncio
import time
import os

# Helper: Get headless browser for Render
def get_browser():
    options = uc.ChromeOptions()
    options.binary_location = "/usr/bin/google-chrome"  # Render Chrome path
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0")
    return uc.Chrome(options=options)

# Discord bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Track active auto loops per game
game_loops = {
    "farm": False,
    "fish": False,
    "stack": False,
    "spin": False,
    "gift": False,
    "shein5": False,
    "shein10": False,
}

loop_tasks = {}

# --- Temu Game Commands ---

async def play_generic_game(ctx, link: str, keywords: list, game_name: str):
    await ctx.send(f"🎮 Starting {game_name}...")
    try:
        browser = get_browser()
        browser.get(link)
        await asyncio.sleep(8)
        buttons = browser.find_elements(By.TAG_NAME, "button")
        clicked = False
        for btn in buttons:
            text = btn.text.lower()
            if any(keyword in text for keyword in keywords):
                btn.click()
                clicked = True
                await ctx.send(f"✅ Clicked '{btn.text}'")
                await asyncio.sleep(2)
        if not clicked:
            await ctx.send(f"⚠️ No action buttons found or already done in {game_name}.")
        browser.quit()
    except Exception as e:
        await ctx.send(f"❌ {game_name} error: {e}")

@bot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def farm(ctx, link: str):
    await play_generic_game(ctx, link, ["water", "harvest", "grow", "start"], "Farmland")

@bot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def fish(ctx, link: str):
    await play_generic_game(ctx, link, ["fish", "catch"], "Fishland")

@bot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def stack(ctx, link: str):
    await play_generic_game(ctx, link, ["stack", "tap"], "Stack")

@bot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def spin(ctx, link: str):
    await play_generic_game(ctx, link, ["spin", "start"], "Spin")

@bot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def gift(ctx, link: str):
    await play_generic_game(ctx, link, ["gift", "claim"], "5-Gift Game")

@bot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def claim(ctx, link: str):
    """Claim Temu invite link"""
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

# --- SHEIN Commands ---

@bot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def shein_claim(ctx, link: str):
    """Claim SHEIN invite or 5 free items"""
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

@bot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def shein_10free(ctx, link: str):
    """Claim SHEIN 10 Free Items"""
    await ctx.send("🎊 Starting SHEIN 10 Free Items claim...")
    try:
        browser = get_browser()
        browser.get(link)
        await asyncio.sleep(6)
        # Try multiple clicks & steps for 10 free items
        try:
            # Customize for 10 free items flow - adjust as needed
            buttons = browser.find_elements(By.TAG_NAME, "button")
            for btn in buttons:
                text = btn.text.lower()
                if "claim" in text or "receive" in text or "confirm" in text:
                    btn.click()
                    await asyncio.sleep(2)
            await ctx.send("✅ Attempted 10 Free Items claim!")
        except Exception:
            await ctx.send("⚠️ Some buttons may be missing, but page was processed.")
        browser.quit()
    except Exception as e:
        await ctx.send(f"❌ SHEIN 10 Free Items error: {e}")

# --- Auto-loop ---

async def auto_loop(ctx, game: str, link: str, interval=300):
    await ctx.send(f"⏲️ Auto-loop started for {game} every {interval} seconds.")
    try:
        while game_loops[game]:
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
            elif game == "shein_claim":
                await shein_claim(ctx, link)
            elif game == "shein_10free":
                await shein_10free(ctx, link)
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
    game = game.lower()
    if game not in game_loops:
        await ctx.send("❌ Invalid game name. Use farm, fish, stack, spin, gift, shein_claim, shein_10free.")
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
    game = game.lower()
    if game not in game_loops or not game_loops[game]:
        await ctx.send(f"⚠️ No running auto-loop for {game}.")
        return
    game_loops[game] = False
    task = loop_tasks.get(game)
    if task:
        task.cancel()
    await ctx.send(f"🛑 Auto-loop stopped for {game}.")

# --- On Ready ---

@bot.event
async def on_ready():
    print(f"🤖 Bot online as {bot.user}")
    print("✅ Ready for Temu & SHEIN commands!")

# --- Run bot ---

if __name__ == "__main__":
    TOKEN = os.getenv("DISCORD_TOKEN")
    if not TOKEN:
        print("❌ ERROR: DISCORD_TOKEN environment variable not set.")
        exit(1)
    bot.run(TOKEN)
