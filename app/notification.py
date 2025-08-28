from config import bot
from aiogram.types import Message, CallbackQuery
import app.keyboard as kb


async def notify_before_end(tg_id: int):
    await bot.send_message(tg_id, "⚠️ Ваша подписка закончится через 24 часа!", reply_markup=kb.go_pay)


async def notify_end(tg_id: int):
    await bot.edit_message_text(tg_id, "🔴 Ваша подписка истекла.", reply_markup=kb.go_pay)


async def notify_sps(tg_id):
    print(f"[notify_sps] start tg_id={tg_id}")
    await bot.send_message(tg_id, "Поздравляю 🎉 Вы успешно приобрели подписку!", reply_markup=kb.go_home)
    print("[notify_sps] message sent")

