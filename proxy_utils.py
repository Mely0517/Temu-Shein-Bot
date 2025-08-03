import random

# Replace with real rotating proxies if available
PROXY_LIST = [
    "http://161.186.166.60:9338",
    "http://125.119.185.110:7350",
    "http://144.149.111.58:4504",
    "http://160.194.146.64:1011",
    "http://120.190.38.113:7284",
    "http://254.159.255.5:6998",
    "http://244.34.145.133:8660",
    "http://121.126.87.224:4769",
    "http://201.45.26.194:5333",
    "http://215.201.166.239:6518"
]

def get_random_proxy():
    return random.choice(PROXY_LIST)
