# proxy_utils.py
import os
import random
from typing import Dict, List, Optional

DEFAULT_SCHEME = "http"

def _strip(s: Optional[str]) -> Optional[str]:
    return s.strip() if isinstance(s, str) else s

def _parse_proxy_line(line: str) -> Optional[Dict]:
    """
    Accepts formats:
      - host:port
      - host:port:username:password
      - username:password@host:port
      - http://username:password@host:port
      - socks5://user:pass@host:port  (scheme kept but you must support it in launch args)
    Returns dict: {ip, port, username, password, scheme}
    """
    if not line:
        return None

    raw = line.strip()
    if not raw or raw.startswith("#"):
        return None

    scheme = DEFAULT_SCHEME
    rest = raw

    # Extract scheme if present
    if "://" in raw:
        maybe_scheme, after = raw.split("://", 1)
        if maybe_scheme:
            scheme = maybe_scheme.lower()
        rest = after

    # Option 1: username:password@host:port
    if "@" in rest:
        creds, hostport = rest.rsplit("@", 1)
        if ":" not in hostport:
            return None
        user = creds.split(":", 1)[0] if ":" in creds else creds
        pw = creds.split(":", 1)[1] if ":" in creds else None
        host, port = hostport.split(":", 1)
        return {
            "ip": _strip(host),
            "port": _strip(port),
            "username": _strip(user) if user else None,
            "password": _strip(pw) if pw else None,
            "scheme": scheme or DEFAULT_SCHEME,
        }

    # Option 2: host:port(:username:password)?
    parts = rest.split(":")
    if len(parts) == 2:
        host, port = parts
        return {
            "ip": _strip(host),
            "port": _strip(port),
            "username": None,
            "password": None,
            "scheme": scheme or DEFAULT_SCHEME,
        }
    elif len(parts) == 4:
        host, port, user, pw = parts
        return {
            "ip": _strip(host),
            "port": _strip(port),
            "username": _strip(user),
            "password": _strip(pw),
            "scheme": scheme or DEFAULT_SCHEME,
        }

    # Anything else is unsupported
    return None


def _load_proxies_from_env_list() -> List[Dict]:
    """
    PROXY_LIST can be a multiline env var:
      PROXY_LIST="host:port\nhost:port:user:pass\nhttp://user:pass@host:port"
    """
    values = os.getenv("PROXY_LIST")
    if not values:
        return []
    proxies: List[Dict] = []
    for line in values.splitlines():
        p = _parse_proxy_line(line)
        if p:
            proxies.append(p)
    return proxies


def _load_proxies_from_file(path: str = "proxies.txt") -> List[Dict]:
    if not os.path.exists(path):
        return []
    proxies: List[Dict] = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                p = _parse_proxy_line(line)
                if p:
                    proxies.append(p)
    except Exception:
        pass
    return proxies


def _single_proxy_from_env() -> Optional[Dict]:
    """
    Fallback to single-proxy env vars:
      PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS
    """
    host = os.getenv("PROXY_HOST")
    port = os.getenv("PROXY_PORT")
    user = os.getenv("PROXY_USER")
    pw = os.getenv("PROXY_PASS")

    if host and port:
        return {
            "ip": host.strip(),
            "port": port.strip(),
            "username": user.strip() if user else None,
            "password": pw.strip() if pw else None,
            "scheme": DEFAULT_SCHEME,
        }
    return None


def _gather_all_proxies() -> List[Dict]:
    # Priority: PROXY_LIST (env) > proxies.txt (file) > single env proxy
    proxies = _load_proxies_from_env_list()
    if proxies:
        return proxies

    proxies = _load_proxies_from_file("proxies.txt")
    if proxies:
        return proxies

    single = _single_proxy_from_env()
    if single:
        return [single]

    return []


def get_random_proxy() -> Dict:
    """
    Returns a proxy dict with keys:
      ip, port, username (opt), password (opt), scheme (default 'http')

    Raises ValueError if nothing is configured.
    """
    proxies = _gather_all_proxies()
    if not proxies:
        raise ValueError(
            "No proxies configured. Set PROXY_LIST, create proxies.txt, or set PROXY_HOST/PROXY_PORT."
        )
    p = random.choice(proxies)
    # Normalize required keys for callers
    return {
        "ip": p.get("ip"),
        "port": str(p.get("port")),
        "username": p.get("username"),
        "password": p.get("password"),
        "scheme": p.get("scheme", DEFAULT_SCHEME),
    }