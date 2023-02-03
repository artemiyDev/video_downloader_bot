from aiogram import types
from aiogram.types import CallbackQuery
from data.config import ADMINS

from loader import dp, unkwnown_links_logger


@dp.message_handler()
async def handler(message):
    unkwnown_links_logger.critical(message.text.strip())
    await message.answer('Неизвестный сервис')