import asyncio
import logging
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


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)


async def on_startup(dispatcher):
    logging.info("🔄 Инициализация on_startup...")
    await async_main()
    await restore_notifications()
    await schedulerс()
    asyncio.create_task(schedulers())


async def main():
    logging.info("🔹 main() стартанул")
    dp.include_routers(user, admin)
    dp.startup.register(on_startup)
    logging.info("🔹 dispatcher.start_polling вызывается")
    await dp.start_polling(bot)
    logging.info("🔹 dispatcher.start_polling завершился")


async def schedulerс():
    logging.info("🕒 Инициализация планировщика...")
    if not scheduler.running:
        scheduler.start()
        logging.info(f"🚀 Scheduler стартанул! running={scheduler.running}")
    else:
        logging.info("⚙️ Scheduler уже запущен")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
