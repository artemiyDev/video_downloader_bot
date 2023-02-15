import os
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.exceptions import WrongFileIdentifier

from data.config import ADMINS, DEVELOPER
from download_services.pinterest import get_pin_content, save_video
from filters import IsSubscriber
from loader import dp
from utils.db_api.stat import increase_stat
from utils.db_api.user import update_last_message_and_last_action_timestamp
from utils.text_constants import CAPTION


@dp.message_handler(regexp='.*pinterest.com.*|.*pin.it.*')
async def get_pin_handler(message: types.Message, state: FSMContext):
    user_id = str(message.from_user['id'])
    url = message.text.strip()
    print(url)
    if len(message.text.strip().split('https')) > 1:
        url = 'https' + message.text.strip().split('https')[1]
    if 'pin.it/' in url or '/pin/' in url:
        pin_content = await get_pin_content(url)
        # print(pin_content)
    else:
        await message.answer('Вы ввели некорректную ссылку!')
        await state.finish()
        await update_last_message_and_last_action_timestamp(user_id, message.text)
        return
    if not pin_content:
        await message.answer('Произошла ошибка, попробуйте позже')
        await dp.bot.send_message(DEVELOPER[0], "Pin error")
        await dp.bot.send_message(DEVELOPER[0], url)
    else:
        text = ''
        if pin_content['title']:
            text += pin_content['title']
        if pin_content['description']:
            text += '\n\n' + pin_content['description']
        if len(pin_content['media']) > 1:
            message_media = types.MediaGroup()
            for media in pin_content['media']:
                if media['video_url']:
                    message_media.attach_video(media['video_url'])
                else:
                    message_media.attach_photo(media['image_url'])
            await message.answer_media_group(message_media)
        else:
            # print(pin_content)
            if pin_content['media'][0]['video_url']:
                try:
                    await message.answer_video(pin_content['media'][0]['video_url'], parse_mode='HTML', caption=CAPTION)
                except WrongFileIdentifier:
                    await message.answer_video('Видео скачивается...Пожалуйста подождите...')
                    file_path = await save_video(pin_content['media'][0]['video_url'], user_id)
                    video = open(file_path, "rb")
                    await message.answer_video(video, caption=CAPTION, parse_mode='HTML')
                    os.remove(file_path)
                    pass
            else:
                await message.answer_photo(pin_content['media'][0]['image_url'], caption=CAPTION, parse_mode='HTML')
        if text:
            await message.answer(text)
    await message.answer('Хочешь скачать еще? Просто пришли ссылку')
    await state.finish()
    await update_last_message_and_last_action_timestamp(user_id, message.text)
    await increase_stat('pinterest')
