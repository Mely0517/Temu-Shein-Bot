# shein.py
import asyncio
import random
from typing import Dict, Optional

from pyppeteer import launch
from pyppeteer_stealth import stealth
from proxy_utils import get_random_proxy

# Serialize SHEIN boosts to prevent overlapping browser closures
BOOST_LOCK = asyncio.Lock()

def jitter(a: float, b: float) -> float:
    return random.uniform(a, b)

def _proxy_arg(proxy: Dict, scheme: str) -> str:
    # Chromium is happiest with host:port for HTTP; include scheme for socks5
    return (f"--proxy-server={scheme}://{proxy['ip']}:{proxy['port']}"
            if scheme in ("socks5", "socks5h")
            else f"--proxy-server={proxy['ip']}:{proxy['port']}")

async def _launch_with_proxy(proxy: Dict, scheme: str):
    browser = await launch({
        "headless": True,
        "ignoreHTTPSErrors": True,
        "args": [
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            "--disable-blink-features=AutomationControlled",
            "--disable-gpu",
            "--no-zygote",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-software-rasterizer",
            "--window-size=1920,1080",
            _proxy_arg(proxy, scheme),
            "--proxy-bypass-list=<-loopback>",
            "--force-webrtc-ip-handling-policy=disable_non_proxied_udp",
            "--disable-webrtc-encryption",
            "--disable-web-security",
            "--user-data-dir=/tmp/puppeteer_dev_profile",
        ],
        "defaultViewport": {"width": 1366, "height": 768},
    })
    page = await browser.newPage()

    # Apply timeouts early
    page.setDefaultNavigationTimeout(90000)
    page.setDefaultTimeout(45000)

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
    Try with proxy's preferred scheme first; on proxy-setup errors,
    fall back to the alternate scheme (http <-> socks5). Retry on transient crashes.
    """
    preferred = (proxy.get("scheme") or "http").lower()
    candidates = [preferred] + (["socks5"] if not preferred.startswith("socks") else ["http"])

    last_err: Optional[Exception] = None

    for scheme in candidates:
        browser = None
        try:
            browser, page = await _launch_with_proxy(proxy, scheme)
            await page.goto("about:blank")
            await page.goto(link, {"waitUntil": "domcontentloaded", "timeout": 90000})
            await asyncio.sleep(1.5)

            # Human-ish behavior
            for _ in range(random.randint(2, 4)):
                await page.evaluate("() => window.scrollBy(0, Math.floor(window.innerHeight*0.6))")
                await asyncio.sleep(jitter(0.8, 1.6))
            await asyncio.sleep(jitter(2.5, 5.0))

            try:
                await browser.close()
            except Exception:
                pass
            return  # success
        except Exception as e:
            last_err = e
            # Clean close if possible
            try:
                if browser:
                    await browser.close()
            except Exception:
                pass

            msg = str(e)
            # Retry if it's likely a proxy/nav flake; otherwise break
            retryable = any(x in msg for x in [
                "Target closed",
                "ERR_TUNNEL_CONNECTION_FAILED",
                "ERR_NO_SUPPORTED_PROXIES",
                "Navigation timeout",
                "net::ERR_PROXY",
                "net::ERR_NETWORK_CHANGED",
            ])
            if retryable:
                await asyncio.sleep(jitter(1.5, 3.0))
                continue
            else:
                break

    # If we get here, all attempts failed
    raise last_err if last_err else RuntimeError("Unknown proxy error")

async def boost_shein_link(link: str, discord_channel=None):
    async with BOOST_LOCK:
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
                    msg = "Chrome rejected the proxy (ERR_NO_SUPPORTED_PROXIES)."
                elif "ERR_TUNNEL_CONNECTION_FAILED" in msg:
                    msg = "Proxy tunnel failed (check scheme/user/pass/host/port)."
                elif "Target closed" in msg:
                    msg = "Chromium target closed unexpectedly."
                if discord_channel:
                    await discord_channel.send(f"❌ SHEIN error {attempt}/{attempts}: {msg} at {link}")
                await asyncio.sleep(jitter(2, 5))
        if discord_channel:
            await discord_channel.send(f"❌ SHEIN failed after {attempts} attempts: {link}")