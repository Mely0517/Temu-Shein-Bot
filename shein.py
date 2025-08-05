import asyncio
import random
from pyppeteer import launch
from proxy_utils import get_random_proxy
from pyppeteer_stealth import stealth

MAX_RETRIES = 3  # Retry boosting up to 3 times if it fails

async def boost_shein_link(link, discord_channel=None):
    print(f"⏳ Starting SHEIN boost for: {link}")

    for attempt in range(1, MAX_RETRIES + 1):
        proxy = get_random_proxy()
        print(f"🌐 Using proxy {proxy['ip']}:{proxy['port']} (Attempt {attempt}/{MAX_RETRIES})")

        proxy_auth_url = f"http://{proxy['username']}:{proxy['password']}@{proxy['ip']}:{proxy['port']}"

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
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )

            await page.goto(link, timeout=60000)
            await page.waitForSelector('body', timeout=10000)

            # Simulate scrolling
            for _ in range(random.randint(1, 3)):
                await page.evaluate("""() => {
                    window.scrollBy(0, window.innerHeight * 0.5);
                }""")
                await asyncio.sleep(random.uniform(1, 2))

            await asyncio.sleep(random.uniform(3, 6))
            await browser.close()

            msg = f"✅ Boost successful for SHEIN link: {link}"
            print(msg)
            if discord_channel:
                await discord_channel.send(msg)
            return  # Success, stop retrying

        except Exception as e:
            error_msg = f"❌ Error with {link} on attempt {attempt}: {e}"
            print(error_msg)
            if discord_channel:
                await discord_channel.send(error_msg)
            await asyncio.sleep(2)  # Short wait before retry