import os
from asyncio import sleep

from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, ContentType, ParseMode
from data.config import ADMINS
from data import config
from aiogram.types import InputFile
from utils.db_api.db_functions import *
from loader import dp, bot, db
from utils.db_api.db_setup_functions import toggle_refferals_status, change_group_for_subs_in_db, \
    get_inactive_mailing_texts, update_invite_link, get_inactive_mailing_status, toggle_inactive_mailing_status, \
    get_inactive_mailing_user_stat
from utils.text_constants import MAIN_MENU_MESSAGE
from keyboards.inline import main_menu, main_menu_admin, admin_menu, referrals_status_menu
from states import MailingStates, SubsListChangeStateRuEng, SubsListChangeStateOthers, AdminSSpyStateAdd, \
    AdminSSpyStateDel
from aiogram.utils.exceptions import MessageTextIsEmpty, BotKicked, BotBlocked, UserDeactivated


class InactiveMailingData(StatesGroup):
    days = State()
    text = State()
    image = State()


@dp.callback_query_handler(text="get_admin_panel", user_id=ADMINS)
async def admin_panel_handler(callback: CallbackQuery):
    await get_total_referrals_added()
    await callback.answer()
    await callback.message.answer(MAIN_MENU_MESSAGE, reply_markup=admin_menu)


@dp.callback_query_handler(text="get_total_users_stat", user_id=ADMINS)
async def get_total_users_stat_handler(callback: CallbackQuery):
    users_amount = await count_users()
    users_blocked = await count_users(blocked_users=True)
    users_lang_stat = await get_users_language_stat()
    final_text = f'Всего пользователей: {str(users_amount)}\n\nЗаблокированных: {str(users_blocked)}\n\n' + users_lang_stat
    await callback.answer()
    await callback.message.answer(final_text,
                                  reply_markup=admin_menu, parse_mode=ParseMode.MARKDOWN_V2)


@dp.callback_query_handler(text="get_user_activity", user_id=ADMINS)
async def user_activity_handler(callback: CallbackQuery):
    reply_message = await get_users_activity()
    await callback.answer()
    await callback.message.answer(reply_message, reply_markup=admin_menu)


@dp.callback_query_handler(text="get_user_activity_by_functions", user_id=ADMINS)
async def user_activity_by_functions_handler(callback: CallbackQuery):
    reply_message = await get_users_activity_by_functions()
    await callback.answer()
    await callback.message.answer(reply_message, reply_markup=admin_menu)


@dp.callback_query_handler(text="get_new_users_by_weekdays", user_id=ADMINS)
async def new_users_by_weekdays_handler(callback: CallbackQuery):
    reply_message = await get_new_users_by_weekdays()
    await callback.message.answer(reply_message, reply_markup=admin_menu, parse_mode=ParseMode.MARKDOWN_V2)


@dp.callback_query_handler(text="create_mailing", user_id=ADMINS)
async def create_mailing_handler(callback: CallbackQuery):
    await callback.message.answer('Отправьте текст для рассылки', reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Отмена рассылки', callback_data='cancel_mailing')]
        ],
        resize_keyboard=True
    ))
    await MailingStates.S1.set()


@dp.callback_query_handler(text="cancel_mailing", user_id=ADMINS, state=MailingStates.S1)
async def cancel_maling_handler(callback, state):
    await state.finish()
    await callback.message.answer('Рассылка отменена', reply_markup=admin_menu)


@dp.message_handler(user_id=ADMINS, state=MailingStates.S1)
async def create_mailing_handler(message, state):
    users_tg_ids = await get_all_users_tg_ids(without_blocked_users=True)
    messages_sent = 0
    await message.answer(f'Рассылка начата', reply_markup=admin_menu)
    await state.finish()
    for user_tg_id in users_tg_ids[:20]:
        try:
            await bot.send_message(user_tg_id, message['text'])
            messages_sent += 1
        except (BotKicked, BotBlocked, UserDeactivated):
            sql = 'UPDATE users SET blocked = true WHERE tg_id = $1'
            await db.pool.execute(sql, int(user_tg_id))
        except Exception as e:
            print(user_tg_id)
            print(e)
        await sleep(0.05)
    await message.answer(
        f'Рассылка завершена. Успешно отправлено <b>{str(messages_sent)}</b> сообщений из <b>{str(len(users_tg_ids))}</b>')


@dp.callback_query_handler(text="get_admin_referals_status", user_id=ADMINS)
async def get_admin_referals_status_handler(callback: CallbackQuery):
    ref_amount = await get_total_referrals_added()
    reply_message = f'Текущий статус рефералов: {"Включен" if config.referrals_enabled else "Выключен"}.' \
                    f'\nКанал для подписки ru/eng:\n@{config.chanel_for_subs_ru_eng}' \
                    f'\nКанал для подписки остальные:\n@{config.chanel_for_subs_others}' \
                    f'\nПриглашено по реф ссылке: {str(ref_amount)}'
    await callback.message.answer(reply_message, reply_markup=referrals_status_menu)


@dp.callback_query_handler(text="change_ref_status", user_id=ADMINS)
async def change_ref_status_handler(callback: CallbackQuery):
    config.referrals_enabled = not config.referrals_enabled
    await toggle_refferals_status()
    reply_message = f'Статус рефераллов изменен на {"Включен" if config.referrals_enabled else "Выключен"}'
    await callback.message.answer(reply_message, reply_markup=referrals_status_menu)


@dp.callback_query_handler(text="change_group_for_subs_ru_eng", user_id=ADMINS)
async def input_groups_list_for_subs_handler(callback: CallbackQuery):
    await callback.message.answer('Отправь имя канала')
    await SubsListChangeStateRuEng.S1.set()


@dp.message_handler(user_id=ADMINS, state=SubsListChangeStateRuEng.S1)
async def change_groups_list_for_subs_handler(message, state):
    new_chanel = message['text'].strip().replace('@', '')
    await change_group_for_subs_in_db('group_for_subc_ru_eng', new_chanel)
    config.chanel_for_subs_ru_eng = new_chanel
    await message.answer(f'Канал изменен на @{new_chanel}', reply_markup=referrals_status_menu)
    await state.finish()


@dp.callback_query_handler(text="change_group_for_subs_others", user_id=ADMINS)
async def input_groups_list_for_subs_handler(callback: CallbackQuery):
    await callback.message.answer('Отправь имя канала')
    await SubsListChangeStateOthers.S1.set()


@dp.message_handler(user_id=ADMINS, state=SubsListChangeStateOthers.S1)
async def change_groups_list_for_subs_handler(message, state):
    new_chanel = message['text'].strip().replace('@', '')
    await change_group_for_subs_in_db('group_for_subc_others', new_chanel)
    config.chanel_for_subs_others = new_chanel
    await message.answer(f'Канал изменен на @{new_chanel}', reply_markup=referrals_status_menu)
    await state.finish()


@dp.callback_query_handler(text="admin_stories_spy", user_id=ADMINS)
async def admin_stories_spy_handler(callback: CallbackQuery):
    result = await get_s_spy_users_added_by_admin()
    await callback.message.answer('tg_user_id / количество аккаунтов\n' + '\n'.join(
        [f'{x["tg_id"]} {x["s_spy_can_follow"]}' for x in result]), reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Добавить', callback_data='add_admin_stories_spy')],
            [InlineKeyboardButton(text='Удалить', callback_data='del_admin_stories_spy')],
            [InlineKeyboardButton(text='Админка', callback_data='get_admin_panel')]
        ],
        resize_keyboard=True
    ))


@dp.callback_query_handler(text="add_admin_stories_spy", user_id=ADMINS)
async def add_admin_stories_spy_handler(callback: CallbackQuery):
    await callback.message.answer('Введите tg_user_id и количество аккаунтов через пробел')
    await AdminSSpyStateAdd.S1.set()


@dp.message_handler(state=AdminSSpyStateAdd.S1, user_id=ADMINS)
async def add_admin_stories_spy_handler_finish(message, state):
    message_text = message['text'].strip().split(' ')
    if len(message_text) != 2:
        await message.answer('Ошибка ввода', reply_markup=admin_menu)
    else:
        try:
            print(config.stories_spy_allowed_users_list)
            await update_s_spy_user_added_by_admin(message_text[0], message_text[1])
            await message.answer('Пользователь добавлен', reply_markup=admin_menu)
            await update_s_spy_filter()
            print(config.stories_spy_allowed_users_list)
        except Exception as e:
            await message.answer('Ошибка', reply_markup=admin_menu)
            print(e)
    await state.finish()


@dp.callback_query_handler(text="del_admin_stories_spy", user_id=ADMINS)
async def del_admin_stories_spy_handler(callback: CallbackQuery):
    await callback.message.answer('Введите tg_user_id')
    await AdminSSpyStateDel.S1.set()


@dp.message_handler(state=AdminSSpyStateDel.S1, user_id=ADMINS)
async def del_admin_stories_spy_handler_finish(message, state):
    try:
        await delete_s_spy_user_added_by_admin(message['text'].strip())
        await message.answer('Пользователь удален', reply_markup=admin_menu)
        await update_s_spy_filter()

    except Exception as e:
        await message.answer('Ошибка', reply_markup=admin_menu)
        print(e)
    await state.finish()


@dp.callback_query_handler(text="invite_links")
async def invite_links(callback: CallbackQuery):
    invite_links = await get_invite_links()
    if invite_links:
        text_for_message = ""

        for invite_link_raw in invite_links:
            invite_link = invite_link_raw['invite_link']
            invite_link_parameter = invite_link.split('start=')[1]
            total_users = await db.pool.fetchval("SELECT count(*)  FROM users where start_referal_link=$1;",
                                                 invite_link_parameter)
            active_users = await db.pool.fetchval(
                "SELECT count(*)  FROM users where start_referal_link=$1 and last_action_date is not null;",
                invite_link_parameter)
            blocked_users = await db.pool.fetchval(
                "SELECT count(*)  FROM users where start_referal_link=$1 and blocked = true;", invite_link_parameter)
            sunscribed_users = await db.pool.fetchval(
                "SELECT count(*)  FROM users where start_referal_link=$1 and subscribed_to_channel = true;",
                invite_link_parameter)
            text_for_message += f"{invite_link_raw['invite_link']}\n\nВсего: {str(total_users)}\nАктивных: {str(active_users)}\nЗаблокировали: {str(blocked_users)}\nПодписались: {str(sunscribed_users)}\n\n"
        text_for_message = text_for_message.strip()
    else:
        text_for_message = 'Нет ссылок'

    await callback.message.answer(text_for_message, reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Добавить', callback_data='add_invite_link')],
            [InlineKeyboardButton(text='Удалить', callback_data='del_invite_link')],
            [InlineKeyboardButton(text='Админка', callback_data='get_admin_panel')]
        ],
        resize_keyboard=True
    ))


@dp.callback_query_handler(text="add_invite_link")
async def add_invite_link1(callback: CallbackQuery, state):
    await callback.message.answer('Введите параметр для ссылки https://t.me/instaROCKbot?start={параметр}')
    await state.set_state("invite_link_adding")


@dp.message_handler(state='invite_link_adding')
async def add_invite_link3(message, state):
    if message['text']:
        await add_invite_link(f"https://t.me/instaROCKbot?start={message['text'].strip()}")
        await message.answer(f'Ссылка добавлена', reply_markup=admin_menu)
    else:
        await message.answer(f'Ошибка', reply_markup=admin_menu)
    await state.finish()


@dp.callback_query_handler(text="del_invite_link")
async def del_invite_link1(callback: CallbackQuery, state):
    await callback.message.answer('Введите ссылку для удаления')
    await state.set_state("del_invite_link")


@dp.message_handler(state='del_invite_link')
async def del_invite_link3(message, state):
    if message['text']:
        await del_invite_link(message['text'].strip())
        await message.answer(f'Ссылка удалена', reply_markup=admin_menu)
    else:
        await message.answer(f'Ошибкаaaa', reply_markup=admin_menu)
    await state.finish()


@dp.callback_query_handler(text="inactive_mailing")
async def inactive_mailing_handler(callback: CallbackQuery):
    stat_text = await get_inactive_mailing_user_stat()
    inactive_mailing_status = await get_inactive_mailing_status()
    if inactive_mailing_status:
        inactive_mailing_status = 'Статус рассылки: <b>ВКЛЮЧЕНА</b>'
    else:
        inactive_mailing_status = 'Статус рассылки: <b>ВЫКЛЮЧЕНА</b>'
    stat_text += '\n\n' + inactive_mailing_status
    await callback.message.answer(stat_text, reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Редактировать тексты и фото', callback_data='inactive_mailing_content')],
            [InlineKeyboardButton(text='Изменить статус', callback_data='change_inactive_mailing_status')],
            [InlineKeyboardButton(text='Админка', callback_data='get_admin_panel')]
        ],
        resize_keyboard=True
    ))


@dp.callback_query_handler(text="inactive_mailing_content")
async def invite_links(callback: CallbackQuery):
    invite_links = await get_inactive_mailing_texts()

    text_for_message = '\n\n<b>Текст и изображения для рассылки неактивным пользователям</b>'

    await callback.message.answer(text_for_message)

    for day in [['three', 3], ['seven', 7], ['onefive', 15]]:
        await callback.message.answer(f'<b>День {str(day[1])}</b>')
        try:
            text = invite_links[f'{day[0]}_days_inactive_mailing_text']
            if text:
                await callback.message.answer('Текст:\n\n' + text)
        except MessageTextIsEmpty:
            pass
        try:
            photo = open(f'utils/images_for_mailing/{str(day[1])}.jpg', "rb")
        except FileNotFoundError:
            continue
        await bot.send_photo(callback.message.chat.id, photo)

    await callback.message.answer(text_for_message, reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Редактировать', callback_data='change_inactive_mailing_link')],
            [InlineKeyboardButton(text='Админка', callback_data='get_admin_panel')]
        ],
        resize_keyboard=True
    ))


@dp.callback_query_handler(text="change_inactive_mailing_status")
async def change_inactive_mailing_status(callback: CallbackQuery):
    await toggle_inactive_mailing_status()
    inactive_mailing_status = await get_inactive_mailing_status()
    if inactive_mailing_status:
        inactive_mailing_status = 'Статус рассылки изменен на <b>ВКЛЮЧЕНА</b>'
    else:
        inactive_mailing_status = 'Статус рассылки изменен на <b>ВЫКЛЮЧЕНА</b>'
    await callback.message.answer(inactive_mailing_status, reply_markup=admin_menu)


@dp.callback_query_handler(text="change_inactive_mailing_link")
async def change_inactive_mailing_link1(callback: CallbackQuery, state):
    await InactiveMailingData.days.set()
    await callback.message.answer('Введите количество дней (3, 7 ,15)')


@dp.message_handler(state=InactiveMailingData.days)
async def change_inactive_mailing_link1(message, state):
    async with state.proxy() as data:
        data['days'] = message.text
    await InactiveMailingData.next()
    await message.reply("Пришли текст")


@dp.message_handler(state=InactiveMailingData.text)
async def change_inactive_mailing_link2(message, state):
    async with state.proxy() as data:
        data['text'] = message.text
    await InactiveMailingData.next()
    await message.answer('Пришли картинку. Чтобы пропустить пришли "нет"', reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Удалить картинку', callback_data='del_image_mailing_link')]
        ],
        resize_keyboard=True
    ))


@dp.callback_query_handler(state=InactiveMailingData.image, text="del_image_mailing_link")
async def del_image_mailing_link(callback: CallbackQuery, state):
    async with state.proxy() as data:
        days = data['days']
    try:
        os.remove(f'utils/images_for_mailing/{str(days)}.jpg')
        await callback.message.answer('Картинка удалена', reply_markup=admin_menu)
    except:
        await callback.message.answer('Ошибка', reply_markup=admin_menu)
    await state.finish()


@dp.message_handler(state=InactiveMailingData.image, content_types=ContentType.all())
async def change_inactive_mailing_link3(message, state):
    async with state.proxy() as data:
        days = data['days']
        text = data['text']
    await update_invite_link(days, text)
    if message.text:
        await state.finish()
        await message.answer('Сообщение для рассылки обновлено', reply_markup=admin_menu)
    else:
        file = await bot.get_file(message['document']['file_id'])
        await bot.download_file(file.file_path, f'utils/images_for_mailing/{str(days)}.jpg')
        await state.finish()
        await message.answer('Сообщение для рассылки обновлено', reply_markup=admin_menu)


@dp.callback_query_handler(text="top_five_posts", user_id=ADMINS)
async def get_top_five_posts_handler(callback: CallbackQuery, state):
    posts = await get_top_five_posts()
    for post in posts:
        url = f'https://www.instagram.com/{post["ig_type"]}/{post["short_code"]}'
        if not post["post_video"]:
            await callback.message.answer_photo(post['tg_file_id'],
                                                caption=str(post["download_times_counter"]) + '\n\n' + url)
        else:
            await callback.message.answer_video(post['tg_file_id'],
                                                caption=str(post["download_times_counter"]) + '\n\n' + url)
    await state.finish()
    await callback.message.answer(MAIN_MENU_MESSAGE, reply_markup=admin_menu)
