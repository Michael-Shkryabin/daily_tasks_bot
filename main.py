import asyncio
import logging
from aiogram import Dispatcher

from bot import bot
from scheduler import setup_scheduler, shutdown_scheduler
from db import add_user

from handlers import start, tasks, digest, timezone, callbacks

logging.basicConfig(level=logging.INFO)


async def ensure_user(handler, event, data):
    if event.from_user:
        add_user(event.from_user.id)
    return await handler(event, data)


async def main():
    dp = Dispatcher()
    dp.message.middleware(ensure_user)
    dp.callback_query.middleware(ensure_user)

    dp.include_router(start.router)
    dp.include_router(tasks.router)
    dp.include_router(digest.router)
    dp.include_router(timezone.router)
    dp.include_router(callbacks.router)

    setup_scheduler(bot)
    try:
        await dp.start_polling(bot)
    finally:
        shutdown_scheduler()


if __name__ == "__main__":
    asyncio.run(main())
