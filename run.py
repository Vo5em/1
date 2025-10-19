import asyncio
from aiogram import Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from zoneinfo import ZoneInfo

from config import bot
from app.user import user
from app.admin import admin
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

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
    # 1. Делаем любые асинхронные подготовительные функции
    await async_main()

    # 2. Сначала стартуем scheduler
    scheduler.start()
    logging.info("Scheduler запущен")

    # 3. Только после старта scheduler добавляем все задачи
    await restore_notifications()
    logging.info("Задачи для уведомлений восстановлены")

    # 4. Можно запускать дополнительный цикл проверки подписок
    asyncio.create_task(schedulers())



if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
