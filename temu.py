import asyncio
import random
from pyppeteer import launch
from proxy_utils import get_random_proxy
from pyppeteer_stealth import stealth

MAX_RETRIES = 3  # Retry attempts

async def boost_temu_link(link, discord_channel=None):
    print(f"⏳ Starting TEMU boost for: {link}")

    for attempt in range(1, MAX_RETRIES + 1):
        proxy = get_random_proxy()
        proxy_server = f"{proxy['ip']}:{proxy['port']}"
        print(f"🌐 Using proxy {proxy_server} (Attempt {attempt}/{MAX_RETRIES})")

        browser_args = [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-blink-features=AutomationControlled',
            f'--proxy-server={proxy_server}',
            '--window-size=1920,1080',
        ]

        try:
            browser = await launch({
                'headless': True,
                'args': browser_args,
                'ignoreHTTPSErrors': True,
            })

            page = await browser.newPage()

            # Authenticate proxy if username/password provided
            if proxy.get("username") and proxy.get("password"):
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

            for _ in range(random.randint(1, 3)):
                await page.evaluate("""() => { window.scrollBy(0, window.innerHeight * 0.5); }""")
                await asyncio.sleep(random.uniform(1, 2))

            await asyncio.sleep(random.uniform(3, 6))
            await browser.close()

            msg = f"✅ Boost successful for TEMU link: {link}"
            print(msg)
            if discord_channel:
                await discord_channel.send(msg)
            return

        except Exception as e:
            error_msg = f"❌ Error boosting {link} with {proxy_server}: {e}"
            print(error_msg)
            if discord_channel:
                await discord_channel.send(error_msg)
            if attempt == MAX_RETRIES:
                print(f"⛔ Giving up on {link} after {MAX_RETRIES} attempts.")