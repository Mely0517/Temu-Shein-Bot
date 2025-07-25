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
    options.binary_location = "/usr/bin/google-chrome"  # Adjust if needed on your host
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0")
    return uc.Chrome(options=options)

# ---------------- Discord bot setup ----------------

intents = discord.Intents.default()
intents.message_content = True  # Required for commands
bot = commands.Bot(command_prefix="!", intents=intents)

# ----------- Referral links and auto-sharing setup -----------

# Replace these with your actual referral links
REFERRAL_LINKS = {
    "shein": "https://onelink.shein.com/15/4vqj870ifsi6",
    "temu": "https://temu.link/your-referral-code"
}

# Replace with your actual Discord channel ID (int) where links will be shared
AUTO_SHARE_CHANNEL_ID = 123456789012345678

auto_sharing = False

@tasks.loop(minutes=60)
async def share_referral_links():
    channel = bot.get_channel(AUTO_SHARE_CHANNEL_ID)
    if channel:
        message = (
            "🌟 Support me by clicking these referral links and claim your free items!\n\n"
            f"SHEIN: {REFERRAL_LINKS['shein']}\n"
            f"Temu: {REFERRAL_LINKS['temu']}\n\n"
            "Thanks for helping out! 🙏"
        )
        await channel.send(message)
    else:
        print(f"Channel ID {AUTO_SHARE_CHANNEL_ID} not found for auto-sharing.")

@bot.command()
async def startsharing(ctx):
    global auto_sharing
    if auto_sharing:
        await ctx.send("⚠️ Auto-sharing is already running.")
    else:
        auto_sharing = True
        share_referral_links.start()
        await ctx.send(f"✅ Started auto-sharing referral links every hour in <#{AUTO_SHARE_CHANNEL_ID}>.")

@bot.command()
async def stopsharing(ctx):
    global auto_sharing
    if not auto_sharing:
        await ctx.send("⚠️ Auto-sharing is not running.")
    else:
        auto_sharing = False
        share_referral_links.cancel()
        await ctx.send("🛑 Stopped auto-sharing referral links.")

# ----------- Game loops tracking -----------

game_loops = {
    "farm": False,
    "fish": False,
    "stack": False,
    "spin": False,
    "gift": False,
}

loop_tasks = {}

# ----------- Temu + SHEIN Game Commands -------------

@bot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
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

@bot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def shein_10free(ctx, link: str):
    """Claim SHEIN 10 Free Items game"""
    await ctx.send("🎊 Starting SHEIN 10 Free Items claim...")
    try:
        browser = get_browser()
        browser.get(link)
        await asyncio.sleep(8)
        # Add custom steps here for 10 free items if needed
        try:
            btn = browser.find_element(By.XPATH, "//button[contains(text(), 'Claim') or contains(text(), 'Get')]")
            btn.click()
            await ctx.send("✅ Clicked claim button for 10 Free Items!")
        except Exception:
            await ctx.send("⚠️ Couldn’t find claim button for 10 Free Items.")
        browser.quit()
    except Exception as e:
        await ctx.send(f"❌ SHEIN 10 Free Items error: {e}")

# ----------- Auto-loop background tasks -----------

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
    print("✅ Ready to accept commands and auto-share referral links!")

# ----------- Run bot -----------

if __name__ == "__main__":
    TOKEN = os.getenv("DISCORD_TOKEN")
    if not TOKEN:
        print("❌ ERROR: DISCORD_TOKEN env var not set.")
        exit()
    bot.run(TOKEN)