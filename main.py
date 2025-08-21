# main.py
import os
import re
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

# Simple URL detector (grabs http/https up to whitespace)
URL_RE = re.compile(r'(https?://\S+)', re.IGNORECASE)


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


# Accept the entire remainder of the message (so captions/newlines work)
@bot.command(name="boost", help="Boost a SHEIN/TEMU link. Usage: !boost <url> or paste text with a url")
async def boost(ctx, *, link_text: str = ""):
    # Fallback: if parser gave us nothing, use the full message content
    if not link_text:
        link_text = ctx.message.content

    urls = URL_RE.findall(link_text)
    if not urls:
        await ctx.reply("❗ I didn’t see any link. Please send `!boost <url>` on one line or include a URL in your message.")
        return

    # Deduplicate while preserving order
    seen = set()
    unique_urls = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            unique_urls.append(u)

    await ctx.reply(f"✅ Found {len(unique_urls)} link(s). Starting boost…")

    # Lazy imports to avoid startup errors if one module fails
    from shein import boost_shein_link
    from temu import boost_temu_link

    for u in unique_urls:
        try:
            if "shein.com" in u:
                await ctx.send(f"🧑‍💻 SHEIN: working on {u}")
                await boost_shein_link(u, ctx.channel)
            elif "temu.com" in u:
                await ctx.send(f"🧑‍💻 TEMU: working on {u}")
                await boost_temu_link(u, ctx.channel)
            else:
                await ctx.send(f"❌ Skipping non-supported link: {u}")
        except Exception as e:
            await ctx.send(f"❌ Error with {u}: {e}")


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