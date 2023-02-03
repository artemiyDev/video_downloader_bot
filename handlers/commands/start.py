from loader import dp
from aiogram import types
from aiogram.dispatcher import FSMContext

from utils.db_api.user import create_user
from utils.text_constants import START_MESSAGE
from keyboards.inline import start_menu


@dp.message_handler(commands=['start'], state='*')
async def bot_start(message: types.Message, state: FSMContext):
    await create_user(message)

    current_state = await state.get_state()
    if current_state is not None:
        await state.finish()

    await message.answer(START_MESSAGE,parse_mode=types.ParseMode.HTML)
