import asyncio
from aiogram import Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from zoneinfo import ZoneInfo

from config import bot
from app.user import user
from app.admin import admin

from app.database.models import async_main
from app.database.requests import schedulers, restore_notifications


dp = Dispatcher()
MOSCOW_TZ = ZoneInfo("Europe/Moscow")
scheduler = AsyncIOScheduler(timezone=MOSCOW_TZ)


async def on_startup(dispatcher):
    await async_main()
    await restore_notifications()
    asyncio.create_task(schedulers())


async def main():
    dp.include_routers(user, admin)
    dp.startup.register(on_startup)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
