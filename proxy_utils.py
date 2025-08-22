# proxy_utils.py
import os
import random
from typing import Dict, List, Optional

DEFAULT_SCHEME = "http"

def _strip(s: Optional[str]) -> Optional[str]:
    return s.strip() if isinstance(s, str) else s

def _parse_proxy_string(proxy_str: str) -> Optional[Dict]:
    """
    Parse a single proxy string like:
      http://user:pass@host:port
      socks5://user:pass@host:port
      host:port
      host:port:user:pass
      user:pass@host:port
    Returns dict {ip, port, username, password, scheme}
    """
    if not proxy_str:
        return None

    raw = proxy_str.strip()
    if not raw or raw.startswith("#"):
        return None

    scheme = DEFAULT_SCHEME
    rest = raw

    # Scheme present?
    if "://" in raw:
        scheme, rest = raw.split("://", 1)
        scheme = scheme.lower()

    # user:pass@host:port
    if "@" in rest:
        creds, hostport = rest.split("@", 1)
        if ":" not in hostport:
            return None
        host, port = hostport.split(":", 1)
        user, pw = (creds.split(":", 1) + [None])[:2]
        return {
            "ip": _strip(host),
            "port": _strip(port),
            "username": _strip(user),
            "password": _strip(pw),
            "scheme": scheme,
        }

    # host:port(:user:pass)?
    parts = rest.split(":")
    if len(parts) == 2:
        host, port = parts
        return {
            "ip": _strip(host),
            "port": _strip(port),
            "username": None,
            "password": None,
            "scheme": scheme,
        }
    if len(parts) == 4:
        host, port, user, pw = parts
        return {
            "ip": _strip(host),
            "port": _strip(port),
            "username": _strip(user),
            "password": _strip(pw),
            "scheme": scheme,
        }

    return None


def get_random_proxy() -> Dict:
    """
    Return one proxy dict shaped like:
      {ip, port, username, password, scheme}
    Priority:
      1. FULL_PROXY env (single string)
      2. PROXY_LIST env (multiline)
      3. proxies.txt file
      4. Split env vars (PROXY_HOST/PORT/USER/PASS/SCHEME)
    """
    # 1. FULL_PROXY
    full_proxy = os.getenv("FULL_PROXY")
    if full_proxy:
        parsed = _parse_proxy_string(full_proxy)
        if parsed:
            return parsed

    # 2. PROXY_LIST
    proxy_list = os.getenv("PROXY_LIST")
    if proxy_list:
        candidates = []
        for line in proxy_list.splitlines():
            parsed = _parse_proxy_string(line)
            if parsed:
                candidates.append(parsed)
        if candidates:
            return random.choice(candidates)

    # 3. proxies.txt
    if os.path.exists("proxies.txt"):
        candidates = []
        with open("proxies.txt", "r", encoding="utf-8") as f:
            for line in f:
                parsed = _parse_proxy_string(line)
                if parsed:
                    candidates.append(parsed)
        if candidates:
            return random.choice(candidates)

    # 4. Split env vars
    host = os.getenv("PROXY_HOST")
    port = os.getenv("PROXY_PORT")
    if host and port:
        return {
            "ip": host.strip(),
            "port": port.strip(),
            "username": _strip(os.getenv("PROXY_USER")),
            "password": _strip(os.getenv("PROXY_PASS")),
            "scheme": os.getenv("PROXY_SCHEME", DEFAULT_SCHEME).lower(),
        }

    raise ValueError("❌ No proxies configured! Set FULL_PROXY, PROXY_LIST, proxies.txt, or PROXY_HOST/PORT.")