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
    """Loads SHEIN and TEMU links from text files."""
    global shein_links, temu_links
    try:
        shein_links = set(filter(None, open("shein_links.txt").read().splitlines()))
    except FileNotFoundError:
        shein_links = set()
    try:
        temu_links = set(filter(None, open("temu_links.txt").read().splitlines()))
    except FileNotFoundError:
        temu_links = set()

def reload_links():
    load_links()

def get_boost_stats():
    return boost_stats

# Load initial links
load_links()
try:
    boosted_links = set(open("boost_log.txt").read().splitlines())
except FileNotFoundError:
    boosted_links = set()

@tasks.loop(seconds=20)
async def background_boost_loop(bot):
    """Runs in the background to boost SHEIN and TEMU links automatically."""
    channel = discord.utils.get(bot.get_all_channels(), name="general")  # Change to your channel name if needed

    # Boost SHEIN links
    for idx, link in enumerate(list(shein_links), start=1):
        if link in boosted_links:
            continue
        if channel:
            await channel.send(f"📢 Boosting SHEIN link ({idx}/{len(shein_links)}): {link}")

        try:
            await boost_shein_link(link, channel)
            boosted_links.add(link)
            boost_stats["shein"] += 1
            open("boost_log.txt", "a").write(link + "\n")
        except Exception as e:
            open("boost_failures.txt", "a").write(f"{link} | Error: {e}\n")
            if channel:
                await channel.send(f"❌ SHEIN boost failed: {link} — {e}")

        await asyncio.sleep(random.uniform(10, 25))  # Random delay between boosts

    # Boost TEMU links
    for idx, link in enumerate(list(temu_links), start=1):
        if link in boosted_links:
            continue
        if channel:
            await channel.send(f"📢 Boosting TEMU link ({idx}/{len(temu_links)}): {link}")

        try:
            await boost_temu_link(link, channel)
            boosted_links.add(link)
            boost_stats["temu"] += 1
            open("boost_log.txt", "a").write(link + "\n")
        except Exception as e:
            open("boost_failures.txt", "a").write(f"{link} | Error: {e}\n")
            if channel:
                await channel.send(f"❌ TEMU boost failed: {link} — {e}")

        await asyncio.sleep(random.uniform(10, 25))  # Random delay between boosts