# temu.py
import asyncio
import random
from typing import Optional, Dict

from pyppeteer import launch
from pyppeteer.errors import NetworkError, TimeoutError, PageError
from pyppeteer_stealth import stealth
from proxy_utils import get_random_proxy


async def _open_with_proxy(link: str, proxy: Dict, discord_channel=None) -> None:
    # Expect keys: ip, port, username (opt), password (opt)
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
            "--proxy-bypass-list=<-loopback>",
            "--force-webrtc-ip-handling-policy=disable_non_proxied_udp",
            "--disable-webrtc-encryption",
            "--disable-web-security",
        ],
    })

    try:
        page = await browser.newPage()

        # Authenticate to the proxy FIRST (before any navigation)
        if proxy.get("username") and proxy.get("password"):
            await page.authenticate({
                "username": proxy["username"],
                "password": proxy["password"]
            })

        await stealth(page)

        await page.setUserAgent(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        # Warm-up so auth is “locked in”
        await page.goto("about:blank")

        # Open the real link
        await page.goto(link, timeout=60_000, waitUntil="networkidle2")
        await page.waitForSelector("body", timeout=10_000)

        # Human-like behavior
        await asyncio.sleep(random.uniform(2.0, 4.0))
        for _ in range(random.randint(1, 3)):
            await page.evaluate(
                "() => window.scrollBy(0, Math.floor(window.innerHeight*0.6));"
            )
            await asyncio.sleep(random.uniform(0.8, 1.6))
        await asyncio.sleep(random.uniform(1.5, 3.0))

    finally:
        await browser.close()


async def boost_temu_link(link: str, discord_channel: Optional[object] = None):
    attempts = 3
    last_err = None

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
            last_err = str(e)
            if "ERR_TUNNEL_CONNECTION_FAILED" in last_err or "ERR_PROXY" in last_err:
                last_err = "Proxy tunnel failed (check proxy username/password/host/port)."
            err = f"❌ TEMU error (attempt {attempt}/{attempts}): {last_err} at {link}"
            print(err)
            if discord_channel:
                await discord_channel.send(err)
            await asyncio.sleep(3 + attempt)

        except Exception as e:
            last_err = f"{type(e).__name__}: {e}"
            err = f"❌ TEMU unexpected error: {last_err}"
            print(err)
            if discord_channel:
                await discord_channel.send(err)
            await asyncio.sleep(3 + attempt)

    fail = f"❌ TEMU failed after {attempts} attempts: {link}"
    print(fail)
    if discord_channel:
        await discord_channel.send(fail)