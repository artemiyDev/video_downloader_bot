from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandHelp

from loader import dp
from utils.text_constants import MAIN_MENU_MESSAGE


@dp.message_handler(CommandHelp())
async def bot_help(message: types.Message):
    await message.answer(MAIN_MENU_MESSAGE, parse_mode=types.ParseMode.HTML)
