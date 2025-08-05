import asyncio
from pyppeteer import launch
import random
from proxy_utils import get_random_proxy
from pyppeteer_stealth import stealth

async def boost_shein_link(link, discord_channel=None):
    print(f"⏳ Starting SHEIN boost for: {link}")

    # Pick a random proxy from proxy_utils.py
    proxy = get_random_proxy()
    print(f"🌐 Using proxy {proxy['ip']}:{proxy['port']}")

    browser_args = [
        "--no-sandbox",
        "--disable-setuid-sandbox",
        "--disable-dev-shm-usage",
        "--disable-blink-features=AutomationControlled",
        f"--proxy-server=http://{proxy['ip']}:{proxy['port']}",
        "--window-size=1920,1080",
    ]

    try:
        browser = await launch(
            {
                "headless": True,
                "args": browser_args,
                "ignoreHTTPSErrors": True,
            }
        )

        page = await browser.newPage()

        # Authenticate proxy if needed
        if proxy.get("username") and proxy.get("password"):
            await page.authenticate({
                "username": proxy["username"],
                "password": proxy["password"]
            })

        await stealth(page)

        await page.setUserAgent(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )

        await page.goto(link, timeout=60000)
        await page.waitForSelector("body", timeout=10000)  # Ensure page loads

        # Scroll like a human
        for _ in range(random.randint(1, 3)):
            await page.evaluate("() => { window.scrollBy(0, window.innerHeight * 0.5); }")
            await asyncio.sleep(random.uniform(1, 2))

        await asyncio.sleep(random.uniform(3, 6))
        await browser.close()

        msg = f"✅ Boost successful for SHEIN link: {link}"
        print(msg)
        if discord_channel:
            await discord_channel.send(msg)

    except Exception as e:
        error_msg = f"❌ Error with SHEIN link {link}: {e}"
        print(error_msg)
        if discord_channel:
            await discord_channel.send(error_msg)