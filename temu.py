import asyncio
import random
import socket
from pyppeteer import launch
from proxy_utils import get_random_proxy
from pyppeteer_stealth import stealth

CHROME_PATH = "/opt/render/.local/share/pyppeteer/local-chromium/588429/chrome-linux/chrome"

async def test_proxy(ip, port, timeout=5):
    try:
        socket.create_connection((ip, int(port)), timeout=timeout)
        return True
    except:
        return False

async def boost_temu_link(link, discord_channel=None):
    for attempt in range(3):
        proxy = get_random_proxy()
        print(f"🌐 Using proxy {proxy['ip']}:{proxy['port']} (Attempt {attempt+1}/3)")

        # Test proxy before launching browser
        if not await asyncio.to_thread(test_proxy, proxy['ip'], proxy['port']):
            print(f"⚠️ Proxy {proxy['ip']}:{proxy['port']} is unreachable, skipping...")
            continue

        proxy_url = f"http://{proxy['ip']}:{proxy['port']}"

        browser_args = [
            f'--proxy-server={proxy_url}',
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-blink-features=AutomationControlled',
            '--disable-features=IsolateOrigins,site-per-process',
            '--window-size=1920,1080',
        ]

        try:
            browser = await launch({
                'headless': True,
                'args': browser_args,
                'executablePath': CHROME_PATH,
                'ignoreHTTPSErrors': True,
            })

            page = await browser.newPage()

            # Proxy authentication
            await page.authenticate({
                'username': proxy['username'],
                'password': proxy['password']
            })

            await stealth(page)

            await page.setUserAgent(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )

            await page.goto(link, timeout=60000)
            await page.waitForSelector('body', timeout=10000)

            await asyncio.sleep(random.uniform(3, 5))

            for _ in range(random.randint(1, 3)):
                await page.evaluate("""() => { window.scrollBy(0, window.innerHeight * 0.5); }""")
                await asyncio.sleep(random.uniform(1, 2))

            await asyncio.sleep(random.uniform(3, 6))
            await browser.close()

            msg = f"✅ Boost successful for TEMU link: {link}"
            print(msg)
            if discord_channel:
                await discord_channel.send(msg)
            return  # ✅ Exit after success

        except Exception as e:
            error_msg = f"❌ Error boosting {link} with {proxy['ip']}:{proxy['port']}: {e}"
            print(error_msg)
            if discord_channel:
                await discord_channel.send(error_msg)

    print(f"❌ All proxy attempts failed for {link}")