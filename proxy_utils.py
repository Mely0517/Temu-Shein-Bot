import random

# List of proxies
PROXIES = [
    {
        "ip": "geo.iproyal.com",
        "port": "12321",
        "username": "melitza0517",
        "password": "PpCMxtvpv1VpA",
        "country": "US"
    },
    # You can add more proxies here...
]

# Keep track of unused proxies in memory
_unused_proxies = PROXIES.copy()

def get_random_proxy():
    """
    Returns a random proxy without repeating until all proxies are used.
    Once all proxies are used, it resets the list.
    """
    global _unused_proxies
    if not _unused_proxies:
        _unused_proxies = PROXIES.copy()
        print("♻️ Proxy list reset — starting over.")

    proxy = random.choice(_unused_proxies)
    _unused_proxies.remove(proxy)  # Remove so it won't be reused immediately
    return proxy