from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Активировать пробный период', callback_data='period')]
])


main_old = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text= 'Оплата',callback_data='pay')],
    [InlineKeyboardButton(text='Перейти к подключению',callback_data='period')],
    [InlineKeyboardButton(text='Реферальная программа',callback_data='refka')],
    [InlineKeyboardButton(text='Помощь',callback_data='help')]
])


helps = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Поддержка',url='https://www.youtube.com/watch?v=CW5oGRx9CLM')],
    [InlineKeyboardButton(text='⬅Назад',callback_data='home')]
])


gadgets = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Android', callback_data='android'),
     InlineKeyboardButton(text='Iphone', callback_data='iphone')],
    [InlineKeyboardButton(text='Huawei', callback_data='huawei'),
     InlineKeyboardButton(text='Windows', callback_data='windows')],
    [InlineKeyboardButton(text='MacOS', callback_data='macos'),
     InlineKeyboardButton(text='Android TV', callback_data='androidtv')]
])


downloadand = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Скачать приложение',
                          url='https://play.google.com/store/apps/details?id=com.v2raytun.android')],
    [InlineKeyboardButton(text='⬅Назад', callback_data='period'),
     InlineKeyboardButton(text='Видео инструкция', url='https://www.youtube.com/watch?v=CW5oGRx9CLM')],
    [InlineKeyboardButton(text='↩️На главную', callback_data='home')]
])


downloadiph = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Скачать приложение', url='https://apps.apple.com/lt/app/v2raytun/id6476628951')],
    [InlineKeyboardButton(text='⬅Назад', callback_data='period'),
     InlineKeyboardButton(text='Видео инструкция', url='https://www.youtube.com/watch?v=CW5oGRx9CLM')],
    [InlineKeyboardButton(text='↩️На главную', callback_data='home')]
])


downloadHUA = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Скачать приложение', url='https://www.youtube.com/watch?v=CW5oGRx9CLM')],
    [InlineKeyboardButton(text='⬅Назад', callback_data='period')],
    [InlineKeyboardButton(text='↩️На главную', callback_data='home')]
])


downloaddich = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Скачать приложение', url='https://www.youtube.com/watch?v=CW5oGRx9CLM')],
    [InlineKeyboardButton(text='⬅Назад', callback_data='period'),
     InlineKeyboardButton(text='Видео инструкция', url='https://www.youtube.com/watch?v=CW5oGRx9CLM')],
    [InlineKeyboardButton(text='↩️На главную', callback_data='home')]
])


downloadwin = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Скачать приложение', url='https://github.com/MatsuriDayo/nekoray/releases'
                                                         '/download/4.0.1/nekoray-4.0.1-2024-12-12-windows64.zip')],
    [InlineKeyboardButton(text='⬅Назад', callback_data='period'),
     InlineKeyboardButton(text='Видео инструкция', url='https://www.youtube.com/watch?v=CW5oGRx9CLM')],
    [InlineKeyboardButton(text='↩️На главную', callback_data='home')]
])


downloadTV = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Пульт для Android', url='https://play.google.com'
                                                        '/store/apps/details?id=tech.simha.androidtvremote&hl=en_US'),
     InlineKeyboardButton(text='Пульт для Iphone', url='https://apps.apple.com'
                                                       '/ru/app/remote-for-android-tv/id1668755298')],
    [InlineKeyboardButton(text='⬅Назад', callback_data='period')],
    [InlineKeyboardButton(text='↩️На главную', callback_data='home')]
])


go_home = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='⬅Назад', callback_data='home')]
])


on_main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='↩️На главную', callback_data='home')]
])


go_pay = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Оформить подписку', callback_data='pay')]
])


give_money = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Перейти к оплате', callback_data='doitpls')],
    [InlineKeyboardButton(text='⬅Назад', callback_data='home')]
])


gadgets_old = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Android', callback_data='android'),
     InlineKeyboardButton(text='Iphone', callback_data='iphone')],
    [InlineKeyboardButton(text='Huawei', callback_data='huawei'),
     InlineKeyboardButton(text='Windows', callback_data='windows')],
    [InlineKeyboardButton(text='MacOS', callback_data='macos'),
     InlineKeyboardButton(text='Android TV', callback_data='androidtv')],
    [InlineKeyboardButton(text='⬅Назад', callback_data='home')]
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

cancelautopay = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Отмена авотпродления', callback_data="plsno")],
    [InlineKeyboardButton(text='⬅Назад', callback_data='home')]
])

def payment_keyboard(payurl: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Оплатить", url=payurl)],
        [InlineKeyboardButton(text="↩️На главную", callback_data="home")]
    ])


