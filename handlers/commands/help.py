from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandHelp

from data.config import ADMINS
from loader import dp
from utils.text_constants import MAIN_MENU_MESSAGE


@dp.message_handler(CommandHelp())
async def bot_help(message: types.Message):
    if str(message.from_user['id']) in ADMINS:
        await message.answer(MAIN_MENU_MESSAGE)
    else:
        await message.answer(MAIN_MENU_MESSAGE)
