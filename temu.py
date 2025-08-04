from pyppeteer import launch
from pyppeteer_stealth import stealth

async def boost_temu_link(link, proxy):
    browser = await launch(
        headless=True,
        args=[
            f'--proxy-server={proxy["server"]}',
            "--no-sandbox", "--disable-setuid-sandbox"
        ]
    )
    page = await browser.newPage()
    await page.authenticate({
        'username': proxy["username"],
        'password': proxy["password"]
    })
    await stealth(page)
    await page.goto(link, timeout=60000)
    await page.waitForTimeout(5000)
    await browser.close()