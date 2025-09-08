from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command, Filter
from aiogram.fsm.context import FSMContext
import app.keyboard as kb
from app.stats import Newsletter, Newsonlyvip, Newsonlybroke
from app.database.requests import get_users, get_vip, get_broke

admin = Router()

class Admin(Filter):
    async def __call__(self, message: Message):
        return message.from_user.id in [1175542555, 5291160519]


@admin.message(Admin(), Command('newsletter'))
async def newsmenu(message: Message):
    await message.answer(text='выбери тип рассылки', reply_markup=kb.admin)


@admin.callback_query(Admin(), F.data == 'cancel')
async def newsmenu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer(text='выбери тип рассылки', reply_markup=kb.admin)


@admin.callback_query(Admin(), F.data == 'send_all')
async def newsall(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Newsletter.message)
    await callback.message.answer(text='Введите текс рассылки(всем)', reply_markup=kb.admin_panel)


@admin.callback_query(Admin(), F.data == 'send_vip')
async def newsall(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Newsonlyvip.message)
    await callback.message.answer(text='Введите текс рассылки(виперам)', reply_markup=kb.admin_panel)


@admin.callback_query(Admin(), F.data == 'send_broke')
async def newsall(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Newsonlybroke.message)
    await callback.message.answer(text='Введите текс рассылки(броукам)', reply_markup=kb.admin_panel)


@admin.message(Newsletter.message)
async def newsmessage_all(message: Message, state: FSMContext):
    await state.clear()
    users = await get_users()
    for tg_id in users:
        try:
            await message.send_copy(chat_id=tg_id)
        except Exception as e:
            print (e)


@admin.message(Newsonlyvip.message)
async def newsmessage_vip(message: Message, state: FSMContext):
    await state.clear()
    users = await get_vip()
    for tg_id in users:
        try:
            await message.send_copy(chat_id=tg_id)
        except Exception as e:
            print(e)


@admin.message(Newsonlybroke.message)
async def newsmessage_broke(message: Message, state: FSMContext):
    await state.clear()
    users = await get_broke()
    for tg_id in users:
        try:
            await message.send_copy(chat_id=tg_id)
        except Exception as e:
            print (e)

@admin.message(Admin(), F.photo)
async def get_photo(message: Message):
    await message.answer(f'ID фотографии: {message.photo[-1].file_id}')