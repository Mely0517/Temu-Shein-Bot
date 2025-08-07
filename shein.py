import asyncio
from pyppeteer import launch
from pyppeteer_stealth import stealth
import random
import string

# ✅ Replace these with your actual SHEIN links
SHEIN_LINKS = [
    "https://onelink.shein.com/15/4wo1q068xvyy",
    # add more if needed
]

# ✅ Your proxy credentials
PROXY_HOST = "geo.iproyal.com"
PROXY_PORT = "12321"
PROXY_USER = "YOUR_PROXY_USERNAME"
PROXY_PASS = "YOUR_PROXY_PASSWORD"

# Function to create a random user-agent string
def get_user_agent():
    return (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    )

async def boost_shein_link(link):
    proxy = f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}"
    print(f"🌐 Using proxy {PROXY_HOST}:{PROXY_PORT}")
    try:
        browser = await launch({
            'headless': True,
            'args': [
                f'--proxy-server=http://{PROXY_HOST}:{PROXY_PORT}',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--window-size=1920,1080'
            ],
        })

        page = await browser.newPage()

        # Authenticate proxy
        await page.authenticate({
            'username': PROXY_USER,
            'password': PROXY_PASS
        })

        # Stealth and user-agent
        await stealth(page)
        await page.setUserAgent(get_user_agent())

        await page.goto(link, timeout=60000)
        await asyncio.sleep(random.uniform(5, 10))  # simulate reading time
        print(f"✅ Boosted SHEIN link: {link}")
        await browser.close()
    except Exception as e:
        print(f"❌ Error with {link}: {e}")

async def run_all():
    for link in SHEIN_LINKS:
        await boost_shein_link(link)
        await asyncio.sleep(2)  # slight delay between boosts

if __name__ == "__main__":
    asyncio.run(run_all())