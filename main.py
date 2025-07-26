import os
from temu import bot

TOKEN = os.getenv("DISCORD_TOKEN")

if __name__ == "__main__":
    bot.run(TOKEN)
