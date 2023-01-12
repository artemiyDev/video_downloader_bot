from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

start_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='В главное меню',callback_data='main_menu')]
    ],
    resize_keyboard=True
)
