import asyncio
from pyppeteer import launch
from proxy_utils import get_random_proxy

async def boost_temu(link):
    try:
        proxy = get_random_proxy()
        browser = await launch({
            'headless': True,
            'args': [
                f'--proxy-server={proxy}',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--window-size=1920,1080'
            ]
        })
        page = await browser.newPage()
        await page.setUserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36")
        await page.goto(link, timeout=60000)
        await asyncio.sleep(8)  # Simulate time on page
        await browser.close()
        return f"✅ Temu visit complete for {link}"
    except Exception as e:
        return f"❌ Error with {link}: {e}"
