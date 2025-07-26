import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import asyncio
import os
import json
import re
import aiohttp
from discord.ext import tasks

# --- Configurable values ---

REFERRAL_LINKS = {
    "shein": "https://onelink.shein.com/15/4vqj870ifsi6",
    "temu": "https://temu.link/your-referral-code"
}
AUTO_SHARE_CHANNEL_ID = 123456789012345678  # Replace with your Discord channel ID

STATS_FILE = "stats.json"
game_loops = {"farm": False, "fish": False, "stack": False, "spin": False, "gift": False}
loop_tasks = {}
auto_sharing = False

# --- Headless browser config for Render ---

def get_browser():
    import undetected_chromedriver as uc

    options = uc.ChromeOptions()
    options.binary_location = "/usr/bin/google-chrome"  # ✅ This is the correct path for Chrome inside Docker/Render
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0")

    return uc.Chrome(options=options)


# --- Stats Helpers ---

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

# --- Chrome Tab Link Fetch (optional debugging) ---

async def get_chrome_tab_url():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:9222/json") as resp:
                tabs = await resp.json()
                if tabs:
                    return tabs[0]["url"]
    except:
        return None

# --- Setup bot commands and events ---

def setup_bot(bot):

    # --- Auto Share Task ---
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
        global auto_sharing
        if not auto_sharing:
            auto_sharing = True
            share_referral_links.start()
            await ctx.send("✅ Started auto-sharing referral links.")
        else:
            await ctx.send("⚠️ Auto-sharing already running.")

    @bot.command()
    async def stopsharing(ctx):
        global auto_sharing
        if auto_sharing:
            share_referral_links.cancel()
            auto_sharing = False
            await ctx.send("🛑 Stopped auto-sharing.")
        else:
            await ctx.send("⚠️ Auto-sharing not running.")

    # --- Core Claim Handler ---
    async def run_claim(ctx, link, source):
        await ctx.send(f"🚀 Opening {source.upper()} link...")
        try:
            browser = get_browser()
            browser.get(link)
            await asyncio.sleep(6)
            try:
                btn = browser.find_element(By.XPATH, "//button[contains(text(), 'Accept') or contains(text(), 'Join') or contains(text(), 'Open') or contains(text(), 'Claim')]")
                btn.click()
                await ctx.send(f"✅ Successfully clicked {source.upper()} claim button!")
                await ctx.author.send(f"✅ Your {source.upper()} link was successfully clicked and opened!")
                record_stat(ctx.author.id, source)
            except:
                await ctx.send("⚠️ Couldn’t find a button, but page opened.")
            browser.quit()
        except Exception as e:
            await ctx.send(f"❌ {source.upper()} error: {e}")

    @bot.command()
    async def claim(ctx, link: str = None):
        """Auto-detect Temu or SHEIN link and claim"""
        if not link:
            chrome_url = await get_chrome_tab_url()
            if chrome_url:
                link = chrome_url
            else:
                await ctx.send("❌ No link provided and Chrome tab not found.")
                return
        if "temu.com" in link:
            await run_claim(ctx, link, "temu")
        elif "shein" in link:
            await run_claim(ctx, link, "shein")
        else:
            await ctx.send("❌ Unknown link type. Please send a Temu or SHEIN link.")

    # --- Game Commands ---
    async def run_game(ctx, link, game, keywords):
        await ctx.send(f"🎮 Starting {game.title()}...")
        try:
            browser = get_browser()
            browser.get(link)
            await asyncio.sleep(8)
            buttons = browser.find_elements(By.TAG_NAME, "button")
            clicked = False
            for btn in buttons:
                text = btn.text.lower()
                if any(kw in text for kw in keywords):
                    btn.click()
                    clicked = True
                    await ctx.send(f"✅ Clicked '{btn.text}'")
                    record_stat(ctx.author.id, "temu")
                    await ctx.author.send(f"✅ Auto-clicked '{btn.text}' for {game}!")
                    break
            if not clicked:
                await ctx.send("⚠️ No action buttons found or already done.")
            browser.quit()
        except Exception as e:
            await ctx.send(f"❌ {game.title()} error: {e}")

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

    # --- SHEIN 10 Free Items ---
    @bot.command()
    async def claim_shein(link):
    print("🎊 Starting SHEIN 10 Free Items claim...")
    try:
        browser = get_browser()
        browser.get(link)
        await asyncio.sleep(8)  # Wait for the page to fully load

        # Scroll down a bit to trigger any lazy-load buttons
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
        await asyncio.sleep(2)

        # Try common buttons
        button_selectors = [
            "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'claim')]",
            "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'receive')]",
            "//a[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'join')]",
            "//a[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'get')]",
            "//div[contains(@class, 'btn')]",
            "//button",
        ]

        found = False
        for selector in button_selectors:
            try:
                button = browser.find_element(By.XPATH, selector)
                if button and button.is_displayed():
                    button.click()
                    await asyncio.sleep(3)
                    print("✅ Clicked a button on SHEIN page.")
                    found = True
                    break
            except Exception:
                continue

        browser.quit()

        if found:
            return "✅ Claimed SHEIN reward successfully!"
        else:
            return "⚠️ Couldn’t find a button, but page opened."

    except Exception as e:
        print("❌ SHEIN error:\n---------------------")
        print(str(e))
        return f"❌ SHEIN error:\n---------------------\n{str(e)}"


    # --- Auto-Loop Game Logic ---
    async def auto_loop(ctx, game, link, interval):
        await ctx.send(f"🔁 Auto-loop started for {game}.")
        try:
            while game_loops[game]:
                await run_game(ctx, link, game, ["tap", "gift", "catch", "grow", "start"])
                await asyncio.sleep(interval)
        except asyncio.CancelledError:
            await ctx.send(f"⏹️ Auto-loop stopped for {game}.")

    @bot.command()
    async def start(ctx, game: str, link: str, interval: int = 300):
        game = game.lower()
        if game not in game_loops or game_loops[game]:
            await ctx.send("⚠️ Invalid game or already running.")
            return
        game_loops[game] = True
        loop_tasks[game] = bot.loop.create_task(auto_loop(ctx, game, link, interval))
        await ctx.send(f"✅ Auto-loop started for {game}.")

    @bot.command()
    async def stop(ctx, game: str):
        game = game.lower()
        if game in loop_tasks:
            game_loops[game] = False
            loop_tasks[game].cancel()
            await ctx.send(f"🛑 Auto-loop stopped for {game}.")

    # --- Stats Commands ---
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

    # --- Auto link detection ---
    @bot.event
    async def on_message(message):
        if message.author.bot:
            return

        # Detect Temu or SHEIN link in messages
        link_match = re.search(r"(https?://\S+)", message.content)
        if link_match:
            link = link_match.group(1)
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

        # Process other commands
        await bot.process_commands(message)

