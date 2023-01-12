import logging

from aiogram import Dispatcher

from data.config import DEVELOPER


async def on_startup_notify(dp: Dispatcher):
    for dev in DEVELOPER:
        try:
            await dp.bot.send_message(dev, "Бот Запущен")
        except Exception as err:
            logging.exception(err)
