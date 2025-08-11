import asyncio
import random
from typing import Optional, Dict

from pyppeteer import launch
from pyppeteer.errors import NetworkError, TimeoutError, PageError
from pyppeteer_stealth import stealth
from proxy_utils import get_random_proxy


async def _open_with_proxy(link: str, proxy: Dict, discord_channel=None) -> None:
    proxy_arg = f"--proxy-server=http://{proxy['ip']}:{proxy['port']}"

    browser = await launch({
        "headless": True,
        "ignoreHTTPSErrors": True,
        "args": [
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            "--disable-blink-features=AutomationControlled",
            "--window-size=1920,1080",
            proxy_arg,
        ],
    })

    try:
        page = await browser.newPage()
        await stealth(page)

        if proxy.get("username") and proxy.get("password"):
            await page.authenticate({
                "username": proxy["username"],
                "password": proxy["password"]
            })

        await page.setUserAgent(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        await page.goto(link, timeout=45_000, waitUntil="domcontentloaded")
        await page.waitForSelector("body", timeout=10_000)

        await asyncio.sleep(random.uniform(2.0, 4.0))
        for _ in range(random.randint(1, 3)):
            await page.evaluate("() => window.scrollBy(0, Math.floor(window.innerHeight*0.6));")
            await asyncio.sleep(random.uniform(0.8, 1.6))
        await asyncio.sleep(random.uniform(1.5, 3.0))

    finally:
        await browser.close()


async def boost_temu_link(link: str, discord_channel: Optional[object] = None):
    attempts = 3
    for attempt in range(1, attempts + 1):
        proxy = get_random_proxy()
        msg = f"🧑‍💻 TEMU: opening (attempt {attempt}/{attempts}) with proxy {proxy['ip']}:{proxy['port']}"
        print(msg)
        if discord_channel:
            await discord_channel.send(msg)

        try:
            await _open_with_proxy(link, proxy, discord_channel)
            ok = f"✅ TEMU success: {link}"
            print(ok)
            if discord_channel:
                await discord_channel.send(ok)
            return

        except (NetworkError, TimeoutError, PageError) as e:
            err = f"❌ TEMU error (attempt {attempt}/{attempts}): {e} at {link}"
            print(err)
            if discord_channel:
                await discord_channel.send(err)
            await asyncio.sleep(3 + attempt)

        except Exception as e:
            err = f"❌ TEMU unexpected error: {type(e).__name__}: {e}"
            print(err)
            if discord_channel:
                await discord_channel.send(err)
            await asyncio.sleep(3 + attempt)

    fail = f"❌ TEMU failed after {attempts} attempts: {link}"
    print(fail)
    if discord_channel:
        await discord_channel.send(fail)