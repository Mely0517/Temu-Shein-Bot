# temu.py
import asyncio, random
from typing import Optional, Dict
from pyppeteer import launch
from pyppeteer.errors import NetworkError, TimeoutError, PageError
from pyppeteer_stealth import stealth
from proxy_utils import get_random_proxy

async def _open_with_proxy(link: str, proxy: Dict, discord_channel=None) -> None:
    scheme = (proxy.get("scheme") or "http").lower()
    proxy_arg = f"--proxy-server={scheme}://{proxy['ip']}:{proxy['port']}"
    browser = await launch({
        "headless": True,
        "ignoreHTTPSErrors": True,
        "args": [
            "--no-sandbox","--disable-setuid-sandbox","--disable-dev-shm-usage",
            "--disable-blink-features=AutomationControlled","--window-size=1920,1080",
            proxy_arg,"--proxy-bypass-list=<-loopback>",
            "--force-webrtc-ip-handling-policy=disable_non_proxied_udp",
            "--disable-webrtc-encryption","--disable-web-security",
        ],
    })
    try:
        page = await browser.newPage()
        if proxy.get("username") and proxy.get("password"):
            await page.authenticate({"username": proxy["username"], "password": proxy["password"]})
        await stealth(page)
        await page.setUserAgent(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        await page.goto("about:blank")
        await page.goto(link, timeout=60_000, waitUntil="networkidle2")
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
    last_err = None
    for attempt in range(1, attempts + 1):
        proxy = get_random_proxy()
        if discord_channel:
            await discord_channel.send(
                f"🧑‍💻 TEMU attempt {attempt}/{attempts} via {(proxy.get('scheme') or 'http')}://{proxy['ip']}:{proxy['port']}"
            )
        try:
            await _open_with_proxy(link, proxy, discord_channel)
            if discord_channel:
                await discord_channel.send(f"✅ TEMU success: {link}")
            return
        except (NetworkError, TimeoutError, PageError) as e:
            last_err = str(e)
            if "ERR_TUNNEL_CONNECTION_FAILED" in last_err or "ERR_PROXY" in last_err:
                last_err = "Proxy tunnel failed (check proxy scheme/username/password/host/port)."
            if discord_channel:
                await discord_channel.send(f"❌ TEMU error {attempt}/{attempts}: {last_err} at {link}")
            await asyncio.sleep(3 + attempt)
        except Exception as e:
            last_err = f"{type(e).__name__}: {e}"
            if discord_channel:
                await discord_channel.send(f"❌ TEMU unexpected error: {last_err}")
            await asyncio.sleep(3 + attempt)
    if discord_channel:
        await discord_channel.send(f"❌ TEMU failed after {attempts} attempts: {link}")