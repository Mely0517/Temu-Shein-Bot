# shein.py
import asyncio, random
from pyppeteer import launch
from pyppeteer_stealth import stealth
from proxy_utils import get_random_proxy

def jitter(a, b): return random.uniform(a, b)

async def _open_with_proxy(link: str, proxy: dict):
    scheme = (proxy.get("scheme") or "http").lower()
    proxy_arg = f"--proxy-server={scheme}://{proxy['ip']}:{proxy['port']}"
    browser = await launch({
        "headless": True,
        "args": [
            "--no-sandbox","--disable-setuid-sandbox","--disable-dev-shm-usage",
            "--disable-blink-features=AutomationControlled","--window-size=1920,1080",
            proxy_arg,"--proxy-bypass-list=<-loopback>",
            "--force-webrtc-ip-handling-policy=disable_non_proxied_udp",
            "--disable-webrtc-encryption","--disable-web-security",
        ],
        "ignoreHTTPSErrors": True,
        "defaultViewport": {"width": 1366, "height": 768},
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
        await page.goto(link, {"waitUntil": "networkidle2", "timeout": 90000})
        for _ in range(random.randint(2, 4)):
            await page.evaluate("() => window.scrollBy(0, Math.floor(window.innerHeight*0.6))")
            await asyncio.sleep(jitter(0.8, 1.6))
        await asyncio.sleep(jitter(2.5, 5.0))
    finally:
        await browser.close()

async def boost_shein_link(link: str, discord_channel=None):
    attempts = 3
    for attempt in range(1, attempts + 1):
        proxy = get_random_proxy()
        try:
            if discord_channel:
                await discord_channel.send(
                    f"🧑‍💻 SHEIN attempt {attempt}/{attempts} via {(proxy.get('scheme') or 'http')}://{proxy['ip']}:{proxy['port']}"
                )
            await _open_with_proxy(link, proxy)
            if discord_channel:
                await discord_channel.send(f"✅ SHEIN success: {link}")
            return
        except Exception as e:
            if discord_channel:
                msg = str(e)
                if "ERR_TUNNEL_CONNECTION_FAILED" in msg or "ERR_PROXY" in msg:
                    msg = "Proxy tunnel failed (check scheme/user/pass/host/port)."
                await discord_channel.send(f"❌ SHEIN error {attempt}/{attempts}: {msg} at {link}")
            await asyncio.sleep(jitter(2, 5))
    if discord_channel:
        await discord_channel.send(f"❌ SHEIN failed after {attempts} attempts: {link}")