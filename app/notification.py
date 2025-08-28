from config import bot
from aiogram.types import Message, CallbackQuery
from app.database.models import async_session, User, Order
from sqlalchemy import select, update, delete, desc
import app.keyboard as kb


async def notify_before_end(tg_id: int):
    await bot.send_message(tg_id, "⚠️ Ваша подписка закончится через 24 часа!", reply_markup=kb.go_pay)


async def notify_end(tg_id: int):
    await bot.send_message(tg_id, "🔴 Ваша подписка истекла.", reply_markup=kb.go_pay)


async def notify_spss(tg_id: int):
    await bot.send_message(
        chat_id=tg_id,
        text="Поздравляю 🎉 Вы успешно приобрели подписку!",
        reply_markup=kb.go_pay
    )