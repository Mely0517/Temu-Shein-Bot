# background.py
import os
import asyncio
import random
import discord
from discord.ext import tasks
from shein import boost_shein_link
from temu import boost_temu_link

shein_links = set()
temu_links = set()
boosted_links = set()
boost_stats = {"shein": 0, "temu": 0}

def load_links():
    """Load links from text files into sets."""
    global shein_links, temu_links
    shein_links = set()
    temu_links = set()
    if os.path.exists("shein_links.txt"):
        with open("shein_links.txt", "r", encoding="utf-8") as f:
            shein_links = {ln.strip() for ln in f if ln.strip()}
    if os.path.exists("temu_links.txt"):
        with open("temu_links.txt", "r", encoding="utf-8") as f:
            temu_links = {ln.strip() for ln in f if ln.strip()}

def reload_links():
    load_links()

def get_boost_stats():
    return boost_stats

# init
load_links()
if os.path.exists("boost_log.txt"):
    with open("boost_log.txt", "r", encoding="utf-8") as f:
        boosted_links = {ln.strip() for ln in f if ln.strip()}

@tasks.loop(seconds=15)
async def background_boost_loop(bot):
    """Continuously works through lists, sending updates to a 'general' channel if it exists."""
    # find a channel named 'general' (change if yours is different)
    channel = None
    for c in bot.get_all_channels():
        if isinstance(c, discord.TextChannel) and c.name.lower() == "general":
            channel = c
            break

    # SHEIN
    shein_total = len(shein_links)
    for idx, link in enumerate(list(shein_links), start=1):
        if link in boosted_links:
            continue

        if channel:
            await channel.send(f"🧷 SHEIN ({idx}/{shein_total}): {link}")

        try:
            await boost_shein_link(link, channel)
            boosted_links.add(link)
            boost_stats["shein"] += 1
            with open("boost_log.txt", "a", encoding="utf-8") as f:
                f.write(link + "\n")
        except Exception as e:
            with open("boost_failures.txt", "a", encoding="utf-8") as f:
                f.write(f"{link} | Error: {e}\n")
            if channel:
                await channel.send(f"❌ SHEIN fail: {e}")

        await asyncio.sleep(random.uniform(10, 20))  # human-ish pacing

    # TEMU
    temu_total = len(temu_links)
    for idx, link in enumerate(list(temu_links), start=1):
        if link in boosted_links:
            continue

        if channel:
            await channel.send(f"🧷 TEMU ({idx}/{temu_total}): {link}")

        try:
            await boost_temu_link(link, channel)
            boosted_links.add(link)
            boost_stats["temu"] += 1
            with open("boost_log.txt", "a", encoding="utf-8") as f:
                f.write(link + "\n")
        except Exception as e:
            with open("boost_failures.txt", "a", encoding="utf-8") as f:
                f.write(f"{link} | Error: {e}\n")
            if channel:
                await channel.send(f"❌ TEMU fail: {e}")

        await asyncio.sleep(random.uniform(10, 20))