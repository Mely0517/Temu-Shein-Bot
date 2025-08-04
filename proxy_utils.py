import random

PROXIES = [
    {
        "ip": "geo.iproyal.com",
        "port": "12321",
        "username": "YOUR_USERNAME_HERE",  # 🔐 Replace with your real IPRoyal username
        "password": "PpCMxtvpv1VpA"
    },
]

def get_random_proxy():
    return random.choice(PROXIES)