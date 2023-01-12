# import traceback
#
# import aiogram
# from aiogram import types
# from aiogram.dispatcher import FSMContext
# from aiogram.types import CallbackQuery
# from aiogram.utils.exceptions import MessageTextIsEmpty, CantParseEntities, WrongFileIdentifier, InvalidHTTPUrlContent
# from aiogram.utils.markdown import escape_md
# from instaloader import BadResponseException, PostChangedException
#
# from data.config import ADMINS, DEVELOPER
# from filters import IsSubscriber
# from states import PostDownloadStates
# from keyboards.inline import main_menu, main_menu_admin
from loader import dp, root_logger
# from utils.db_api.check_used_posts import write_post_to_db, get_used_post_from_db
# from utils.ig_content_downloader import get_post_content, save_reel, del_temp_reel, check_is_reel_huge
# import logging
#
# from utils.misc import rate_limit
# from utils.text_constants import MAIN_MENU_MESSAGE
# from utils.db_api.db_functions import update_last_message_and_last_action_timestamp, increase_stat, update_subscriber
#
#
# @dp.callback_query_handler(IsSubscriber(), text="get_post_content")
# async def input_post_link_handler(callback: CallbackQuery):
#     await callback.answer()
#     await callback.message.answer('Отправь ссылку на пост или reels')
#     await PostDownloadStates.S1.set()
#
#
# @rate_limit(5)
# @dp.message_handler(state=PostDownloadStates.S1)
# async def get_post_handler(message: types.Message, state: FSMContext):
#     url = ''
#     user_id = str(message.from_user['id'])
#     try:
#         url = message.text.strip()
#         print(url)
#         if 'instagram.com/reel/' in url:
#             short_code = url.split('/reel/')[1].split('/')[0]
#             ig_type = 'reel'
#         elif 'instagram.com/p/' in url:
#             short_code = url.split('/p/')[1].split('/')[0]
#             ig_type = 'p'
#         elif 'instagram.com/tv/' in url:
#             short_code = url.split('/tv/')[1].split('/')[0]
#             ig_type = 'tv'
#         else:
#             await message.answer('Вы ввели некорректную ссылку или аккаунт приватный!')
#             if user_id in ADMINS:
#                 await message.answer(MAIN_MENU_MESSAGE, reply_markup=main_menu_admin)
#             else:
#                 await message.answer(MAIN_MENU_MESSAGE, reply_markup=main_menu)
#             await state.finish()
#             await update_last_message_and_last_action_timestamp(user_id, message.text)
#             return
#         caption = "Бро, спасибо, что пользуешься " + "<a href='https://t.me/instaROCKbot?start=repost'>@instaROCKbot</a>" + "\nОбнял, приподнял!"
#
#         post_from_db = await get_used_post_from_db(ig_type, short_code)
#
#         if post_from_db:
#             print('Пост из базы')
#             if post_from_db['post_text']:
#                 try:
#                     await message.answer(post_from_db['post_text'])
#                 except:
#                     traceback.print_exc()
#             if post_from_db['post_video']:
#                 await message.answer_video(post_from_db['tg_file_id'], caption=caption, parse_mode='HTML')
#             else:
#                 await message.answer_photo(post_from_db['tg_file_id'], caption=caption, parse_mode='HTML')
#         else:
#             post = await get_post_content(short_code)
#
#             if post == 'error':
#                 await message.answer('Произошла ошибка, попробуйте позже')
#             else:
#                 post_hashtags = ', '.join(post.caption_hashtags)
#                 post_caption_mentions = ', '.join(post.caption_mentions)
#                 post_tagged_users = ', '.join(post.tagged_users)
#
#                 if ig_type == 'p' and post.mediacount > 1:
#                     message_media = types.MediaGroup()
#                     post_medias = post.get_sidecar_nodes(start=0, end=-1)
#                     for post_media in post_medias:
#                         if post_media.video_url:
#                             message_media.attach_video(post_media.video_url)
#                         else:
#                             message_media.attach_photo(post_media.display_url)
#                     try:
#                         await message.answer_media_group(message_media)
#                     except (WrongFileIdentifier,InvalidHTTPUrlContent):
#                         post_medias = post.get_sidecar_nodes(start=0, end=-1)
#                         message_media = types.MediaGroup()
#                         for idx,post_media in enumerate(post_medias):
#                             pathes_for_del = []
#                             if post_media.video_url:
#                                 file_path = await save_reel(short_code+str(idx), post_media.video_url)
#                                 video = open(file_path, "rb")
#                                 message_media.attach_video(video)
#                                 pathes_for_del.append(file_path)
#
#                             else:
#                                 message_media.attach_photo(post_media.display_url)
#                         await message.answer_media_group(message_media)
#                         if pathes_for_del:
#                             for file_path in pathes_for_del:
#                                 await del_temp_reel(file_path)
#                 else:
#                     if post.video_url:
#                         try:
#                             message_data = await message.answer_video(post.video_url, caption=caption,
#                                                                       parse_mode='HTML')
#                             # print(message_data)
#                             try:
#                                 file_id = message_data['video']['file_id']
#                             except TypeError:
#                                 file_id = message_data['animation']['file_id']
#                         except (InvalidHTTPUrlContent, WrongFileIdentifier):
#                             await message.answer('<b>Длинное видео. Дождись загрузки...</b>')
#                             file_path = await save_reel(short_code, post.video_url)
#                             video = open(file_path, "rb")
#                             message_data = await message.answer_video(video=video, caption=caption, parse_mode='HTML')
#                             file_id = message_data['video']['file_id']
#                             await del_temp_reel(file_path)
#                         await write_post_to_db(ig_type, short_code, post.owner_username, post.title, None,
#                                                post.video_url,
#                                                post.caption,
#                                                post.date_utc, post_hashtags, post_caption_mentions, post_tagged_users,
#                                                post.video_view_count, post.likes, post.comments, None, file_id)
#                     else:
#                         message_data = await message.answer_photo(post.url, caption=caption, parse_mode='HTML')
#                         file_id = message_data['photo'][-1]['file_id']
#                         await write_post_to_db(ig_type, short_code, post.owner_username, post.title, post.url, None,
#                                                post.caption,
#                                                post.date_utc, post_hashtags, post_caption_mentions, post_tagged_users,
#                                                post.video_view_count, post.likes, post.comments, None, file_id)
#                 if post.caption:
#                     post_caption = post.caption.replace('<', '&lt;').replace('>', '&gt;').replace("&", "&amp;").replace(
#                         '"', "&quot;")
#                     try:
#                         await message.answer(post_caption)
#                     except:
#                         root_logger.error('Error post download ' + str(url), exc_info=True)
#     except (BadResponseException,PostChangedException):
#         await message.answer('Вы ввели некорректную ссылку или аккаунт приватный!')
#     except (IndexError, MessageTextIsEmpty, WrongFileIdentifier):
#         root_logger.error('Error post download ' + str(url), exc_info=True)
#         await message.answer('Вы ввели некорректную ссылку или аккаунт приватный!')
#     except (InvalidHTTPUrlContent):
#         root_logger.error('Error post download ' + str(url), exc_info=True)
#         await message.answer('Произошла ошибка')
#     except Exception as e:
#         root_logger.error('Error post download ' + str(url), exc_info=True)
#         try:
#             await dp.bot.send_message(DEVELOPER[0], e)
#         except CantParseEntities:
#             pass
#         await message.answer('Произошла ошибка, попробуйте позже')
#     if user_id in ADMINS:
#         await message.answer(MAIN_MENU_MESSAGE, reply_markup=main_menu_admin)
#     else:
#         await message.answer(MAIN_MENU_MESSAGE, reply_markup=main_menu)
#     await state.finish()
#     await update_last_message_and_last_action_timestamp(user_id, message.text)
#     await update_subscriber(user_id)
#     await increase_stat('download_count')
