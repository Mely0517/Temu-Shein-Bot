# shein.py
import os
import asyncio
import random
from pyppeteer import launch
from pyppeteer_stealth import stealth

# ── Proxy config from environment (Render → Environment → Add Secrets)
PROXY_HOST = os.getenv("PROXY_HOST", "geo.iproyal.com")
PROXY_PORT = os.getenv("PROXY_PORT", "12321")
PROXY_USER = os.getenv("PROXY_USER")       # set this in Render
PROXY_PASS = os.getenv("PROXY_PASS")       # set this in Render

# Small helper for human-ish delays
def jitter(a: float, b: float) -> float:
    return random.uniform(a, b)

async def _open_with_proxy(link: str):
    # NOTE: DO NOT include user:pass in --proxy-server
    proxy_arg = f"--proxy-server=http://{PROXY_HOST}:{PROXY_PORT}"

    browser = await launch({
        "headless": True,
        "args": [
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            "--disable-blink-features=AutomationControlled",
            "--window-size=1920,1080",
            proxy_arg,
        ],
        "ignoreHTTPSErrors": True,
        "defaultViewport": {"width": 1366, "height": 768},
    })

    page = await browser.newPage()
    await stealth(page)

    # Authenticate to the proxy here (this is the fix)
    if PROXY_USER and PROXY_PASS:
        await page.authenticate({"username": PROXY_USER, "password": PROXY_PASS})

    await page.setUserAgent(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    # Open the link
    await page.goto(link, {"waitUntil": "domcontentloaded", "timeout": 60000})

    # A little scrolling + dwell to look human
    for _ in range(random.randint(2, 4)):
        await page.evaluate("() => window.scrollBy(0, Math.floor(window.innerHeight*0.6))")
        await asyncio.sleep(jitter(0.8, 1.6))

    await asyncio.sleep(jitter(2.5, 5.0))
    await browser.close()

async def boost_shein_link(link: str, discord_channel=None):
    # Try up to 3 times with short backoff
    last_err = None
    for attempt in range(1, 4):
        try:
            if discord_channel:
                await discord_channel.send(
                    f"🧑‍💻 SHEIN: opening (attempt {attempt}/3) with proxy {PROXY_HOST}:{PROXY_PORT}"
                )
            await _open_with_proxy(link)
            msg = f"✅ SHEIN boost successful: {link}"
            print(msg)
            if discord_channel:
                await discord_channel.send(msg)
            return
        except Exception as e:
            last_err = e
            err_text = str(e)
            print(f"[shein] attempt {attempt} error: {err_text}")
            if discord_channel:
                await discord_channel.send(
                    f"❌ SHEIN error (attempt {attempt}/3): {err_text[:400]} at {link}"
                )
            await asyncio.sleep(jitter(2, 5))

    # All attempts failed
    fail_msg = f"❌ SHEIN failed after 3 attempts: {link}"
    print(fail_msg, last_err)
    if discord_channel:
        await discord_channel.send(fail_msg)
    # Also log to file so the background loop can skip next time
    try:
        with open("boost_failures.txt", "a") as f:
            f.write(f"{link} | {last_err}\n")
    except:
        pass