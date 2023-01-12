from aiogram import types

from download_services.tiktok import get_tiktok_video_url
from loader import dp, root_logger



@dp.message_handler(regexp='.*tiktok\.com\/@.*\/video.*')
async def echo(message: types.Message):
    tiktok_url = message.text
    tiktok_video_url = await get_tiktok_video_url(tiktok_url)
    await message.answer_video(tiktok_video_url)