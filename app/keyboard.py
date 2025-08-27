from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Активировать пробный период', callback_data='period')]
])


main_old = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='💳 Таирфы и оплата',callback_data='pay')],
    [InlineKeyboardButton(text='📡 Перейти к подключенью',callback_data='period')],
    [InlineKeyboardButton(text='💸 Реферальная программа',callback_data='refka')],
    [InlineKeyboardButton(text='🛟 Помощь',callback_data='help')]
])


gadgets = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Android📱', callback_data='android'),
     InlineKeyboardButton(text='Iphone📱', callback_data='iphone')],
    [InlineKeyboardButton(text='Huawei 🇨🇳', callback_data='huawei'),
     InlineKeyboardButton(text='Windows💻', callback_data='windows')],
    [InlineKeyboardButton(text='MacOS💻', callback_data='macos'),
     InlineKeyboardButton(text='Android TV 📺', callback_data='androidtv')]
])


download = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='↩️Назад', callback_data='period')], #после добавлю кнопку видео инструкция
    [InlineKeyboardButton(text='↩️На главную', callback_data='home')]       # с сылкай на закрытую группу в тг
])


go_home = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='↩️Назад', callback_data='home')],
])


go_pay = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Оформить подписку', callback_data='pay')]
])


give_money = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='150р/мес', callback_data='doitpls')],
    [InlineKeyboardButton(text='↩️Назад', callback_data='home')]
])


gadgets_old = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Android📱', callback_data='android'),
     InlineKeyboardButton(text='Iphone📱', callback_data='iphone')],
    [InlineKeyboardButton(text='Huawei 🇨🇳', callback_data='huawei'),
     InlineKeyboardButton(text='Windows💻', callback_data='windows')],
    [InlineKeyboardButton(text='MacOS💻', callback_data='macos'),
     InlineKeyboardButton(text='Android TV 📺', callback_data='androidtv')],
    [InlineKeyboardButton(text='↩️Назад', callback_data='home')]
])


admin = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='рассылка всем пользователям', callback_data='send_all')],
    [InlineKeyboardButton(text='рассылка только платикам', callback_data='send_vip')],
    [InlineKeyboardButton(text='рассылка только броукам', callback_data='send_broke')],
    [InlineKeyboardButton(text='↩️На главную', callback_data='home')]
])

admin_panel = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Отмена', callback_data='cancel')]
])

def payment_keyboard(payurl, payment_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Оплатить", url=payurl)],
        [InlineKeyboardButton(text="Отмена", callback_data=f"cancel:{payment_id}")]
    ])
