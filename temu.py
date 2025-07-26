import os
import re
import json
import asyncio
import logging
import traceback
from concurrent.futures import ThreadPoolExecutor

import aiohttp
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from discord.ext import tasks

# ----------- Setup logging -----------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("temu-bot")

# ----------- Configurable via environment variables -----------

REFERRAL_LINKS = {
    "shein": os.getenv("SHEIN_REFERRAL_LINK", "https://onelink.shein.com/15/4vqj870ifsi6"),
    "temu": os.getenv("TEMU_REFERRAL_LINK", "https://temu.link/your-referral-code"),
}

AUTO_SHARE_CHANNEL_ID = int(os.getenv("AUTO_SHARE_CHANNEL_ID", "0"))  # Set your Discord channel ID as env var

STATS_FILE = "stats.json"
MAX_CONCURRENT_BROWSERS = int(os.getenv("MAX_CONCURRENT_BROWSERS", "2"))  # limit concurrent browsers to avoid overload

# Semaphore to limit concurrent browsers
browser_semaphore = asyncio.Semaphore(MAX_CONCURRENT_BROWSERS)

game_loops = {"farm": False, "fish": False, "stack": False, "spin": False, "gift": False}
loop_tasks = {}
auto_sharing = False

# Executor for blocking selenium calls
executor = ThreadPoolExecutor(max_workers=MAX_CONCURRENT_BROWSERS)

# ----------- Browser setup for Render -----------

def get_browser():
    options = uc.ChromeOptions()
    # Render Chrome path (adjust if needed)
    options.binary_location = "/opt/render/project/.render/chrome/opt/google/chrome/chrome"
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    # Use a realistic user agent to reduce detection
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/115.0.0.0 Safari/537.36"
    )
    return uc.Chrome(options=options)


# ----------- Stats Helpers -----------

def load_stats():
    if not os.path.exists(STATS_FILE):
        return {}
    with open(STATS_FILE, "r") as f:
        return json.load(f)

def save_stats(data):
    with open(STATS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def record_stat(user_id, game_type):
    stats = load_stats()
    if str(user_id) not in stats:
        stats[str(user_id)] = {"temu": 0, "shein": 0}
    stats[str(user_id)][game_type] += 1
    save_stats(stats)


# ----------- Utility for running blocking code in thread -----------

async def run_in_executor(func, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, lambda: func(*args))


# ----------- Selenium helpers -----------

def wait_for_button(browser, xpaths, timeout=10):
    """Wait until any button matching xpaths is present and return it."""
    wait = WebDriverWait(browser, timeout)
    for xpath in xpaths:
        try:
            btn = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            return btn
        except:
            continue
    return None


# ----------- Headless browser claim/game logic -----------

def browser_claim_link(link, source):
    """
    Blocking function to open a link and click claim/open/join buttons if found.
    Returns tuple (success: bool, message: str)
    """
    browser = None
    try:
        browser = get_browser()
        browser.get(link)

        # Wait for page load (wait for body)
        WebDriverWait(browser, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # Buttons to look for (XPaths)
        button_xpaths = [
            "//button[contains(text(), 'Accept')]",
            "//button[contains(text(), 'Join')]",
            "//button[contains(text(), 'Open')]",
            "//button[contains(text(), 'Claim')]",
            "//button[contains(text(), 'Get')]",
        ]

        btn = wait_for_button(browser, button_xpaths, timeout=12)
        if btn:
            btn.click()
            return True, f"Successfully clicked {source.upper()} claim button!"
        else:
            return False, "No claim/open/join button found on page."
    except Exception as e:
        logger.error(f"Exception in browser_claim_link: {traceback.format_exc()}")
        return False, f"Error during {source.upper()} claim: {e}"
    finally:
        if browser:
            browser.quit()


def browser_run_game(link, game, keywords):
    """
    Blocking function to open game link and click first matching keyword button.
    Returns tuple (clicked: bool, message: str)
    """
    browser = None
    try:
        browser = get_browser()
        browser.get(link)

        # Wait for page load
        WebDriverWait(browser, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        buttons = browser.find_elements(By.TAG_NAME, "button")
        for btn in buttons:
            text = btn.text.lower()
            if any(kw in text for kw in keywords):
                btn.click()
                return True, f"Clicked '{btn.text}' button."
        return False, "No matching action buttons found."
    except Exception as e:
        logger.error(f"Exception in browser_run_game: {traceback.format_exc()}")
        return False, f"Error during {game.title()} game: {e}"
    finally:
        if browser:
            browser.quit()


# ----------- Async wrappers using executor and semaphore -----------

async def run_claim(ctx, link, source):
    await ctx.send(f"🚀 Opening {source.upper()} link...")
    async with browser_semaphore:
        success, msg = await run_in_executor(browser_claim_link, link, source)
    if success:
        await ctx.send(f"✅ {msg}")
        try:
            await ctx.author.send(f"✅ Your {source.upper()} link was successfully claimed!")
        except:
            logger.warning("Failed to DM user.")
        record_stat(ctx.author.id, source)
    else:
        await ctx.send(f"⚠️ {msg}")


async def run_game(ctx, link, game, keywords):
    await ctx.send(f"🎮 Starting {game.title()}...")
    async with browser_semaphore:
        clicked, msg = await run_in_executor(browser_run_game, link, game, keywords)
    if clicked:
        await ctx.send(f"✅ {msg}")
        try:
            await ctx.author.send(f"✅ Auto-clicked '{msg}' for {game}!")
        except:
            logger.warning("Failed to DM user.")
        record_stat(ctx.author.id, "temu")
    else:
        await ctx.send(f"⚠️ {msg}")


# ----------- Setup function to add commands and events -----------

def setup_bot(bot):

    global auto_sharing

    # ----------- Auto Share Task -----------

    @tasks.loop(minutes=60)
    async def share_referral_links():
        channel = bot.get_channel(AUTO_SHARE_CHANNEL_ID)
        if channel:
            msg = (
                "🌟 Support me by clicking these referral links and claim your free items!\n\n"
                f"SHEIN: {REFERRAL_LINKS['shein']}\n"
                f"Temu: {REFERRAL_LINKS['temu']}\n\n"
                "Thanks for helping out! 🙏"
            )
            await channel.send(msg)

    @bot.command()
    async def startsharing(ctx):
        nonlocal auto_sharing
        if not auto_sharing:
            auto_sharing = True
            share_referral_links.start()
            await ctx.send("✅ Started auto-sharing referral links.")
        else:
            await ctx.send("⚠️ Auto-sharing already running.")

    @bot.command()
    async def stopsharing(ctx):
        nonlocal auto_sharing
        if auto_sharing:
            share_referral_links.cancel()
            auto_sharing = False
            await ctx.send("🛑 Stopped auto-sharing.")
        else:
            await ctx.send("⚠️ Auto-sharing not running.")

    # ----------- Claim Command -----------

    @bot.command()
    async def claim(ctx, link: str = None):
        """Auto-detect Temu or SHEIN link and claim."""
        if not link:
            await ctx.send("❌ Please provide a Temu or SHEIN link to claim.")
            return
        link = link.strip().rstrip(".,!?)\"'")  # strip trailing punctuation
        if "temu.com" in link:
            await run_claim(ctx, link, "temu")
        elif "shein.com" in link or "onelink.shein.com" in link:
            await run_claim(ctx, link, "shein")
        else:
            await ctx.send("❌ Unknown link type. Please send a Temu or SHEIN link.")

    # ----------- Game Commands -----------

    @bot.command()
    async def farm(ctx, link: str):
        await run_game(ctx, link, "farm", ["water", "grow", "harvest"])

    @bot.command()
    async def fish(ctx, link: str):
        await run_game(ctx, link, "fish", ["fish", "catch"])

    @bot.command()
    async def stack(ctx, link: str):
        await run_game(ctx, link, "stack", ["stack", "tap"])

    @bot.command()
    async def spin(ctx, link: str):
        await run_game(ctx, link, "spin", ["spin", "start"])

    @bot.command()
    async def gift(ctx, link: str):
        await run_game(ctx, link, "gift", ["gift", "claim"])

    # ----------- SHEIN 10 Free Items -------------

    @bot.command()
    async def shein_10free(ctx, link: str):
        await ctx.send("🎊 Starting SHEIN 10 Free Items claim...")
        async with browser_semaphore:
            success, msg = await run_in_executor(browser_claim_link, link, "shein")
        if success:
            await ctx.send(f"✅ {msg}")
            try:
                await ctx.author.send("🎉 Claimed SHEIN 10 Free Items!")
            except:
                logger.warning("Failed to DM user.")
            record_stat(ctx.author.id, "shein")
        else:
            await ctx.send(f"⚠️ {msg}")

    # ----------- Auto-Loop Game Logic -----------

    async def auto_loop(ctx, game, link, interval):
        await ctx.send(f"🔁 Auto-loop started for {game}. Use !stop {game} to stop.")
        try:
            while game_loops[game]:
                await run_game(ctx, link, game, ["tap", "gift", "catch", "grow", "start"])
                await asyncio.sleep(interval)
        except asyncio.CancelledError:
            await ctx.send(f"⏹️ Auto-loop stopped for {game}.")
        except Exception:
            logger.error(f"Error in auto_loop {game}:\n{traceback.format_exc()}")

    @bot.command()
    async def start(ctx, game: str, link: str, interval: int = 300):
        game = game.lower()
        if game not in game_loops:
            await ctx.send("⚠️ Invalid game name.")
            return
        if game_loops[game]:
            await ctx.send("⚠️ Auto-loop already running for this game.")
            return
        game_loops[game] = True
        loop_tasks[game] = bot.loop.create_task(auto_loop(ctx, game, link, interval))
        await ctx.send(f"✅ Auto-loop started for {game} every {interval} seconds.")

    @bot.command()
    async def stop(ctx, game: str):
        game = game.lower()
        if game in loop_tasks and game_loops[game]:
            game_loops[game] = False
            loop_tasks[game].cancel()
            await ctx.send(f"🛑 Auto-loop stopped for {game}.")
        else:
            await ctx.send("⚠️ No auto-loop running for this game.")

    # ----------- Stats Commands -----------

    @bot.command()
    async def stats(ctx):
        stats = load_stats()
        uid = str(ctx.author.id)
        if uid in stats:
            s = stats[uid]
            await ctx.send(f"📊 Your Stats:\nTemu: {s['temu']} clicks\nSHEIN: {s['shein']} clicks")
        else:
            await ctx.send("📊 You have no stats yet.")

    @bot.command()
    async def leaderboard(ctx):
        stats = load_stats()
        top = sorted(stats.items(), key=lambda x: x[1]['temu'] + x[1]['shein'], reverse=True)[:10]
        lines = []
        for i, (uid, data) in enumerate(top, 1):
            lines.append(f"{i}. <@{uid}> - Temu: {data['temu']}, SHEIN: {data['shein']}")
        await ctx.send("🏆 **Top Helpers Leaderboard** 🏆\n" + "\n".join(lines))

    # ----------- On Message Event for Auto Link Detection -----------

    @bot.event
    async def on_message(message):
        if message.author.bot:
            return

        # Detect Temu or SHEIN link in any message (improved regex, stripping trailing punctuation)
        link_match = re.search(r"(https?://[^\s]+)", message.content)
        if link_match:
            link = link_match.group(1).rstrip(".,!?)\"'")
            if "temu.com" in link:
                await message.channel.send("🔗 Temu link detected! Attempting to claim...")
                class Ctx:
                    author = message.author
                    async def send(self, content): await message.channel.send(content)
                await run_claim(Ctx(), link, "temu")
            elif "shein.com" in link or "onelink.shein.com" in link:
                await message.channel.send("👗 SHEIN link detected! Attempting to claim...")
                class Ctx:
                    author = message.author
                    async def send(self, content): await message.channel.send(content)
                await run_claim(Ctx(), link, "shein")

        # Process commands as usual
        await bot.process_commands(message)
