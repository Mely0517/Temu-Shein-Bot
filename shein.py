import asyncio
from pyppeteer import launch
from proxy_utils import get_random_proxy

async def visit_shein_referral(url):
    proxy = get_random_proxy()
    print(f"🟡 Using proxy: {proxy}")

    browser = await launch({
        "headless": True,
        "args": [
            f'--proxy-server={proxy}',
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu',
            '--window-size=1280,800',
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        ]
    })

    page = await browser.newPage()

    try:
        await page.goto(url, timeout=30000)
        await asyncio.sleep(5)
        await page.mouse.move(200, 200)
        await page.mouse.click(200, 200)
        await asyncio.sleep(3)
        print(f"✅ Visited SHEIN referral: {url}")
    except Exception as e:
        print(f"❌ SHEIN error: {e}")
    finally:
        await browser.close()
