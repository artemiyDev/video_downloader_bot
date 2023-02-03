from aiogram.dispatcher.filters import BoundFilter
from aiogram import types
from aiogram.dispatcher.handler import CancelHandler

from data import config
from loader import bot


class IsSubscriber(BoundFilter):
    async def check(self, callback: types.CallbackQuery):
        if config.test or  not config.subscription_check:
            return True
        language_code = callback["from"]["language_code"]

        if language_code == 'en' or language_code == 'ru':
            chat_for_check = f'@{str(config.chanel_for_subs_ru_eng)}'
        else:
            chat_for_check = f'@{str(config.chanel_for_subs_others)}'
        chat_member_data = await bot.get_chat_member(chat_for_check, int(callback.message.chat.id))

        if chat_member_data.status != types.ChatMemberStatus.LEFT:
            return True
        else:
            await callback.message.answer(
                f'Чтобы далее пользоваться этой функцией вступите в наш канал {chat_for_check}')
            await callback.answer()
            # print(chat_member_data)
            raise CancelHandler()
