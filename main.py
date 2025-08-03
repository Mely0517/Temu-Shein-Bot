import discord
from discord.ext import commands, tasks
import asyncio
from temu import boost_temu_link
from shein import boost_shein_link
from proxy_utils import get_next_proxy
import os

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Files for background boosting
temu_links_file = "temu_links.txt"
shein_links_file = "shein_links.txt"

@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user}')
    background_boost.start()

@bot.command()
async def boost(ctx, *, link: str):
    await ctx.send(f"🔄 Boosting: {link}")
    try:
        proxy = get_next_proxy()
        if "temu.com" in link:
            await boost_temu_link(link, proxy)
        elif "shein.com" in link:
            await boost_shein_link(link, proxy)
        else:
            await ctx.send("❌ Unsupported link format.")
            return
        await ctx.send(f"✅ Successfully boosted: {link}")
    except Exception as e:
        await ctx.send(f"❌ Error with {link}: {str(e)}")

@bot.command()
async def ping(ctx):
    await ctx.send("🏓 Pong! The bot is alive.")

@tasks.loop(seconds=60)
async def background_boost():
    try:
        with open(temu_links_file, "r") as tf:
            temu_links = [l.strip() for l in tf if l.strip()]
        with open(shein_links_file, "r") as sf:
            shein_links = [l.strip() for l in sf if l.strip()]

        all_links = []
        for t, s in zip(temu_links, shein_links):
            all_links.append(t)
            all_links.append(s)
        leftover = temu_links[len(shein_links):] if len(temu_links) > len(shein_links) else shein_links[len(temu_links):]
        all_links += leftover

        for link in all_links:
            proxy = get_next_proxy()
            try:
                if "temu.com" in link:
                    await boost_temu_link(link, proxy)
                elif "shein.com" in link:
                    await boost_shein_link(link, proxy)
                else:
                    print(f"❌ Skipped invalid link: {link}")
                await asyncio.sleep(10)
            except Exception as e:
                print(f"❌ Background boost error for {link}: {e}")
    except Exception as e:
        print(f"❌ Error in background_boost task: {e}")

# ✅ Securely read Discord token from environment
token = os.environ.get("DISCORD_TOKEN")
if not token:
    raise ValueError("❌ DISCORD_TOKEN not found in environment variables.")
bot.run(token)