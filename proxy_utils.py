import random

# ✅ Proxy list (add more if you have them)
PROXIES = [
    {
        "ip": "geo.iproyal.com",
        "port": "12321",
        "username": "melitza0517",
        "password": "PpCMxtvpv1VpA",
        "country": "US"
    }
]

def get_random_proxy():
    """Return a random proxy from the list."""
    return random.choice(PROXIES)

async def test_proxy(proxy):
    """Test if a proxy is working before using it."""
    import aiohttp
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://httpbin.org/ip",
                proxy=f"http://{proxy['username']}:{proxy['password']}@{proxy['ip']}:{proxy['port']}",
                timeout=10
            ) as resp:
                if resp.status == 200:
                    print(f"✅ Proxy {proxy['ip']}:{proxy['port']} is working.")
                    return True
    except Exception as e:
        print(f"❌ Proxy {proxy['ip']}:{proxy['port']} failed: {e}")
    return False