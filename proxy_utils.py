import itertools

# List of proxies — format: ip:port or user:pass@ip:port if needed
proxies = [
    "http://103.172.70.45:7070",
    "http://138.2.86.245:3128",
    "http://47.88.11.3:8080",
    # Replace with working ones from ProxyScrape, BrightData, etc.
]

proxy_cycle = itertools.cycle(proxies)

def get_next_proxy():
    return next(proxy_cycle)
