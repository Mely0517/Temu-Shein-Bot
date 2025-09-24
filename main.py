# main.py
import os
import re
import discord
from discord.ext import commands
from background import background_boost_loop, get_boost_stats, reload_links

# Use ONE env var name and set it in Render
TOKEN = os.getenv("DISCORD_BOT_TOKEN")  # Set this in Render → Environment
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


@bot.command(name="boost", help="Boost a SHEIN/TEMU link. Usage: !boost <url> or paste text with a url")
async def boost(ctx, *, link_text: str = ""):
    # If nothing passed, use raw message
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

    # Correct lazy imports — use our boosters from boost.py
    from boost import boost_shein_link, boost_temu_link

    for u in unique_urls:
        try:
            if "shein.com" in u:
                await ctx.send(f"🧑‍💻 SHEIN: working on {u}")
                msg = await boost_shein_link(u)  # returns a short status string
                await ctx.send(f"➡️ {msg}")
            elif "temu.com" in u:
                await ctx.send(f"🧑‍💻 TEMU: working on {u}")
                msg = await boost_temu_link(u)
                await ctx.send(f"➡️ {msg}")
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


# Explicit reconnect (default True)
bot.run(TOKEN, reconnect=True)