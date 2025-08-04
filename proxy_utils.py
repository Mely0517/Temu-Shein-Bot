import itertools

# Your authenticated proxy credentials
PROXY_LIST = [
    "geo.iproyal.com:12321:PpCMxtvpv1VpA9te:8cFhbwxhl0vyO5Hg"
] * 10  # Use the same proxy 10x for rotation

proxy_cycle = itertools.cycle(PROXY_LIST)

def get_next_proxy():
    proxy = next(proxy_cycle)
    host, port, user, pwd = proxy.strip().split(":")
    return {
        "server": f"http://{host}:{port}",
        "username": user,
        "password": pwd
    }