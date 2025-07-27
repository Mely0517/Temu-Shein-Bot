from temu import setup_bot

bot = setup_bot()

if __name__ == "__main__":
    import asyncio

    async def main():
        await bot.start(os.getenv("DISCORD_TOKEN"))

    asyncio.run(main())
