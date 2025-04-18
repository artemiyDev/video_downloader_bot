import os
import time
import traceback

from aiogram import types
from aiogram.types import InputFile
from aiogram.utils.exceptions import CantParseEntities
from pytube.exceptions import RegexMatchError
from data.config import DEVELOPER
from download_services.youtube import download_youtube_video
from filters.users_filters import check_subscription
from loader import dp, root_logger
from utils.db_api.stat import increase_stat
from utils.db_api.youtube import write_youtube_to_db, get_used_youtube_from_db
from utils.text_constants import CAPTION, PROMO_MESSAGE
from data import config 

@dp.message_handler(regexp='.*youtu\.be\/.*|.*youtube\.com\/.*')
async def echo(message: types.Message):
    try:
        video_url = message.text.strip()
        video_from_db = await get_used_youtube_from_db(video_url)
        if video_from_db:
            await message.answer_video(video_from_db['tg_file_id'],caption=CAPTION, parse_mode='HTML')
        else:
            await message.answer('<b>Дождись загрузки...</b>', parse_mode='HTML')
            video_file_path, thumb_file_path, resolution = await download_youtube_video(video_url,message.chat.id)

            for retry in range(3):
                try:
                    print(video_file_path)
                    print(thumb_file_path)
                    video = InputFile(video_file_path)
                    thumb = InputFile(thumb_file_path)
                    message_data = await message.answer_video(video=video, parse_mode='HTML', supports_streaming=True, thumb=thumb,
                                                              height=resolution, width=(resolution / 9) * 16,caption=CAPTION)
                    break
                except FileNotFoundError:
                    time.sleep(1)
                except:
                    traceback.print_exc()
                    time.sleep(1)


            file_id = message_data['video']['file_id']

            await write_youtube_to_db(video_url, file_id)
        if config.subscription_check:
            subscribed = await check_subscription(message)
            if not subscribed:
                await dp.bot.send_message(message.chat.id, PROMO_MESSAGE, disable_web_page_preview=True,
                                          parse_mode='HTML')
        await increase_stat('youtube')
    except RegexMatchError:
        await message.answer('Неверная ссылка')
    except Exception as e:
        traceback.print_exc()
        root_logger.error('Error youtube download ' + str(video_url), exc_info=True)
        try:
            await dp.bot.send_message(DEVELOPER[0], 'Error youtube download')
            await dp.bot.send_message(DEVELOPER[0], e)
            await dp.bot.send_message(DEVELOPER[0], video_url)
        except CantParseEntities:
            pass
        await message.answer('Произошла ошибка, попробуйте позже')
    finally:
        try:
            os.remove(video_file_path)
        except:
            pass
        try:
            os.remove(thumb_file_path)
        except:
            pass
    await message.answer('Хочешь скачать еще? Просто пришли ссылку')