from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandHelp

from data.config import ADMINS
from keyboards.inline import main_menu_admin, main_menu
from loader import dp
from utils.text_constants import MAIN_MENU_MESSAGE


@dp.message_handler(CommandHelp())
async def bot_help(message: types.Message):
    if str(message.from_user['id']) in ADMINS:
        await message.answer(MAIN_MENU_MESSAGE, reply_markup=main_menu_admin)
    else:
        await message.answer(MAIN_MENU_MESSAGE, reply_markup=main_menu)
