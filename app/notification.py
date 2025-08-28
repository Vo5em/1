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
    print("🔥 notify_sps_test вызвана")
    async with async_session() as session:
        result = await session.execute(select(User).where(User.tg_id == tg_id))
        user = result.scalars().first()

        if not user:
            print(f"[notify_sps] Пользователь с tg_id={tg_id} не найден")
            return

        if user.message_id:
            try:
                await bot.delete_message(chat_id=tg_id, message_id=user.message_id)
                print(f"[notify_sps] Удалено старое сообщение {user.message_id} для {tg_id}")
            except Exception as e:
                print(f"[notify_sps] Ошибка при удалении старого сообщения: {e}")

        try:
            msg = await bot.send_message(
                chat_id=tg_id,
                text="Поздравляю 🎉 Вы успешно приобрели подписку!",
                reply_markup=kb.go_pay
            )
            await session.commit()
            print(f"[notify_sps] Отправлено новое сообщение {msg.message_id} пользователю {tg_id}")
        except Exception as e:
            print(f"[notify_sps] Ошибка при отправке нового сообщения: {e}")
