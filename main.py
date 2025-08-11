# main.py
import os
import discord
from discord.ext import commands
from background import background_boost_loop, get_boost_stats, reload_links

# === Environment ===
TOKEN = os.getenv("DISCORD_BOT_TOKEN")        # set this in Render > Environment
ADMIN_ID = os.getenv("DISCORD_ADMIN_ID", "")  # optional: your Discord user ID for admin-only cmds

if not TOKEN:
    raise ValueError("❌ DISCORD_BOT_TOKEN environment variable not set!")

# === Bot setup ===
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    # start the background loop (reads shein_links.txt & temu_links.txt)
    background_boost_loop.start(bot)

# === Commands ===
@bot.command(help="Boost a single link now (SHEIN or TEMU). Usage: !boost <url>")
async def boost(ctx, link: str):
    await ctx.send(f"🚀 Boosting: {link}")
    if "shein.com" in link:
        from shein import boost_shein_link
        await boost_shein_link(link, ctx.channel)
    elif "temu.com" in link:
        from temu import boost_temu_link
        await boost_temu_link(link, ctx.channel)
    else:
        await ctx.send("❌ Invalid link. Please send a valid SHEIN or TEMU link.")

@bot.command(help="Show how many links have been boosted so far.")
async def status(ctx):
    if ADMIN_ID and str(ctx.author.id) != str(ADMIN_ID):
        return await ctx.send("⛔ Admin only.")
    stats = get_boost_stats()
    await ctx.send(f"📊 Progress — SHEIN: {stats['shein']} | TEMU: {stats['temu']}")

@bot.command(help="Reload shein_links.txt and temu_links.txt without restarting the bot.")
async def refresh(ctx):
    if ADMIN_ID and str(ctx.author.id) != str(ADMIN_ID):
        return await ctx.send("⛔ Admin only.")
    reload_links()
    await ctx.send("🔄 Link files reloaded.")

# Run
bot.run(TOKEN)