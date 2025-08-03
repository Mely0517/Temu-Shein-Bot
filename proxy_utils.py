import itertools

# ✅ Working HTTP proxies for testing (you can replace with premium ones)
# Format must be either http://ip:port or http://user:pass@ip:port
proxies = [
    "http://103.172.70.45:7070",
    "http://47.88.11.3:8080",
    "http://138.2.86.245:3128",
    "http://207.2.120.117:80",
    "http://193.123.103.34:8080",
    # Add more here
]

# 🔁 Create an infinite cycle of proxies
proxy_cycle = itertools.cycle(proxies)

# ✅ Get the next proxy in the list (rotates forever)
def get_next_proxy():
    return next(proxy_cycle)