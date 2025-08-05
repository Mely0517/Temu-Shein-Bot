import asyncio
import random
from pyppeteer import launch
from proxy_utils import get_random_proxy
from pyppeteer_stealth import stealth

async def boost_temu_link(link, discord_channel=None):
    print(f"⏳ Starting TEMU boost for: {link}")
    
    # Try boosting with up to 3 retries if proxy fails
    for attempt in range(1, 3 + 1):
        proxy = get_random_proxy()
        print(f"🌐 Using proxy {proxy['ip']}:{proxy['port']} (Attempt {attempt}/3)")

        proxy_auth = f"{proxy['username']}:{proxy['password']}@{proxy['ip']}:{proxy['port']}"
        proxy_server = f"http://{proxy['ip']}:{proxy['port']}"

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

            # Authenticate proxy if needed
            if proxy.get("username") and proxy.get("password"):
                await page.authenticate({
                    'username': proxy['username'],
                    'password': proxy['password']
                })

            await stealth(page)

            # Randomized user agent to avoid detection
            await page.setUserAgent(
                f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                f"(KHTML, like Gecko) Chrome/{random.randint(100,120)}.0.0.0 Safari/537.36"
            )

            await page.goto(link, timeout=60000)
            await page.waitForSelector('body', timeout=10000)

            # Randomized scrolling to simulate human behavior
            for _ in range(random.randint(2, 5)):
                await page.evaluate("() => window.scrollBy(0, window.innerHeight * 0.5)")
                await asyncio.sleep(random.uniform(1, 2))

            # Short wait before closing
            await asyncio.sleep(random.uniform(2, 4))

            await browser.close()

            msg = f"✅ Boost successful for TEMU link: {link}"
            print(msg)
            if discord_channel:
                await discord_channel.send(msg)
            return  # Exit if successful

        except Exception as e:
            error_msg = f"❌ Error with {link} on attempt {attempt}: {e}"
            print(error_msg)
            if discord_channel:
                await discord_channel.send(error_msg)

            try:
                await browser.close()
            except:
                pass

            await asyncio.sleep(3)  # Wait before retry

    # If all attempts fail
    fail_msg = f"❌ Failed to boost TEMU link after 3 attempts: {link}"
    print(fail_msg)
    if discord_channel:
        await discord_channel.send(fail_msg)