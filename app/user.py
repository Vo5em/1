import re
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command, CommandObject
from zoneinfo import ZoneInfo
from datetime import datetime, timedelta
from app.keyboard import payment_ketboard
import app.keyboard as kb
from app.gen import addkey

from app.database.requests import set_user, find_key, find_dayend, create_payment, cancelpay
MOSCOW_TZ = ZoneInfo("Europe/Moscow")

user = Router()

def escape_markdown(text: str) -> str:
    return re.sub(r'([_\*\[\]\(\)~`>#+\-=|{}.!])', r'\\\1', text)


@user.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject):
    tg_id = message.from_user.id
    ref_id = command.args
    if ref_id and ref_id.isdigit():
        await set_user(tg_id, ref_id)
    else:
        await set_user(tg_id, ref_id)

    is_key = await find_key(tg_id)
    if not is_key:
        await message.answer(text='привет', reply_markup=kb.main)
    else:
        is_day = await find_dayend(tg_id)
        now_moscow = datetime.now(tz=MOSCOW_TZ)

        if is_day.tzinfo is None:
            is_day = is_day.replace(tzinfo=MOSCOW_TZ)

        if is_day < now_moscow:
            await message.answer(
                text=f"Ваш id: <code>{tg_id}</code>\n🔴У вас нет активной подписки",
                parse_mode="HTML",
                reply_markup=kb.main_old
            )
        else: await message.answer(
            text=f"Ваш id: <code>{tg_id}</code>\n🟢Действует до {is_day.strftime('%d.%m.%Y %H:%M')}",
            parse_mode="HTML",
            reply_markup=kb.main_old
        )


@user.callback_query(F.data == 'home')
async def home(callback: CallbackQuery):
    tg_id = callback.from_user.id
    is_day = await find_dayend(tg_id)
    now_moscow = datetime.now(tz=MOSCOW_TZ)
    if is_day.tzinfo is None:
        is_day = is_day.replace(tzinfo=MOSCOW_TZ)

    if is_day < now_moscow:
        await callback.message.edit_text(
            text=f"Ваш id: <code>{tg_id}</code>\n🔴У вас нет активной подписки",
            parse_mode="HTML",
            reply_markup=kb.main_old
        )
    else:
        await callback.message.edit_text(
            text=f"Ваш id: <code>{tg_id}</code>\n🟢Действует до {is_day.strftime('%d.%m.%Y %H:%M')}",
            parse_mode="HTML",
            reply_markup=kb.main_old
        )


@user.message(Command('help'))
async def cmd_help(message: Message):
    tg_id = message.from_user.id
    url = await create_payment(tg_id)
    await message.answer(f"💳 Оплатите по ссылке:\n{url}")



@user.message(Command('subscribe'))
async def cmd_sub(message: Message):
    await message.answer(text='подписка')


@user.message(Command('ref_programm'))
async def cmd_ref(message: Message):
    tg_id = message.from_user.id
    BOT_USERNAME = 'test0viybotnafig_bot'
    ref_link = f"https://t.me/{BOT_USERNAME}?start={tg_id}"
    escaped_link = escape_markdown(ref_link)
    await message.answer(
        f"🗣️ *Реферальная ссылка:* \n`{escaped_link}`",
        parse_mode="MarkdownV2",
        reply_markup=kb.go_home
    )


@user.callback_query(F.data == 'period')
async def period(callback: CallbackQuery):
    tg_id = callback.from_user.id
    is_key = await find_key(tg_id)
    if not is_key:
        await callback.answer('')
        await callback.message.edit_text('*Выберите ваше устройство:*',
                                         parse_mode="MarkdownV2",
                                         reply_markup=kb.gadgets)
    else:
        is_day = await find_dayend(tg_id)
        now_moscow = datetime.now(tz=MOSCOW_TZ)
        if is_day.tzinfo is None:
            is_day = is_day.replace(tzinfo=MOSCOW_TZ)
        if is_day > now_moscow:
            await callback.answer('')
            await callback.message.edit_text('*Выберите ваше устройство:*',
                                             parse_mode="MarkdownV2",
                                             reply_markup=kb.gadgets_old)
        else: await callback.message.edit_text('*У вас нет активной подписки*',
                                               parse_mode="MarkdownV2",
                                               reply_markup=kb.go_pay)


@user.callback_query(F.data == 'android')
async def connect_an(callback: CallbackQuery):
    user_id = callback.from_user.id
    is_key = await find_key(user_id)
    if not is_key:
      await addkey(user_id)
      is_key = await find_key(user_id)
      await callback.answer('')
      await callback.message.edit_text(f"`{is_key}`",
                                     parse_mode="MarkdownV2",
                                     reply_markup=kb.download)
    else: await callback.message.edit_text(f"`{is_key}`",
                                           parse_mode="MarkdownV2",
                                           reply_markup=kb.download)


@user.callback_query(F.data == 'iphone')
async def connect_i(callback: CallbackQuery):
    user_id = callback.from_user.id
    is_key = await find_key(user_id)
    if not is_key:
      await addkey(user_id)
      is_key = await find_key(user_id)
      await callback.answer('')
      await callback.message.edit_text(f"`{is_key}`",
                                     parse_mode="MarkdownV2",
                                     reply_markup=kb.download)
    else: await callback.message.edit_text(f"`{is_key}`",
                                           parse_mode="MarkdownV2",
                                           reply_markup=kb.download)


@user.callback_query(F.data == 'huawei')
async def connect_hu(callback: CallbackQuery):
    user_id = callback.from_user.id
    is_key = await find_key(user_id)
    if not is_key:
      await addkey(user_id)
      is_key = await find_key(user_id)
      await callback.answer('')
      await callback.message.edit_text(f"`{is_key}`",
                                     parse_mode="MarkdownV2",
                                     reply_markup=kb.download)
    else: await callback.message.edit_text(f"`{is_key}`",
                                           parse_mode="MarkdownV2",
                                           reply_markup=kb.download)


@user.callback_query(F.data == 'windows')
async def connect_win(callback: CallbackQuery):
    user_id = callback.from_user.id
    is_key = await find_key(user_id)
    if not is_key:
      await addkey(user_id)
      is_key = await find_key(user_id)
      await callback.answer('')
      await callback.message.edit_text(f"`{is_key}`",
                                     parse_mode="MarkdownV2",
                                     reply_markup=kb.download)
    else: await callback.message.edit_text(f"`{is_key}`",
                                           parse_mode="MarkdownV2",
                                           reply_markup=kb.download)


@user.callback_query(F.data == 'macos')
async def connect_mc(callback: CallbackQuery):
    user_id = callback.from_user.id
    is_key = await find_key(user_id)
    if not is_key:
      await addkey(user_id)
      is_key = await find_key(user_id)
      await callback.answer('')
      await callback.message.edit_text(f"`{is_key}`",
                                     parse_mode="MarkdownV2",
                                     reply_markup=kb.download)
    else: await callback.message.edit_text(f"`{is_key}`",
                                           parse_mode="MarkdownV2",
                                           reply_markup=kb.download)


@user.callback_query(F.data == 'androidtv')
async def connect_antv(callback: CallbackQuery):
    user_id = callback.from_user.id
    is_key = await find_key(user_id)
    if not is_key:
      await addkey(user_id)
      is_key = await find_key(user_id)
      await callback.answer('')
      await callback.message.edit_text(f"`{is_key}`",
                                     parse_mode="MarkdownV2",
                                     reply_markup=kb.download)
    else: await callback.message.edit_text(f"`{is_key}`",
                                           parse_mode="MarkdownV2",
                                           reply_markup=kb.download)


@user.callback_query(F.data == 'refka')
async def refka(callback: CallbackQuery):
    tg_id = callback.from_user.id
    BOT_USERNAME = 'test0viybotnafig_bot'
    ref_link = f"https://t.me/{BOT_USERNAME}?start={tg_id}"
    escaped_link = escape_markdown(ref_link)
    await callback.answer('')
    await callback.message.edit_text(
        f"🗣️ *Реферальная ссылка:* \n`{escaped_link}`",
        parse_mode="MarkdownV2",
        reply_markup=kb.go_home
    )


@user.callback_query(F.data == 'pay')
async def sub(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.edit_text(
        'балалабалалабалалб \nДИСКЛЕЙМЕР'
        '\nкароч вы обязанны мне платить деньги каждый месяц\n'
        'НЕСОГЛАСНЫ?\nвышлинахеротсюда',
        reply_markup=kb.give_money
    )


@user.callback_query(F.data == 'doitpls')
async def pay(callback: CallbackQuery):
    tg_id = callback.from_user.id
    payment_url, payment_id = await create_payment(tg_id)
    kburl = payment_ketboard(payment_url, payment_id)
    await callback.message.answer(f"💳 Оплатите по ссылке:\n{payment_url}", reply_markup=kburl)

@user.callback_query(F.data.startswith("cancel"))
async def delitepay(callback: CallbackQuery):
    payment_id = callback.data.replace("cancel", "")
    await cancelpay(payment_id)
    await callback.message.edit_text('Платеж отменен', reply_markup=kb.go_home)