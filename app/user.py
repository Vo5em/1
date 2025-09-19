import re
import html
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.filters import CommandStart, Command, CommandObject
from zoneinfo import ZoneInfo
from datetime import datetime, timedelta
from app.keyboard import payment_keyboard
import app.keyboard as kb
from app.gen import addkey

from app.database.requests import set_user, find_key, find_dayend, create_payment, save_message, find_paymethod_id
from app.database.requests import delpaymethod_id
MOSCOW_TZ = ZoneInfo("Europe/Moscow")

user = Router()

file_id01="AgACAgIAAxkBAAIDJGi98rSpeXZ-DD7LjnQjGlVQhMnzAAI3_zEbYF_wSUQ71x7vAxTSAQADAgADdwADNgQ"
file_id02="AgACAgIAAxkBAAIDNmi-11DgQxRxzRElzTQPzwbZ2553AALw8jEbYF_4SX2hWNO4hiqDAQADAgADdwADNgQ"
file_id03="AgACAgIAAxkBAAIECmjLDehdsa2MTbFTRI7mhgK7hQs5AAIQCTIb985YSgO9r4rHggE3AQADAgADdwADNgQ"

def escape_markdown(text: str) -> str:
    return re.sub(r'([_\*\[\]\(\)~`>#+\-=|{}.!])', r'\\\1', text)


@user.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject):
    tg_id = message.from_user.id
    ref_id = command.args
    if ref_id and ref_id.isdigit():
        ref_id = int(ref_id)
        await set_user(tg_id, ref_id)
    else:
        await set_user(tg_id, None)

    is_key = await find_key(tg_id)
    if not is_key:
        await message.answer_photo(
            photo=file_id03,
            caption=f"<blockquote>ESCHELON district 01</blockquote>\n"
                    f"Ты близко.\n\n\n"
                    f"Анонимность начинается здесь, подключи 3 дня пробного периода.",
            parse_mode="HTML",
            reply_markup=kb.main
        )
    else:
        is_day = await find_dayend(tg_id)
        now_moscow = datetime.now(tz=MOSCOW_TZ)

        if is_day.tzinfo is None:
            is_day = is_day.replace(tzinfo=MOSCOW_TZ)

        if is_day < now_moscow:
            await message.answer_photo(
                photo=file_id02,
                caption=f"<blockquote>project eschelon;\n district: 01</blockquote>\n\n\n"
                        f"<b>Абонемент не активен.</b>",
                parse_mode="HTML",
                reply_markup=kb.main_old
            )
        else: await message.answer_photo(
            photo=file_id01,
            caption=f"<blockquote>project eschelon;\n district: 01</blockquote>\n\n\n"
                    f"<b>Абонемент активен.</b>",
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
        await callback.message.edit_media(InputMediaPhoto(
            media=file_id02,
            caption=f"<blockquote>project eschelon;\n district: 01</blockquote>\n\n\n"
                    f"<b>Абонемент не активен.</b>",
            parse_mode="HTML"),
            reply_markup=kb.main_old
        )
    else:
        await callback.message.edit_media(InputMediaPhoto(
            media=file_id01,
            caption=f"<blockquote>project eschelon;\n district: 01</blockquote>\n\n\n"
                    f"<b>Абонемент активен.</b>",
            parse_mode="HTML"),
            reply_markup=kb.main_old
        )


@user.callback_query(F.data == 'help')
async def helps(callback: CallbackQuery):
    tg_id = callback.from_user.id
    await callback.answer('')
    await callback.message.delete()
    await callback.message.answer(
        f"<b>ID:</b> <code>{tg_id}</code>\n\n"
        f"Первым сообщением напиши свой ID\n"
        f"Дальше опиши проблему — и мы тебе поможем.",
        parse_mode="HTML",
        reply_markup=kb.helps
    )



@user.message(Command('help'))
async def cmd_help(message: Message):
    tg_id = message.from_user.id
    await message.answer(
        f"<b>ID:</b><code>{tg_id}</code>\n\n"
        f"Первым сообщением напиши свой ID\n"
        f"Дальше опиши проблему — и мы тебе поможем.",
        pats_mode="HTML",
        reply_markup=kb.helps
    )


@user.message(Command('subscribe'))
async def cmd_sub(message: Message):
    tg_id = message.from_user.id
    paymenthodid = await find_paymethod_id(tg_id)

    if not paymenthodid:
        is_day = await find_dayend(tg_id)
        now_moscow = datetime.now(tz=MOSCOW_TZ)
        if is_day.tzinfo is None:
            is_day = is_day.replace(tzinfo=MOSCOW_TZ)

        if is_day < now_moscow:
            await message.answer(
                '<b>Абонемент не активен</b>\n\n'
                '<b>Подписка на месяц — 150₽</b>\n'
                '— Деньги будут списываться каждый месяц.\n'
                '— Отключить автопродление можно в любой момент в этом разделе.\n'
                '— При отключении доступ сохранится до конца оплаченного.\n\n'
                '<b>Важно знать:</b> подключаясь, Ты принимаешь условия\n'
                'ежемесячного списания.',
                parse_mode="HTML",
                reply_markup=kb.give_money
            )
        else:
            await message.answer(
                f"<b>Абонемент до {is_day.strftime('%d.%m.%Y')}</b>\n\n"
                f"<b>Подписка на месяц — 150₽</b>\n"
                f"— Деньги будут списываться каждый месяц.\n"
                f"— Отключить автопродление можно в любой момент в этом разделе.\n"
                f"— При отключении доступ сохранится до конца оплаченного.\n\n"
                f"<b>Важно знать:</b> подключаясь, Ты принимаешь условия\n"
                f"ежемесячного списания.",
                parse_mode="HTML",
                reply_markup=kb.give_money
            )
    else:
        is_day = await find_dayend(tg_id)
        if is_day.tzinfo is None:
            is_day = is_day.replace(tzinfo=MOSCOW_TZ)
        await message.answer(
            f"Следующее списание {is_day.strftime('%d.%m.%Y')}</b>\n\n"
            f"<b>Подписка на месяц — 150₽</b>\n"
            f"— Деньги будут списываться каждый месяц.\n"
            f"— Отключить автопродление можно в любой момент в этом разделе.\n"
            f"— При отключении доступ сохранится до конца оплаченного\n\n"
            f"<b>Важно знать:</b> подключаясь, Ты принимаешь условия\n"
            f"ежемесячного списания.",
            parse_mode="HTML",
            reply_markup=kb.cancelautopay
        )


@user.message(Command('ref_programm'))
async def cmd_ref(message: Message):
    tg_id = message.from_user.id
    BOT_USERNAME = 'test0viybotnafig_bot'
    ref_link = f"https://t.me/{BOT_USERNAME}?start={tg_id}"
    escaped_link = escape_markdown(ref_link)
    await message.answer(
        f"*Реферальная программа ESCHELON*\n\n"
        f"За каждого приглашённого друга, оформившего подписку,\n"
        f"Твой доступ продлевается на 7 дней\.\n\n"
        f"*Реферальная ссылка:*\n`{escaped_link}`",
        disable_web_page_preview=True,
        parse_mode="MarkdownV2",
        reply_markup=kb.go_home
    )


@user.callback_query(F.data == 'period')
async def period(callback: CallbackQuery):
    tg_id = callback.from_user.id
    is_key = await find_key(tg_id)
    if not is_key:
        await callback.answer('')
        await callback.message.delete()
        await callback.message.answer('*Выберите ваше устройство:*',
                                         parse_mode="MarkdownV2",
                                         reply_markup=kb.gadgets)
    else:
        is_day = await find_dayend(tg_id)
        now_moscow = datetime.now(tz=MOSCOW_TZ)
        if is_day.tzinfo is None:
            is_day = is_day.replace(tzinfo=MOSCOW_TZ)
        if is_day > now_moscow:
            await callback.answer('')
            await callback.message.delete()
            await callback.message.answer('*Выберите ваше устройство:*',
                                             parse_mode="MarkdownV2",
                                             reply_markup=kb.gadgets_old)
        else:
            await callback.message.delete()
            await callback.message.answer('*У вас нет активной подписки*',
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
      await callback.message.edit_text(f'<b>ИНСТРУКЦИЯ:</b>\n\n'
                                       f'<b>№1</b> - скачай приложение'
                                       f' <a href="https://play.google.com'
                                       f'/store/apps/details?id=com.v2raytun.android">v2RayTun</a>'"\n"
                                       "<b>№2</b> - Нажми на ключ доступа cнизу ( начинается с vless://)\n"
                                       "<b>№3</b> - Запусти программу v2RayTun и нажми на <b>+</b>"
                                       " в правом верхнем углу\n"
                                       "<b>№4</b> -  Выбери «Импорт из буфера обмена»\n"
                                       "<b>№5</b> - Нажми круглую кнопку включения\n\n"
                                       f"<blockquote expandable><code>{html.escape(is_key)}</code></blockquote>",
                                       disable_web_page_preview=True,
                                       parse_mode="HTML",
                                    reply_markup=kb.downloadand)
    else: await callback.message.edit_text(f'<b>ИНСТРУКЦИЯ:</b>\n\n'
                                           f'<b>№1</b> - скачай приложение'
                                           f' <a href="https://play.google.com'
                                           f'/store/apps/details?id=com.v2raytun.android">v2RayTun</a>'"\n"
                                           "<b>№2</b> - Нажми на ключ доступа cнизу ( начинается с vless://)\n"
                                           "<b>№3</b> - Запусти программу v2RayTun и нажми на <b>+</b>"
                                           " в правом верхнем углу\n"
                                           "<b>№4</b> - Выбери «Импорт из буфера обмена»\n"
                                           "<b>№5</b> - Нажми круглую кнопку включения\n\n"
                                           f"<blockquote expandable><code>{html.escape(is_key)}</code></blockquote>",
                                           disable_web_page_preview=True,
                                           parse_mode="HTML",
                                           reply_markup=kb.downloadand)


@user.callback_query(F.data == 'iphone')
async def connect_i(callback: CallbackQuery):
    user_id = callback.from_user.id
    is_key = await find_key(user_id)
    if not is_key:
      await addkey(user_id)
      is_key = await find_key(user_id)
      await callback.answer('')
      await callback.message.edit_text(f'<b>ИНСТРУКЦИЯ:</b>\n\n'
                                       f'<b>№1</b> - Cкачай приложение'
                                       f' <a href="https://apps.apple.com'
                                       f'/lt/app/v2raytun/id6476628951">v2RayTun</a>'"\n"
                                       "<b>№2</b> - Нажми на ключ доступа cнизу ( начинается с vless://)\n"
                                       "<b>№3</b> - Запусти программу v2RayTun и нажми на <b>+</b>"
                                       " в правом верхнем углу\n"
                                       "<b>№4</b> -  Выбери «Импорт из буфера обмена»\n"
                                       "<b>№5</b> - Нажми круглую кнопку включения\n\n"
                                       f"<blockquote expandable><code>{html.escape(is_key)}</code></blockquote>",
                                       disable_web_page_preview=True,
                                       parse_mode="HTML",
                                     reply_markup=kb.downloadiph)
    else: await callback.message.edit_text(f'<b>ИНСТРУКЦИЯ:</b>\n\n'
                                           f'<b>№1</b> - Cкачай приложение'
                                           f' <a href="https://apps.apple.com'
                                           f'/lt/app/v2raytun/id6476628951">v2RayTun</a>'"\n"
                                           "<b>№2</b> - Нажми на ключ доступа cнизу ( начинается с vless://)\n"
                                           "<b>№3</b> - Запусти программу v2RayTun и нажми на <b>+</b>"
                                           " в правом верхнем углу\n"
                                           "<b>№4</b> -  Выбери «Импорт из буфера обмена»\n"
                                           "<b>№5</b> - Нажми круглую кнопку включения\n\n"
                                           f"<blockquote expandable><code>{html.escape(is_key)}</code></blockquote>",
                                           disable_web_page_preview=True,
                                           parse_mode="HTML",
                                           reply_markup=kb.downloadiph)


@user.callback_query(F.data == 'huawei')
async def connect_hu(callback: CallbackQuery):
    user_id = callback.from_user.id
    is_key = await find_key(user_id)
    if not is_key:
      await addkey(user_id)
      is_key = await find_key(user_id)
      await callback.answer('')
      await callback.message.edit_text(f'<b>ИНСТРУКЦИЯ:</b>\n\n'
                                       f'<b>№1</b> - Cкачай приложение'
                                       f' <a href="https://github.com/barmaiey5553/V2RayTun-for-china-mobile'
                                       f'/releases/download/v1.0/v2RayTun_3.10.42_arm64-v8a.apk">v2RayTun</a>'"\n"
                                       "<b>№2</b> - Нажми на ключ доступа cнизу ( начинается с vless://)\n"
                                       "<b>№3</b> - Запусти программу v2RayTun и нажми на <b>+</b>"
                                       " в правом верхнем углу\n"
                                       "<b>№4</b> -  Выбери «Импорт из буфера обмена»\n"
                                       "<b>№5</b> - Нажми круглую кнопку включения\n\n"
                                       f"<blockquote expandable><code>{html.escape(is_key)}</code></blockquote>",
                                       disable_web_page_preview=True,
                                       parse_mode="HTML",
                                     reply_markup=kb.downloadHUA)
    else: await callback.message.edit_text(f'<b>ИНСТРУКЦИЯ:</b>\n\n'
                                           f'<b>№1</b> - Cкачай приложение'
                                           f' <a href="https://github.com/barmaiey5553/V2RayTun-for-china-mobile'
                                           f'/releases/download/v1.0/v2RayTun_3.10.42_arm64-v8a.apk">v2RayTun</a>'"\n"
                                           "<b>№2</b> - Нажми на ключ доступа cнизу ( начинается с vless://)\n"
                                           "<b>№3</b> - Запусти программу v2RayTun и нажми на <b>+</b>"
                                           " в правом верхнем углу\n"
                                           "<b>№4</b> -  Выбери «Импорт из буфера обмена»\n"
                                           "<b>№5</b> - Нажми круглую кнопку включения\n\n"
                                           f"<blockquote expandable><code>{html.escape(is_key)}</code></blockquote>",
                                           disable_web_page_preview=True,
                                           parse_mode="HTML",
                                           reply_markup=kb.downloadHUA)



@user.callback_query(F.data == 'windows')
async def connect_win(callback: CallbackQuery):
    user_id = callback.from_user.id
    is_key = await find_key(user_id)
    if not is_key:
      await addkey(user_id)
      is_key = await find_key(user_id)
      await callback.answer('')
      await callback.message.edit_text(f'<b>ИНСТРУКЦИЯ:</b>\n\n'
                                       f'<b>№1</b> - Скачай приложение'
                                       f' <a href="https://github.com/MatsuriDayo/nekoray/releases'
                                       f'/download/4.0.1/nekoray-4.0.1-2024-12-12-windows64.zip">v2RayTun</a>'"\n"
                                       "<b>№2</b> - Нажми на ключ доступа cнизу ( начинается с vless://)\n"
                                       "<b>№3</b> - Разархивируй и запусти программу «NekoBox» имени администратора\n"
                                       "<b>№4</b> - Включи режим TUN в правом веерхнем углу \n"
                                       "<b>№5</b> - Нажми правой кнопкой мыши по пустому пространству"
                                       " и выбери «Добавить профиль из буфера обмена»\n"
                                       "<b>№6</b> - Нажми правой кнопкой мыши по появившимуся профилю"
                                       " и выбери «Запустить»\n\n"
                                       f"<blockquote expandable><code>{html.escape(is_key)}</code></blockquote>",
                                       disable_web_page_preview=True,
                                       parse_mode="HTML",
                                     reply_markup=kb.downloadwin)
    else: await callback.message.edit_text(f'<b>ИНСТРУКЦИЯ:</b>\n\n'
                                           f'<b>№1</b> - Скачай приложение'
                                           f' <a href="https://github.com/MatsuriDayo/nekoray/releases'
                                           f'/download/4.0.1/nekoray-4.0.1-2024-12-12-windows64.zip">v2RayTun</a>'"\n"
                                           "<b>№2</b> - Нажми на ключ доступа cнизу ( начинается с vless://)\n"
                                           "<b>№3</b> - Разархивируй и запусти программу «NekoBox»"
                                           " имени администратора\n"
                                           "<b>№4</b> - Включи режим TUN в правом веерхнем углу \n"
                                           "<b>№5</b> - Нажми правой кнопкой мыши по пустому пространству"
                                           " и выбери «Добавить профиль из буфера обмена»\n"
                                           "<b>№6</b> - Нажми правой кнопкой мыши по появившимуся профилю"
                                           " и выбери «Запустить»\n\n"
                                           f"<blockquote expandable><code>{html.escape(is_key)}</code></blockquote>",
                                           disable_web_page_preview=True,
                                           parse_mode="HTML",
                                           reply_markup=kb.downloadwin)


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
                                     reply_markup=kb.downloaddich)
    else: await callback.message.edit_text(f"`{is_key}`",
                                           parse_mode="MarkdownV2",
                                           reply_markup=kb.downloaddich)


@user.callback_query(F.data == 'androidtv')
async def connect_antv(callback: CallbackQuery):
    user_id = callback.from_user.id
    is_key = await find_key(user_id)
    if not is_key:
      await addkey(user_id)
      is_key = await find_key(user_id)
      await callback.answer('')
      await callback.message.edit_text(f'<b>ИНСТРУКЦИЯ:</b>\n\n'
                                       f"<b>№1</b> - Установи пульт на свой телефон по кнопке ниже\n"
                                       "<b>№2</b> - Нажми на ключ доступа cнизу ( начинается с vless://)\n"
                                       "<b>№3</b> - Установи v2RayTun на Android TV"
                                       "<b>№4</b> - Запусти v2RayTun и выбери пункт «ручной ввод»\n"
                                       "<b>№5</b> - Вставь скопированный ключ используя установленный пульт\n"
                                       "<b>№6</b> - Нажми <b>Ок</b>\n\n"
                                       f"<blockquote expandable><code>{html.escape(is_key)}</code></blockquote>",
                                       disable_web_page_preview=True,
                                       parse_mode="HTML",
                                     reply_markup=kb.downloadTV)
    else: await callback.message.edit_text(f'<b>ИНСТРУКЦИЯ:</b>\n\n'
                                           f"<b>№1</b> - Установи пульт на свой телефон по кнопке ниже\n"
                                           "<b>№2</b> - Нажми на ключ доступа cнизу ( начинается с vless://)\n"
                                           "<b>№3</b> - Установи v2RayTun на Android TV"
                                           "<b>№4</b> - Запусти v2RayTun и выбери пункт «ручной ввод»\n"
                                           "<b>№5</b> - Вставь скопированный ключ используя установленный пульт\n"
                                           "<b>№6</b> - Нажми <b>Ок</b>\n\n"
                                           f"<blockquote expandable><code>{html.escape(is_key)}</code></blockquote>",
                                           disable_web_page_preview=True,
                                           parse_mode="HTML",
                                           reply_markup=kb.downloadTV)


@user.callback_query(F.data == 'refka')
async def refka(callback: CallbackQuery):
    tg_id = callback.from_user.id
    BOT_USERNAME = 'test0viybotnafig_bot'
    ref_link = f"https://t.me/{BOT_USERNAME}?start={tg_id}"
    escaped_link = escape_markdown(ref_link)
    await callback.answer('')
    await callback.message.delete()
    await callback.message.answer(
        f"*Реферальная программа ECHALON*\n\n"
        f"За каждого приглашённого друга, оформившего подписку,\n"
        f"Твой доступ продлевается на 7 дней\.\n\n"
        f"*Реферальная ссылка:*\n`{escaped_link}`",
        parse_mode="MarkdownV2",
        reply_markup=kb.go_home
    )


@user.callback_query(F.data == 'pay')
async def sub(callback: CallbackQuery):
    tg_id = callback.from_user.id
    paymenthodid = await find_paymethod_id(tg_id)
    if not paymenthodid:
        is_day = await find_dayend(tg_id)
        now_moscow = datetime.now(tz=MOSCOW_TZ)
        if is_day.tzinfo is None:
            is_day = is_day.replace(tzinfo=MOSCOW_TZ)

        if is_day < now_moscow:
            await callback.answer('')
            await callback.message.delete()
            await callback.message.answer(
                '<b>Абонемент не активен</b>\n\n'
                '<b>Подписка на месяц — 150₽</b>\n'
                '— Деньги будут списываться каждый месяц.\n'
                '— Отключить автопродление можно в любой момент в этом разделе.\n'
                '— При отключении доступ сохранится до конца оплаченного.\n\n'
                '<b>Важно знать:</b> подключаясь, Ты принимаешь условия\n'
                'ежемесячного списания.',
                parse_mode="HTML",
                reply_markup=kb.give_money
            )
        else:
            await callback.answer('')
            await callback.message.delete()
            await callback.message.answer(
                f"<b>Абонемент до {is_day.strftime('%d.%m.%Y')}</b>\n\n"
                f"<b>Подписка на месяц — 150₽</b>\n"
                f"— Деньги будут списываться каждый месяц.\n"
                f"— Отключить автопродление можно в любой момент в этом разделе.\n"
                f"— При отключении доступ сохранится до конца оплаченного.\n\n"
                f"<b>Важно знать:</b> подключаясь, Ты принимаешь условия\n"
                f"ежемесячного списания.",
                parse_mode="HTML",
                reply_markup=kb.give_money
            )
    else:
        is_day = await find_dayend(tg_id)
        if is_day.tzinfo is None:
            is_day = is_day.replace(tzinfo=MOSCOW_TZ)
        await callback.answer('')
        await callback.message.delete()
        await callback.message.answer(
            f"<b>Следующее списание {is_day.strftime('%d.%m.%Y')}</b>\n\n"
            f"<b>Подписка на месяц — 150₽</b>\n"
            f"— Деньги будут списываться каждый месяц.\n"
            f"— Отключить автопродление можно в любой момент в этом разделе.\n"
            f"— При отключении доступ сохранится до конца оплаченного\n\n"
            f"<b>Важно знать:</b> подключаясь, Ты принимаешь условия\n"
            f"ежемесячного списания.",
            parse_mode="HTML",
            reply_markup=kb.cancelautopay
        )

@user.callback_query(F.data == 'plsno')
async def no(callback: CallbackQuery):
    tg_id = callback.from_user.id
    await delpaymethod_id(tg_id)
    await callback.answer('')
    await callback.message.edit_text(
        'Вы успешно отменили автопродление',
        reply_markup=kb.on_main
    )


@user.callback_query(F.data == 'doitpls')
async def pay(callback: CallbackQuery):
    tg_id = callback.from_user.id
    payment_url = await create_payment(tg_id)
    kburl = payment_keyboard(payment_url)
    message_id = callback.message.message_id
    await save_message(tg_id, message_id)
    await callback.message.edit_text(
        f"Оплатите по ссылке:\n{payment_url}",
        reply_markup=kburl
    )


