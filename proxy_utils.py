import itertools

# List of proxies — format: ip:port or user:pass@ip:port if needed
proxies = [
    "123.45.67.89:8080",
    "98.76.54.32:8000",
    "username:password@111.222.333.444:3128",
    # Add more here
]

proxy_cycle = itertools.cycle(proxies)

def get_next_proxy():
    return next(proxy_cycle)
