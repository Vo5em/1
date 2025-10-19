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

async def main():
    dp.include_routers(user, admin)
    dp.startup.register(on_startup)
    await dp.start_polling(bot)


async def on_startup(dispatcher):


    # 1. Инициализация базы и прочих сервисов
    await async_main()

    # 2. Восстановление уведомлений из БД
    await restore_notifications()

    # 3. Запуск scheduler
    scheduler.start()


    # 4. Запуск дополнительного цикла, если нужен
    asyncio.create_task(schedulers())



if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
