from aiogram.dispatcher.filters import BoundFilter
from aiogram import types
from aiogram.dispatcher.handler import CancelHandler
from aiogram.utils.exceptions import BadRequest

from data import config
from data.config import DEVELOPER
from loader import bot, dp


class IsSubscriber(BoundFilter):
    async def check(self, message: types.Message):
        if config.test or  not config.subscription_check:
            return True
        language_code = message["from"]["language_code"]

        if language_code == 'en' or language_code == 'ru':
            chat_for_check = f'@{str(config.chanel_for_subs_ru_eng)}'
        else:
            chat_for_check = f'@{str(config.chanel_for_subs_others)}'
        try:
            chat_member_data = await bot.get_chat_member(chat_for_check, int(message.chat.id))
        except BadRequest:
            await dp.bot.send_message(DEVELOPER[0], 'Seems like bot is not admin in the subscription group')
            return True
        if chat_member_data.status != types.ChatMemberStatus.LEFT:
            return True
        else:
            await message.answer(
                f'Чтобы далее пользоваться этой функцией вступите в наш канал {chat_for_check}')
            # print(chat_member_data)
            raise CancelHandler()
