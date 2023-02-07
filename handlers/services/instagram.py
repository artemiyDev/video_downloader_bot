from aiogram import types
from aiogram.dispatcher import FSMContext

from aiogram.utils.exceptions import WrongFileIdentifier, InvalidHTTPUrlContent

from data.config import DEVELOPER
from filters import IsSubscriber
from loader import dp, root_logger
from utils.db_api.instagram import write_post_to_db, get_used_post_from_db
from download_services.instagram import get_post_content, save_reel, del_temp_reel
from utils.db_api.stat import update_last_message_and_last_action_timestamp, increase_stat, update_subscriber


@dp.message_handler(IsSubscriber(), regexp='.*instagram.com.*')
async def get_post_handler(message: types.Message, state: FSMContext):
    async def send_menu_and_finish_state(user_id, state):
        await state.finish()
        await update_last_message_and_last_action_timestamp(user_id, message.text)

    async def send_multiple_post(post):
        message_media = types.MediaGroup()
        post_medias = post.get_sidecar_nodes(start=0, end=-1)
        for post_media in post_medias:
            if post_media.video_url:
                message_media.attach_video(post_media.video_url)
            else:
                message_media.attach_photo(post_media.display_url)
        try:
            await message.answer_media_group(message_media)
        except (WrongFileIdentifier, InvalidHTTPUrlContent):
            message_media = types.MediaGroup()
            for idx, post_media in enumerate(post_medias):
                pathes_for_del = []
                if post_media.video_url:
                    file_path = await save_reel(short_code + str(idx), post_media.video_url)
                    video = open(file_path, "rb")
                    message_media.attach_video(video)
                    pathes_for_del.append(file_path)
                else:
                    message_media.attach_photo(post_media.display_url)
            await message.answer_media_group(message_media)
            if pathes_for_del:
                for file_path in pathes_for_del:
                    await del_temp_reel(file_path)

    async def send_single_post(post):
        if post.video_url:
            try:
                message_data = await message.answer_video(post.video_url, caption=caption,
                                                          parse_mode='HTML')
                try:
                    file_id = message_data['video']['file_id']
                except TypeError:
                    file_id = message_data['animation']['file_id']
            except (InvalidHTTPUrlContent, WrongFileIdentifier):
                await message.answer('<b>Длинное видео. Дождись загрузки...</b>')
                file_path = await save_reel(short_code, post.video_url)
                video = open(file_path, "rb")
                message_data = await message.answer_video(video=video, caption=caption, parse_mode='HTML')
                file_id = message_data['video']['file_id']
                await del_temp_reel(file_path)

        else:
            message_data = await message.answer_photo(post.url, caption=caption, parse_mode='HTML')
            file_id = message_data['photo'][-1]['file_id']
        await write_post_to_db(ig_type, short_code, post, file_id)

    url = ''
    user_id = str(message.from_user['id'])
    try:
        url = message.text.strip()
        print(url)
        if 'instagram.com/reel/' in url:
            short_code = url.split('/reel/')[1].split('/')[0]
            ig_type = 'reel'
        elif 'instagram.com/p/' in url:
            short_code = url.split('/p/')[1].split('/')[0]
            ig_type = 'p'
        elif 'instagram.com/tv/' in url:
            short_code = url.split('/tv/')[1].split('/')[0]
            ig_type = 'tv'
        else:
            if 'instagram.com/stories/' in url:
                await message.answer('Сторис бот не скачивает')
            else:
                await message.answer('Вы ввели некорректную ссылку или аккаунт приватный!')
            await send_menu_and_finish_state(user_id, state)
            return

        caption = "Бро, спасибо, что пользуешься " + "<a href='https://t.me/instaROCKbot?start=repost'>@instaROCKbot</a>" + "\nОбнял, приподнял!"

        post_from_db = await get_used_post_from_db(ig_type, short_code)

        if post_from_db:
            print('Пост из базы')
            if post_from_db['post_text']:
                await message.answer(post_from_db['post_text'])
            if post_from_db['post_video']:
                await message.answer_video(post_from_db['tg_file_id'], caption=caption, parse_mode='HTML')
            else:
                await message.answer_photo(post_from_db['tg_file_id'], caption=caption, parse_mode='HTML')
        else:
            post = await get_post_content(short_code)
            if post == 'error':
                await message.answer('Произошла ошибка, попробуйте позже')
            elif post == 'error_link':
                await message.answer('Вы ввели некорректную ссылку или аккаунт приватный!')
            else:
                if ig_type == 'p' and post.mediacount > 1:
                    await send_multiple_post(post)
                else:
                    await send_single_post(post)
                if post.caption:
                    post_caption = post.caption.strip()
                    try:
                        await message.answer(post_caption)
                    except:
                        root_logger.error('Error post download ' + str(url), exc_info=True)
    except Exception as e:
        root_logger.error('Error post download ' + str(url), exc_info=True)
        await dp.bot.send_message(DEVELOPER[0], e)
        await message.answer('Произошла ошибка, попробуйте позже')
    await message.answer('Хочешь скачать еще? Просто пришли ссылку')
    await send_menu_and_finish_state(user_id, state)
    await update_subscriber(user_id)
    await increase_stat('instagram')
