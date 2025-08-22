import os
from dotenv import load_dotenv
from aiogram import Bot

load_dotenv()

TOKEN=('8198715354:AAE1Da_41VnpaxnjsKqk64KZB7V2wUCT7Uc')
bot = Bot(token=TOKEN)
mybot = ('https://web.telegram.org/k/#@test0viybotnafig_bot')
yookassa_shopid = ('1028866')
yookassa_api = ('test_mW2Dr5Qvh94kNvQga4zWDKs5wWZcBcbAqY-0cuIlsA4')
BASE_URL = "https://set.kabinetboos.ru:47342/7Q2B7v7PUsInwA3/"
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://vpnuser:vpnpass@localhost:5432/vpn"
)