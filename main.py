from temu import bot, setup_bot
import os

if __name__ == "__main__":
    setup_bot()
    bot.run(os.getenv("DISCORD_TOKEN"))
