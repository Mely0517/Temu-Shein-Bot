import asyncio
import random
from pyppeteer import launch
from proxy_utils import get_random_proxy

async def boost_shein(ctx, link=None):
    url = link or "https://onelink.shein.com/15/4vzpagy20nbj"
    try:
        proxy = get_random_proxy()
        browser = await launch({
            "headless": True,
            "args": [
                f'--proxy-server={proxy}',
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--disable-infobars',
                '--window-size=1920,1080',
                f'--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
            ]
        })
        page = await browser.newPage()
        await page.goto(url, timeout=60000)
        await asyncio.sleep(random.randint(5, 9))
        await page.evaluate('window.scrollBy(0, window.innerHeight)')
        await asyncio.sleep(random.randint(2, 4))
        await browser.close()
        await ctx.send(f"✅ Boosted SHEIN link: {url}")
    except Exception as e:
        await ctx.send(f"❌ Error with {url}: {e}")
