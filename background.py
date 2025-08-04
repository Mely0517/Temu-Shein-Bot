import asyncio
import discord  # ✅ Added so discord.utils.get works
from discord.ext import tasks
from shein import boost_shein_link
from temu import boost_temu_link

shein_links = set()
temu_links = set()
boosted_links = set()
boost_stats = {"shein": 0, "temu": 0}

def load_links():
    global shein_links, temu_links
    shein_links = set(open("shein_links.txt").read().splitlines())
    temu_links = set(open("temu_links.txt").read().splitlines())

def reload_links():
    load_links()

def get_boost_stats():
    return boost_stats

load_links()
try:
    boosted_links = set(open("boost_log.txt").read().splitlines())
except:
    boosted_links = set()

@tasks.loop(seconds=15)
async def background_boost_loop(bot):
    for link in list(shein_links):
        if link in boosted_links:
            continue
        channel = discord.utils.get(bot.get_all_channels(), name="general")  # or your channel name
        await boost_shein_link(link, channel)
        boosted_links.add(link)
        boost_stats["shein"] += 1
        open("boost_log.txt", "a").write(link + "\n")
        await asyncio.sleep(15)

    for link in list(temu_links):
        if link in boosted_links:
            continue
        channel = discord.utils.get(bot.get_all_channels(), name="general")
        await boost_temu_link(link, channel)
        boosted_links.add(link)
        boost_stats["temu"] += 1
        open("boost_log.txt", "a").write(link + "\n")
        await asyncio.sleep(15)