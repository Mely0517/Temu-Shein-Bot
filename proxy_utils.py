# proxy_utils.py
import os, random
from typing import Dict, Optional

DEFAULT_SCHEME = os.getenv("PROXY_SCHEME", "http").lower()  # http or socks5

def _strip(s: Optional[str]) -> Optional[str]:
    return s.strip() if isinstance(s, str) else s

def _parse(line: str) -> Optional[Dict]:
    """
    Accepts:
      host:port
      host:port:username:password
      username:password@host:port
      http://user:pass@host:port
      socks5://user:pass@host:port
    Returns: {ip, port, username, password, scheme}
    """
    if not line: return None
    raw = line.strip()
    if not raw or raw.startswith("#"): return None

    scheme = DEFAULT_SCHEME
    rest = raw

    if "://" in raw:
        scheme, rest = raw.split("://", 1)
        scheme = scheme.lower()

    if "@" in rest:
        creds, hostport = rest.split("@", 1)
        if ":" not in hostport: return None
        host, port = hostport.split(":", 1)
        user, pw = (creds.split(":", 1) + [None])[:2]
        return {"ip": _strip(host), "port": _strip(port),
                "username": _strip(user), "password": _strip(pw),
                "scheme": scheme}

    parts = rest.split(":")
    if len(parts) == 2:
        host, port = parts
        return {"ip": _strip(host), "port": _strip(port),
                "username": None, "password": None, "scheme": scheme}
    if len(parts) == 4:
        host, port, user, pw = parts
        return {"ip": _strip(host), "port": _strip(port),
                "username": _strip(user), "password": _strip(pw),
                "scheme": scheme}
    return None

def _load_list_from_env():
    env = os.getenv("PROXY_LIST")
    if not env: return []
    out = []
    for line in env.splitlines():
        p = _parse(line)
        if p: out.append(p)
    return out

def _load_from_file(path="proxies.txt"):
    if not os.path.exists(path): return []
    out = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            p = _parse(line)
            if p: out.append(p)
    return out

def get_random_proxy() -> Dict:
    # Priority: PROXY_LIST (env) → proxies.txt
    candidates = _load_list_from_env()
    if not candidates:
        candidates = _load_from_file("proxies.txt")
    if not candidates:
        raise ValueError("❌ No proxies found. Add lines to proxies.txt or set PROXY_LIST.")
    p = random.choice(candidates)
    # normalize port to str
    p["port"] = str(p["port"])
    if not p.get("scheme"):
        p["scheme"] = DEFAULT_SCHEME
    return p