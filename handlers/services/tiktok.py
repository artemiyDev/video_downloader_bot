from aiogram import types
from aiogram.utils.exceptions import InvalidHTTPUrlContent, CantParseEntities

from data.config import DEVELOPER
from download_services.tiktok import get_tiktok_video_url, save_tiktok
from loader import dp, root_logger
from utils.db_api.stat import increase_stat
from utils.db_api.tiktoks import get_used_tiktok_from_db, write_tiktok_to_db
from utils.text_constants import CAPTION
from filters import IsSubscriber

@dp.message_handler(IsSubscriber(), regexp='.*tiktok\.com\/@.*\/video.*|.*\.tiktok\.com.*')
async def echo(message: types.Message):
    try:
        tiktok_url = message.text.split('?')[0]

        tiktok_from_db = await get_used_tiktok_from_db(tiktok_url)

        if tiktok_from_db:
            await message.answer_video(tiktok_from_db['tg_file_id'],caption=CAPTION, parse_mode='HTML')
        else:
            tiktok_video_url = await get_tiktok_video_url(tiktok_url)
            try:
                message_data = await message.answer_video(tiktok_video_url,caption=CAPTION, parse_mode='HTML')
            except InvalidHTTPUrlContent:
                await message.answer('<b>Длинное видео. Дождись загрузки...</b>', parse_mode='HTML')
                file_path = await save_tiktok(tiktok_video_url)
                video = open(file_path, "rb")
                message_data = await message.answer_video(video=video, parse_mode='HTML',caption=CAPTION)

            file_id = message_data['video']['file_id']
            await write_tiktok_to_db(tiktok_url, file_id)
        await increase_stat('tiktok')
    except Exception as e:
        root_logger.error('Error tiktok download ' + str(tiktok_url), exc_info=True)
        try:
            await dp.bot.send_message(DEVELOPER[0], 'Error tiktok download')
            await dp.bot.send_message(DEVELOPER[0], e)
        except CantParseEntities:
            pass
        await message.answer('Произошла ошибка, попробуйте позже')
    await message.answer('Хочешь скачать еще? Просто пришли ссылку')



