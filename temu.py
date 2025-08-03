import discord
from discord.ext import commands
import os
import asyncio
import random
import time
from pyppeteer import launch

REFERRAL_LINKS = [
    "https://temu.com/a/VeHhz9bwz5DB1Fk",
    "https://onelink.shein.com/15/4vzpagy20nbj",
    "https://onelink.shein.com/15/4vzqhnqesl4x",
    "https://onelink.shein.com/15/4vzqljtlysyj",
    "https://onelink.shein.com/15/4vzqo6j35pna"
]

PROXIES = [
    "http://18.76.174.190:1519",
    "http://184.70.246.27:1787",
    "http://238.237.229.250:7703",
    "http://253.149.208.151:2388",
    "http://45.194.232.142:6217",
    "http://203.232.170.74:3306",
    "http://170.47.147.229:5859",
    "http://98.223.239.174:8400",
    "http://141.20.163.57:2685",
    "http://125.185.233.169:7984"
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (Linux; Android 10)"
]

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

async def simulate_visit(link):
    try:
        proxy = random.choice(PROXIES)
        user_agent = random.choice(USER_AGENTS)

        browser = await launch(
            headless=True,
            args=[
                f'--proxy-server={proxy}',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                f'--user-agent={user_agent}'
            ]
        )
        page = await browser.newPage()
        await page.goto(link, timeout=60000)

        await asyncio.sleep(random.uniform(2.5, 5.5))
        await page.keyboard.down("End")
        await asyncio.sleep(random.uniform(2, 4))
        await browser.close()
        return True, proxy
    except Exception as e:
        return False, str(e)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.command()
async def start(ctx):
    await ctx.send("🚀 Starting referral booster...")
    for link in REFERRAL_LINKS:
        success, info = await simulate_visit(link)
        if success:
            await ctx.send(f"✅ Visited: {link} via {info}")
        else:
            await ctx.send(f"❌ Error with {link}: {info}")

@bot.command()
async def visit(ctx, link: str):
    await ctx.send(f"🌐 Visiting custom link...")
    success, info = await simulate_visit(link)
    if success:
        await ctx.send(f"✅ Visited: {link} via {info}")
    else:
        await ctx.send(f"❌ Error with {link}: {info}")

def setup_bot():
    TOKEN = os.getenv("DISCORD_TOKEN")
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("❌ DISCORD_TOKEN not set.")