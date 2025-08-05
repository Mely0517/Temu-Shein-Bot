import discord
from discord.ext import commands
import os
from background import background_boost_loop, get_boost_stats, reload_links

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
ADMIN_ID = os.getenv("DISCORD_ADMIN_ID")  # Optional — your Discord user ID

if not TOKEN:
    raise ValueError("❌ DISCORD_BOT_TOKEN environment variable not set!")

# Enable message content so bot can read commands
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    if not background_boost_loop.is_running():
        background_boost_loop.start(bot)
    channel = discord.utils.get(bot.get_all_channels(), name="general")
    if channel:
        await channel.send("🤖 Bot is online and boosting links automatically!")

@bot.command()
async def boost(ctx, link: str):
    """Manually boost a specific SHEIN or TEMU link."""
    from shein import boost_shein_link
    from temu import boost_temu_link

    await ctx.send(f"🚀 Boosting: {link}")

    if "shein.com" in link:
        await boost_shein_link(link, ctx.channel)
    elif "temu.com" in link:
        await boost_temu_link(link, ctx.channel)
    else:
        await ctx.send("❌ Invalid link. Please use a SHEIN or TEMU link.")

@bot.command()
async def status(ctx):
    """Show total boosts completed."""
    if ADMIN_ID and str(ctx.author.id) != ADMIN_ID:
        return await ctx.send("⛔ Admin only.")
    stats = get_boost_stats()
    await ctx.send(f"📊 Boosted {stats['shein']} SHEIN links and {stats['temu']} TEMU links so far.")

@bot.command()
async def refresh(ctx):
    """Reload links from shein_links.txt and temu_links.txt."""
    if ADMIN_ID and str(ctx.author.id) != ADMIN_ID:
        return await ctx.send("⛔ Admin only.")
    reload_links()
    await ctx.send("🔄 Link files reloaded.")

bot.run(TOKEN)