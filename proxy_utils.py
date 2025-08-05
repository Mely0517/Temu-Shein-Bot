import random

# ✅ List of authenticated proxies
PROXIES = [
    {
        "ip": "geo.iproyal.com",
        "port": "12321",
        "username": "melitza0517",
        "password": "PpCMxtvpv1VpA",
        "country": "US"
    },
    # Add more if you have them
]

def get_random_proxy():
    """Returns a random proxy from the list."""
    return random.choice(PROXIES)

async def test_proxy(proxy):
    """Tests if a proxy is working (optional check)."""
    import aiohttp
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.ipify.org?format=json",
                                   proxy=f"http://{proxy['username']}:{proxy['password']}@{proxy['ip']}:{proxy['port']}",
                                   timeout=10) as resp:
                data = await resp.json()
                print(f"✅ Proxy working: {data['ip']}")
                return True
    except Exception as e:
        print(f"❌ Proxy failed: {proxy['ip']}:{proxy['port']} — {e}")
        return False