from config import bot
from aiogram.types import Message, CallbackQuery
from app.database.requests import find_message
import app.keyboard as kb


async def notify_before_end(tg_id: int):
    await bot.send_message(tg_id, "⚠️ Ваша подписка закончится через 24 часа!", reply_markup=kb.go_pay)


async def notify_end(tg_id: int):
    await bot.edit_message_text(tg_id, "🔴 Ваша подписка истекла.", reply_markup=kb.go_pay)


async def notify_sps(tg_id):
    message = await find_message(tg_id)
    try:
        await bot.edit_message_text(
            chat_id=tg_id,
            message_id=message,
            text="Поздравляю 🎉 Вы успешно приобрели подписку!",
            reply_markup=kb.go_home
        )
    except Exception as e:
        print(f"Ошибка при редактировании сообщения: {e}")

