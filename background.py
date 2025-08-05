import asyncio
import random
import discord
from discord.ext import tasks
from shein import boost_shein_link
from temu import boost_temu_link

# Store links and stats
shein_links = set()
temu_links = set()
boosted_links = set()
boost_stats = {"shein": 0, "temu": 0}

# Load SHEIN & TEMU links from files
def load_links():
    global shein_links, temu_links
    try:
        shein_links = set(open("shein_links.txt").read().splitlines())
    except FileNotFoundError:
        shein_links = set()

    try:
        temu_links = set(open("temu_links.txt").read().splitlines())
    except FileNotFoundError:
        temu_links = set()

def reload_links():
    load_links()

def get_boost_stats():
    return boost_stats

# Load data at start
load_links()
try:
    boosted_links = set(open("boost_log.txt").read().splitlines())
except FileNotFoundError:
    boosted_links = set()

@tasks.loop(seconds=15)
async def background_boost_loop(bot):
    """ Continuously boosts links in the background """
    # Boost SHEIN links
    for idx, link in enumerate(list(shein_links), start=1):
        if link in boosted_links:
            continue

        channel = discord.utils.get(bot.get_all_channels(), name="general")
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
                await channel.send(f"❌ Failed to boost SHEIN link: {link} — {e}")

        await asyncio.sleep(random.uniform(10, 20))

    # Boost TEMU links
    for idx, link in enumerate(list(temu_links), start=1):
        if link in boosted_links:
            continue

        channel = discord.utils.get(bot.get_all_channels(), name="general")
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
                await channel.send(f"❌ Failed to boost TEMU link: {link} — {e}")

        await asyncio.sleep(random.uniform(10, 20))