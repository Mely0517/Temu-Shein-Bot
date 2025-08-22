# shein.py
import asyncio
import random
from typing import Dict, Optional

from pyppeteer import launch
from pyppeteer_stealth import stealth
from proxy_utils import get_random_proxy

def jitter(a: float, b: float) -> float:
    return random.uniform(a, b)

async def _launch_with_proxy(proxy: Dict, scheme: str):
    """
    Launch Chromium with a given proxy scheme.
    We pass ONLY host:port in --proxy-server and authenticate separately.
    """
    proxy_arg = f"--proxy-server={scheme}://{proxy['ip']}:{proxy['port']}" if scheme in ("socks5", "socks5h") \
                else f"--proxy-server={proxy['ip']}:{proxy['port']}"  # http works without explicit scheme

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
        "defaultViewport": {"width": 1366, "height": 768},
    })
    page = await browser.newPage()

    # Authenticate if creds present
    if proxy.get("username") and proxy.get("password"):
        await page.authenticate({"username": proxy["username"], "password": proxy["password"]})

    await stealth(page)
    await page.setUserAgent(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    return browser, page

async def _open_with_proxy(link: str, proxy: Dict):
    """
    Try with the proxy's own scheme first; on proxy-setup errors,
    auto-fallback to the opposite scheme (http <-> socks5).
    """
    preferred = (proxy.get("scheme") or "http").lower()
    candidates = [preferred]
    if preferred.startswith("http"):
        candidates.append("socks5")
    else:
        candidates.append("http")

    last_err: Optional[Exception] = None

    for scheme in candidates:
        browser = None
        try:
            browser, page = await _launch_with_proxy(proxy, scheme)
            # Warm-up
            await page.goto("about:blank")
            # Navigate
            await page.goto(link, {"waitUntil": "networkidle2", "timeout": 90000})

            # Human-ish behavior
            for _ in range(random.randint(2, 4)):
                await page.evaluate("() => window.scrollBy(0, Math.floor(window.innerHeight*0.6))")
                await asyncio.sleep(jitter(0.8, 1.6))
            await asyncio.sleep(jitter(2.5, 5.0))

            await browser.close()
            return  # success
        except Exception as e:
            last_err = e
            try:
                if browser:
                    await browser.close()
            except:
                pass
            # If it looks like a proxy setup error, try the alternate scheme
            msg = str(e)
            if ("ERR_NO_SUPPORTED_PROXIES" in msg or
                "ERR_TUNNEL_CONNECTION_FAILED" in msg or
                "proxy" in msg.lower()):
                continue  # try next candidate
            else:
                break  # not a proxy-setup issue; bubble up

    # If we get here, all attempts failed
    raise last_err if last_err else RuntimeError("Unknown proxy error")

async def boost_shein_link(link: str, discord_channel=None):
    attempts = 3
    for attempt in range(1, attempts + 1):
        proxy = get_random_proxy()
        scheme_label = (proxy.get("scheme") or "http").lower()
        if discord_channel:
            await discord_channel.send(
                f"🧑‍💻 SHEIN attempt {attempt}/{attempts} via {scheme_label}://{proxy['ip']}:{proxy['port']}"
            )
        try:
            await _open_with_proxy(link, proxy)
            if discord_channel:
                await discord_channel.send(f"✅ SHEIN success: {link}")
            return
        except Exception as e:
            msg = str(e)
            if "ERR_NO_SUPPORTED_PROXIES" in msg:
                msg = "Chrome rejected the proxy (ERR_NO_SUPPORTED_PROXIES). Trying other scheme/line…"
            elif "ERR_TUNNEL_CONNECTION_FAILED" in msg:
                msg = "Proxy tunnel failed (check scheme/user/pass/host/port)."
            if discord_channel:
                await discord_channel.send(f"❌ SHEIN error {attempt}/{attempts}: {msg} at {link}")
            await asyncio.sleep(jitter(2, 5))
    if discord_channel:
        await discord_channel.send(f"❌ SHEIN failed after {attempts} attempts: {link}")