# shein.py
import os
import asyncio
import random
from pyppeteer import launch
from pyppeteer_stealth import stealth

PROXY_SCHEME = os.getenv("PROXY_SCHEME", "http").lower()
if PROXY_SCHEME not in {"http", "socks5", "socks5h"}:
    PROXY_SCHEME = "http"

PROXY_HOST = os.getenv("PROXY_HOST", "geo.iproyal.com")
PROXY_PORT = os.getenv("PROXY_PORT", "12321")
PROXY_USER = os.getenv("PROXY_USER")
PROXY_PASS = os.getenv("PROXY_PASS")

def jitter(a: float, b: float) -> float:
    return random.uniform(a, b)

async def _open_with_proxy(link: str):
    proxy_arg = f"--proxy-server={PROXY_SCHEME}://{PROXY_HOST}:{PROXY_PORT}"

    browser = await launch({
        "headless": True,
        "args": [
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            "--disable-blink-features=AutomationControlled",
            "--window-size=1920,1080",
            proxy_arg,
            "--proxy-bypass-list=<-loopback>",
            "--force-webrtc-ip-handling-policy=disable_non_proxied_udp",
            "--disable-webrtc-encryption",
            "--disable-web-security",
        ],
        "ignoreHTTPSErrors": True,
        "defaultViewport": {"width": 1366, "height": 768},
    })

    try:
        page = await browser.newPage()

        if PROXY_USER and PROXY_PASS:
            await page.authenticate({"username": PROXY_USER, "password": PROXY_PASS})

        await stealth(page)

        await page.setUserAgent(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        await page.goto("about:blank")
        await page.goto(link, {"waitUntil": "networkidle2", "timeout": 90000})

        for _ in range(random.randint(2, 4)):
            await page.evaluate("() => window.scrollBy(0, Math.floor(window.innerHeight*0.6))")
            await asyncio.sleep(jitter(0.8, 1.6))

        await asyncio.sleep(jitter(2.5, 5.0))
    finally:
        await browser.close()

async def boost_shein_link(link: str, discord_channel=None):
    last_err = None
    for attempt in range(1, 4):
        try:
            if discord_channel:
                await discord_channel.send(
                    f"🧑‍💻 SHEIN: opening (attempt {attempt}/3) with proxy {PROXY_SCHEME}://{PROXY_HOST}:{PROXY_PORT}"
                )
            await _open_with_proxy(link)
            msg = f"✅ SHEIN boost successful: {link}"
            if discord_channel:
                await discord_channel.send(msg)
            return
        except Exception as e:
            last_err = str(e)
            if "ERR_TUNNEL_CONNECTION_FAILED" in last_err or "ERR_PROXY" in last_err:
                last_err = "Proxy tunnel failed (check PROXY_SCHEME/USER/PASS/HOST/PORT)."
            if discord_channel:
                await discord_channel.send(
                    f"❌ SHEIN error (attempt {attempt}/3): {last_err[:400]} at {link}"
                )
            await asyncio.sleep(jitter(2, 5))

    if discord_channel:
        await discord_channel.send(f"❌ SHEIN failed after 3 attempts: {link}")