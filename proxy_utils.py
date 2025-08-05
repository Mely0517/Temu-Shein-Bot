import random

PROXIES = [
    {
        "ip": "geo.iproyal.com",
        "port": "12321",
        "username": "melitza0517",
        "password": "PpCMxtvpv1VpA",
        "country": "US"
    },
    # Add more proxies here if you have them
]

def get_random_proxy():
    """Returns a random proxy from the list."""
    return random.choice(PROXIES)