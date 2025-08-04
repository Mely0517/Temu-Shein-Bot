import itertools

# ✅ Your IPRoyal authenticated proxies in the correct format for pyppeteer
proxies = [
    "http://PpCMxtvpv1VpA9te:8cFhbwxhl0vyO5Hg@geo.iproyal.com:12321",
    "http://PpCMxtvpv1VpA9te:8cFhbwxhl0vyO5Hg@geo.iproyal.com:12321",
    "http://PpCMxtvpv1VpA9te:8cFhbwxhl0vyO5Hg@geo.iproyal.com:12321",
    "http://PpCMxtvpv1VpA9te:8cFhbwxhl0vyO5Hg@geo.iproyal.com:12321",
    "http://PpCMxtvpv1VpA9te:8cFhbwxhl0vyO5Hg@geo.iproyal.com:12321",
    "http://PpCMxtvpv1VpA9te:8cFhbwxhl0vyO5Hg@geo.iproyal.com:12321",
    "http://PpCMxtvpv1VpA9te:8cFhbwxhl0vyO5Hg@geo.iproyal.com:12321",
    "http://PpCMxtvpv1VpA9te:8cFhbwxhl0vyO5Hg@geo.iproyal.com:12321",
    "http://PpCMxtvpv1VpA9te:8cFhbwxhl0vyO5Hg@geo.iproyal.com:12321",
    "http://PpCMxtvpv1VpA9te:8cFhbwxhl0vyO5Hg@geo.iproyal.com:12321"
]

proxy_cycle = itertools.cycle(proxies)

def get_next_proxy():
    return next(proxy_cycle)