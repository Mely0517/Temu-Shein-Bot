import discord
from discord.ext import commands
import os
from background import background_boost_loop, get_boost_stats, reload_links

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
ADMIN_ID = os.getenv("DISCORD_ADMIN_ID")  # Optional for admin commands

if not TOKEN:
    raise ValueError("❌ DISCORD_BOT_TOKEN environment variable not set!")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    background_boost_loop.start(bot)

@bot.command()
async def boost(ctx, link: str):
    await ctx.send(f"🚀 Boosting: {link}")
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

bot.run(TOKEN)