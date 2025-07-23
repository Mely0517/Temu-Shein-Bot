import os
from temu import bot

if __name__ == "__main__":
    bot.run(os.getenv("DISCORD_TOKEN"))
