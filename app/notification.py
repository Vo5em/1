from config import bot
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from app.database.models import async_session, User, Order
from sqlalchemy import select, update, delete, desc
import app.keyboard as kb
from zoneinfo import ZoneInfo
from datetime import datetime, timedelta
import logging

MOSCOW_TZ = ZoneInfo("Europe/Moscow")

file04 = "AgACAgIAAxkBAAMaaNMPnzGPdHKD_6UQTSuLxSiiT54AAg4MMhtRY5lKmvQCMwSLnvwBAAMCAAN5AAM2BA"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)



async def test_job(tg_id: int):
    logging.info(f"🚀 test_job запущена для tg_id={tg_id}")
    await bot.send_message(tg_id, "Твоя подписка истекла.", reply_markup=kb.go_pay)

async def notify_before_end(tg_id: int):
    async with async_session() as session:
        user = await session.get(User, tg_id)
        now = datetime.now(tz=MOSCOW_TZ)
        if user and user.dayend:
            daybeforeend = user.dayend - timedelta(days=1)
            if now >= daybeforeend:
                await bot.send_message(tg_id,
                                       "Твоя подписка закончится через 24 часа!",
                                       reply_markup=kb.go_pay)
                return


async def notify_end(tg_id: int):
    async with async_session() as session:
        user = await session.get(User, tg_id)
        now = datetime.now(tz=MOSCOW_TZ)
        if user and user.dayend and now >= user.dayend:
            await bot.send_message(tg_id, "Твоя подписка истекла.", reply_markup=kb.go_pay)
            return


async def notify_spss(tg_id: int):
    print ("te")
    async with async_session() as session:
        result = await session.execute(select(User).where(User.tg_id == tg_id))
        user = result.scalars().first()

        if not user or not user.message_id:
            return
    await bot.edit_message_media(
        chat_id=tg_id,
        message_id=user.message_id,
        media=InputMediaPhoto(
            media=file04,
            caption="Теперь Ты — один из тех, кто знает."
        ),
        reply_markup=kb.on_main
    )