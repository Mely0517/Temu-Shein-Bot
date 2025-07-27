from temu import setup_bot
import os

bot = setup_bot()
bot.run(os.getenv("DISCORD_TOKEN"))
