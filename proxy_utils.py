import random

# List of proxies (add as many as you want)
PROXIES = [
    {
        "ip": "geo.iproyal.com",
        "port": "12321",
        "username": "melitza0517",
        "password": "PpCMxtvpv1VpA",
        "country": "US"
    },
    {
        "ip": "geo.iproyal.com",
        "port": "12321",
        "username": "melitza0517",
        "password": "PpCMxtvpv1VpA",
        "country": "US"
    },
    # Add more here (different endpoints or countries if you have them)
]

failed_proxies = set()  # Keeps track of failed proxies

def get_random_proxy():
    """Return a random working proxy that has not failed yet."""
    available = [p for p in PROXIES if proxy_to_str(p) not in failed_proxies]
    if not available:
        print("⚠️ No working proxies left — retrying all.")
        failed_proxies.clear()
        available = PROXIES
    return random.choice(available)

def mark_proxy_failed(proxy):
    """Mark a proxy as failed so it won't be used again this run."""
    failed_proxies.add(proxy_to_str(proxy))

def proxy_to_str(proxy):
    """Convert proxy dict to string for tracking."""
    return f"{proxy['ip']}:{proxy['port']}:{proxy['username']}:{proxy['password']}"