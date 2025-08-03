import discord
from discord.ext import commands
import asyncio
from shein import boost_shein
from temu import boost_temu

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.command()
async def boost(ctx, link: str = None):
    if not link:
        await ctx.send("❗ Please provide a link after the command. Example: `!boost <link>`")
        return

    await ctx.send(f"🚀 Starting referral booster...\n{link}")
    if "temu.com" in link:
        result = await boost_temu(link)
    elif "shein.com" in link:
        result = await boost_shein(link)
    else:
        result = "❌ Unsupported link. Only Temu and SHEIN are supported."
    await ctx.send(result)

bot.run("YOUR_DISCORD_BOT_TOKEN")