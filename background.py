# background.py
import os
import asyncio
from discord.ext import tasks

from shein import boost_shein_link
from temu import boost_temu_link

# Where to store the links
SHEIN_FILE = "shein_links.txt"
TEMU_FILE = "temu_links.txt"

# Track stats across runtime
_stats = {"shein": 0, "temu": 0}

# Keep a set of links that already failed (don’t retry them every loop)
_failed_links = set()

def _load_links(path: str):
    """Read non-empty, non-duplicate lines from a file."""
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f if l.strip()]
    # Remove comments and duplicates
    return list(dict.fromkeys([l for l in lines if not l.startswith("#")]))


def get_boost_stats():
    return dict(_stats)


def reload_links():
    # Just a dummy reset — will be reloaded on next loop
    _failed_links.clear()
    print("🔄 Links reloaded (failures cleared).")


@tasks.loop(minutes=15)  # run every 15 min; adjust if you want faster
async def background_boost_loop(bot):
    """Continuously run boosts in the background."""

    shein_links = _load_links(SHEIN_FILE)
    temu_links = _load_links(TEMU_FILE)

    if not shein_links and not temu_links:
        print("📭 No links found in shein_links.txt or temu_links.txt")
        return

    print(f"🔁 Background loop: {len(shein_links)} SHEIN, {len(temu_links)} TEMU links loaded.")

    for link in shein_links:
        if link in _failed_links:
            continue
        try:
            await boost_shein_link(link)
            _stats["shein"] += 1
        except Exception as e:
            print(f"[background] SHEIN link failed: {link} ({e})")
            _failed_links.add(link)

    for link in temu_links:
        if link in _failed_links:
            continue
        try:
            await boost_temu_link(link)
            _stats["temu"] += 1
        except Exception as e:
            print(f"[background] TEMU link failed: {link} ({e})")
            _failed_links.add(link)

    print(f"✅ Background loop finished. Stats so far: {_stats}")