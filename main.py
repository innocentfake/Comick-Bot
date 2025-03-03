import asyncio as aio
from bot import async_main, manga_updater, chapter_creation, bot

async def main():
    await async_main()  # Ensure this function exists in bot.py
    aio.create_task(manga_updater())
    for i in range(10):
        aio.create_task(chapter_creation(i + 1))
    bot.run()  # Assuming bot.run() is synchronous

if __name__ == '__main__':
    aio.run(main())  # Ensures proper async handling
