# shein.py
import asyncio
import random
from typing import Dict, Optional

from pyppeteer import launch
from pyppeteer_stealth import stealth
from proxy_utils import get_random_proxy

BOOST_LOCK = asyncio.Lock()

def _jitter(a: float, b: float) -> float:
    return random.uniform(a, b)

def _proxy_arg(proxy: Dict, scheme: str) -> str:
    return (f"--proxy-server={scheme}://{proxy['ip']}:{proxy['port']}"
            if scheme.startswith("socks")
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

    try:
        page.setDefaultNavigationTimeout(90000)
    except AttributeError:
        pass

    if proxy.get("username") and proxy.get("password"):
        await page.authenticate({"username": proxy["username"], "password": proxy["password"]})

    await stealth(page)
    # A common mobile/Chrome UA can reduce deep-link/app store shenanigans; keep Desktop UA if you prefer.
    await page.setUserAgent(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    # Language header helps some geo/captcha flows
    await page.setExtraHTTPHeaders({"Accept-Language": "en-US,en;q=0.9"})
    return browser, page

async def _wait_stable(page, total_ms: int = 6000):
    """Wait until the document is 'complete' and give it a tiny quiet period."""
    try:
        await page.waitForFunction('document.readyState === "complete"', {"timeout": total_ms})
    except Exception:
        # If it never reaches 'complete', continue anyway
        pass
    await asyncio.sleep(1.5)

async def _open_with_proxy(link: str, proxy: Dict):
    preferred = (proxy.get("scheme") or "http").lower()
    candidates = [preferred] + (["socks5"] if not preferred.startswith("socks") else ["http"])
    last_err: Optional[Exception] = None

    for scheme in candidates:
        browser = None
        try:
            browser, page = await _launch_with_proxy(proxy, scheme)

            # First jump
            await page.goto("about:blank")
            await page.goto(link, {"waitUntil": "networkidle2", "timeout": 90000})

            # Some onelink flows auto-redirect again; allow one follow-up nav quietly
            try:
                await page.waitForNavigation({"waitUntil": "networkidle2", "timeout": 15000})
            except Exception:
                pass

            # Wait for stability before any JS
            await _wait_stable(page, 8000)

            # Try a gentle scroll sequence, but ignore if context gets destroyed mid-redirect
            try:
                for _ in range(random.randint(2, 4)):
                    await page.evaluate("() => window.scrollBy(0, Math.floor(window.innerHeight*0.6))")
                    await asyncio.sleep(_jitter(0.8, 1.6))
                await asyncio.sleep(_jitter(2.0, 4.0))
            except Exception as e:
                # If navigation happened during scroll, that's okay—we've already opened the link.
                if "Execution context was destroyed" not in str(e):
                    raise

            try:
                await browser.close()
            except Exception:
                pass
            return  # success
        except Exception as e:
            last_err = e
            try:
                if browser:
                    await browser.close()
            except Exception:
                pass

            msg = str(e)
            # Treat these as retryable and let the outer loop try again or swap scheme
            retryable = any(x in msg for x in [
                "Target closed",
                "ERR_TUNNEL_CONNECTION_FAILED",
                "ERR_NO_SUPPORTED_PROXIES",
                "Navigation timeout",
                "net::ERR_PROXY",
                "net::ERR_NETWORK_CHANGED",
                "Execution context was destroyed",   # ⬅️ added
            ])
            if retryable:
                await asyncio.sleep(_jitter(1.5, 3.0))
                continue
            else:
                break

    raise last_err if last_err else RuntimeError("Unknown proxy/navigation error")

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
                elif "Execution context was destroyed" in msg:
                    msg = "Page redirected during action; retrying."
                if discord_channel:
                    await discord_channel.send(f"❌ SHEIN error {attempt}/{attempts}: {msg} at {link}")
                await asyncio.sleep(_jitter(2, 5))
        if discord_channel:
            await discord_channel.send(f"❌ SHEIN failed after {attempts} attempts: {link}")