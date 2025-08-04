import random

PROXIES = [
    {
        "ip": "geo.iproyal.com",
        "port": "12321",
        "username": "YOUR_USERNAME_HERE",  # 🔐 Replace this with your IPRoyal username
        "password": "PpCMxtvpv1VpA"
    },
]

def get_random_proxy():
    return random.choice(PROXIES)