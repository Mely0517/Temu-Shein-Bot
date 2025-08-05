import asyncio
from pyppeteer import launch
import random
from proxy_utils import get_random_proxy
from pyppeteer_stealth import stealth

async def boost_shein_link(link, discord_channel=None):
    for attempt in range(1, 4):  # Retry up to 3 times
        proxy = get_random_proxy()
        proxy_address = f"{proxy['ip']}:{proxy['port']}"
        print(f"🌐 Using proxy {proxy_address} (Attempt {attempt}/3)")

        try:
            browser_args = [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-blink-features=AutomationControlled',
                f'--proxy-server={proxy_address}',
                '--window-size=1920,1080',
            ]

            browser = await launch({
                'headless': True,
                'args': browser_args,
                'ignoreHTTPSErrors': True,
            })

            page = await browser.newPage()
            await stealth(page)

            # Authenticate proxy
            await page.authenticate({
                "username": proxy["username"],
                "password": proxy["password"]
            })

            await page.setUserAgent(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )

            await page.goto(link, timeout=60000)
            await page.waitForSelector('body', timeout=10000)

            # Scroll like a human
            for _ in range(random.randint(1, 3)):
                await page.evaluate("() => window.scrollBy(0, window.innerHeight * 0.5)")
                await asyncio.sleep(random.uniform(1, 2))

            # Click claim button if present
            try:
                claim_button = await page.waitForSelector('button, a', timeout=5000)
                if claim_button:
                    await claim_button.click()
                    print("✅ Clicked claim button")
            except:
                print("⚠️ No claim button found")

            await asyncio.sleep(random.uniform(3, 6))
            await browser.close()

            msg = f"✅ Boost successful for SHEIN link: {link}"
            print(msg)
            if discord_channel:
                await discord_channel.send(msg)
            return  # Exit after success

        except Exception as e:
            error_msg = f"❌ Error boosting {link} with {proxy_address}: {e}"
            print(error_msg)
            if discord_channel:
                await discord_channel.send(error_msg)
            await asyncio.sleep(2)

    # All retries failed
    fail_msg = f"❌ All proxy attempts failed for {link}"
    print(fail_msg)
    if discord_channel:
        await discord_channel.send(fail_msg)