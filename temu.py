import asyncio
from pyppeteer import launch
import random
from proxy_utils import get_random_proxy
from pyppeteer_stealth import stealth

MAX_RETRIES = 3  # Retry each link this many times before giving up

async def boost_temu_link(link, discord_channel=None):
    print(f"⏳ Starting TEMU boost for: {link}")
    
    for attempt in range(1, MAX_RETRIES + 1):
        proxy = get_random_proxy()
        proxy_auth_url = f"http://{proxy['username']}:{proxy['password']}@{proxy['ip']}:{proxy['port']}"
        print(f"🌐 Using proxy {proxy['ip']}:{proxy['port']} (Attempt {attempt}/{MAX_RETRIES})")

        browser_args = [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-blink-features=AutomationControlled',
            f'--proxy-server={proxy_auth_url}',
            '--window-size=1920,1080',
        ]

        try:
            browser = await launch({
                'headless': True,
                'args': browser_args,
                'ignoreHTTPSErrors': True,
            })

            page = await browser.newPage()
            await stealth(page)

            await page.setUserAgent(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
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
            return  # Success → exit function

        except Exception as e:
            error_msg = f"❌ Error with {link} on attempt {attempt}: {e}"
            print(error_msg)
            if discord_channel:
                await discord_channel.send(error_msg)
            await asyncio.sleep(2)

    fail_msg = f"⛔ Failed to boost TEMU link after {MAX_RETRIES} attempts: {link}"
    print(fail_msg)
    if discord_channel:
        await discord_channel.send(fail_msg)