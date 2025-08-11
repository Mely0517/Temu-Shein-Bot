# main.py
import os
import discord
from discord.ext import commands
from background import background_boost_loop, get_boost_stats, reload_links

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
ADMIN_ID = os.getenv("DISCORD_ADMIN_ID")  # optional: restrict !status / !refresh

if not TOKEN:
    raise ValueError("❌ DISCORD_BOT_TOKEN environment variable not set!")

intents = discord.Intents.default()
intents.message_content = True  # requires Message Content Intent enabled in Dev Portal
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (id={bot.user.id})")
    # Start background loop once
    if not background_boost_loop.is_running():
        try:
            background_boost_loop.start(bot)
            print("🔁 background_boost_loop started")
        except RuntimeError as e:
            print(f"⚠️ background_boost_loop already running? {e}")


@bot.event
async def on_disconnect():
    print("⚠️ Discord gateway disconnected (clean close or network blip). "
          "discord.py will auto-reconnect...")


@bot.event
async def on_resumed():
    print("✅ Discord gateway session resumed successfully.")


@bot.command()
async def boost(ctx, link: str):
    await ctx.send(f"🚀 Boosting: {link}")
    # Lazy import to avoid startup errors if one module fails
    from shein import boost_shein_link
    from temu import boost_temu_link

    if "shein.com" in link:
        await boost_shein_link(link, ctx.channel)
    elif "temu.com" in link:
        await boost_temu_link(link, ctx.channel)
    else:
        await ctx.send("❌ Invalid link. Use a SHEIN or TEMU link.")


@bot.command()
async def status(ctx):
    if ADMIN_ID and str(ctx.author.id) != ADMIN_ID:
        return await ctx.send("⛔ Admin only.")
    stats = get_boost_stats()
    await ctx.send(f"📊 Boosted {stats['shein']} SHEIN links and {stats['temu']} TEMU links so far.")


@bot.command()
async def refresh(ctx):
    if ADMIN_ID and str(ctx.author.id) != ADMIN_ID:
        return await ctx.send("⛔ Admin only.")
    reload_links()
    await ctx.send("🔄 Link files reloaded.")


# Explicit reconnect (default is True, but we set it to be clear)
bot.run(TOKEN, reconnect=True)