import random

PROXIES = [
    {
        "ip": "geo.iproyal.com",
        "port": "12321",
        "username": "perezjones.melitza@gmail.com",
        "password": "Mpj#1184",
        "country": "US"
    },
    # You can add more proxies here if needed
]

def get_random_proxy():
    return random.choice(PROXIES)