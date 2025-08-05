import random

PROXIES = [
    {
        "ip": "geo.iproyal.com",
        "port": "12321",
        "username": "melitza0517",
        "password": "PpCMxtvpv1VpA",
        "country": "US"
    },
    # Add more proxies here if available
]

def get_random_proxy():
    return random.choice(PROXIES)