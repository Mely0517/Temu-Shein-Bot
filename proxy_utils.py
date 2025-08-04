import itertools

# Your authenticated proxies in this format: host:port:username:password
raw_proxies = [
    "geo.iproyal.com:12321:PpCMxtvpv1VpA9te:8cFhbwxhl0vyO5Hg",
    "geo.iproyal.com:12321:PpCMxtvpv1VpA9te:8cFhbwxhl0vyO5Hg",
    "geo.iproyal.com:12321:PpCMxtvpv1VpA9te:8cFhbwxhl0vyO5Hg",
    "geo.iproyal.com:12321:PpCMxtvpv1VpA9te:8cFhbwxhl0vyO5Hg",
    "geo.iproyal.com:12321:PpCMxtvpv1VpA9te:8cFhbwxhl0vyO5Hg",
]

proxy_cycle = itertools.cycle(raw_proxies)

def get_next_proxy():
    proxy = next(proxy_cycle)
    parts = proxy.strip().split(":")
    if len(parts) != 4:
        raise ValueError(f"Invalid proxy format: {proxy}")
    
    host, port, user, pwd = parts
    proxy_url = f"http://{user}:{pwd}@{host}:{port}"
    
    return {
        "server": f"http://{host}:{port}",
        "username": user,
        "password": pwd,
        "pyppeteer_proxy": proxy_url
    }