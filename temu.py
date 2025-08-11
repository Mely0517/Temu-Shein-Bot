# temu.py
import asyncio
import random
from pyppeteer import launch
from pyppeteer_stealth import stealth
from proxy_utils import get_random_proxy

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/114.0.0.0 Safari/537.36"
)

async def _open_page_with_proxy():
    """Launch Chromium with proxy and return (browser, page)."""
    p = get_random_proxy()

    launch_args = [
        f"--proxy-server=http://{p['ip']}:{p['port']}",
        "--no-sandbox",
        "--disable-setuid-sandbox",
        "--disable-dev-shm-usage",
        "--disable-blink-features=AutomationControlled",
        "--window-size=1280,800",
    ]

    browser = await launch({
        "headless": True,
        "args": launch_args,
        "ignoreHTTPSErrors": True,
        "handleSIGINT": False,
        "handleSIGTERM": False,
        "handleSIGHUP": False,
    })

    page = await browser.newPage()

    # ✅ Proper proxy authentication (fixes ERR_PROXY_AUTH_UNSUPPORTED)
    if p.get("username") and p.get("password"):
        await page.authenticate({"username": p["username"], "password": p["password"]})

    await stealth(page)
    await page.setUserAgent(USER_AGENT)
    await page.setViewport({"width": 1280, "height": 800})
    return browser, page

async def boost_temu_link(link: str, discord_channel=None):
    """Open a Temu invite link with stealth + proxy, with retries."""
    attempts = 3

    for attempt in range(1, attempts + 1):
        browser = None
        try:
            if discord_channel:
                await discord_channel.send(f"⏳ TEMU: opening (attempt {attempt}/{attempts})")

            browser, page = await _open_page_with_proxy()

            # Load the page (temu invites can chain redirects)
            await page.goto(link, timeout=60000, waitUntil="domcontentloaded")
            await page.waitForSelector("body", timeout=10000)

            # Human-like dwell & scroll
            await asyncio.sleep(random.uniform(2.5, 4.0))
            for _ in range(random.randint(2, 4)):
                await page.evaluate("() => window.scrollBy(0, Math.floor(window.innerHeight * 0.6))")
                await asyncio.sleep(random.uniform(1.0, 2.0))

            await asyncio.sleep(random.uniform(3.0, 5.0))

            await browser.close()
            msg = f"✅ TEMU boost successful: {link}"
            print(msg)
            if discord_channel:
                await discord_channel.send(msg)
            return  # success, stop retrying

        except Exception as e:
            if browser:
                try:
                    await browser.close()
                except Exception:
                    pass
            err = f"❌ TEMU error (attempt {attempt}/{attempts}): {e}"
            print(err)
            if discord_channel:
                await discord_channel.send(err)
            await asyncio.sleep(1 + attempt)  # simple backoff

    # All attempts failed
    fail_msg = f"❌ TEMU failed after {attempts} attempts: {link}"
    print(fail_msg)
    if discord_channel:
        await discord_channel.send(fail_msg)