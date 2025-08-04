import asyncio
from pyppeteer import launch
from pyppeteer_stealth import stealth

async def boost_temu_link(link: str, proxy: str = None):
    proxy_auth = None
    args = ['--no-sandbox']

    if proxy and "@" in proxy:
        creds, ip_port = proxy.split("@")
        user, pwd = creds.split(":")
        proxy_host = ip_port.replace("http://", "")
        args.append(f'--proxy-server={proxy_host}')
        proxy_auth = {"username": user, "password": pwd}
    elif proxy:
        args.append(f'--proxy-server={proxy}')

    browser = await launch(headless=True, args=args, handleSIGINT=False, handleSIGTERM=False, handleSIGHUP=False)
    try:
        page = await browser.newPage()
        if proxy_auth:
            await page.authenticate(proxy_auth)
        await stealth(page)

        await page.setUserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")
        await page.goto(link, timeout=60000)

        await asyncio.sleep(5)
        await page.mouse.move(200, 200)
        await page.mouse.click(200, 200)
        await asyncio.sleep(3)
        await page.evaluate('window.scrollBy(0, 500)')
        await asyncio.sleep(2)
        await page.evaluate('window.scrollBy(0, 800)')
        await asyncio.sleep(5)
    finally:
        await browser.close()