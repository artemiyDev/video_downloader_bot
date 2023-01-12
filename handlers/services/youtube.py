from aiogram import types

from loader import dp, root_logger


# https://youtu.be/CzZqTd4Peg8
# https://www.youtube.com/watch?v=CzZqTd4Peg8


@dp.message_handler(regexp='.*youtu\.be\/.*|.*youtube\.com\/.*')
async def echo(message: types.Message):
    await message.answer('youtube')
