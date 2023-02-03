from asyncio import sleep

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.exceptions import BotKicked, BotBlocked, UserDeactivated, MessageTextIsEmpty

from data import config
from data.config import ADMINS
from loader import dp, bot, db, root_logger
from states import MailingStates, SubsListChangeStateRuEng, SubsListChangeStateOthers
from utils.db_api.admin import get_all_users_tg_ids, get_inactive_mailing_user_stat, \
    get_inactive_mailing_status, toggle_inactive_mailing_status, update_inactive_mailing_image, update_invite_link, \
    toggle_subscription_check_status, change_group_for_subs_in_db
from utils.db_api.setup import get_setup_data
from utils.db_api.stat import count_users, get_users_language_stat, get_users_activity, get_users_activity_by_functions, \
    get_new_users_by_weekdays
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ContentType

admin_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Статистика', callback_data='get_users_stat')],
        [InlineKeyboardButton(text='Создать рассылку', callback_data='create_mailing')],
        [InlineKeyboardButton(text='Проверка подписки', callback_data='get_subscription_check_status')],
        [InlineKeyboardButton(text='Рассылка неактивным', callback_data='inactive_mailing')],
        [InlineKeyboardButton(text='Выход', callback_data='admin_exit')]
    ],
    resize_keyboard=True
)

referrals_status_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Изменить статус подписки', callback_data='change_subs_status')],
        [InlineKeyboardButton(text='Изменить канал для подписки (ru, eng)', callback_data='change_group_for_subs_ru_eng')],
        [InlineKeyboardButton(text='Изменить канал для подписки (остальные)', callback_data='change_group_for_subs_others')],
        [InlineKeyboardButton(text='Главное меню', callback_data='get_subscription_check_status')]
    ],
    resize_keyboard=True
)


class InactiveMailingData(StatesGroup):
    days = State()
    text = State()
    image = State()

@dp.message_handler(commands='admin', user_id=ADMINS)
async def admin(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer('Выбери пункт', reply_markup=admin_menu)


@dp.callback_query_handler(text="get_users_stat", user_id=ADMINS)
async def total_users_number_handler(callback: CallbackQuery):
    users_amount = await count_users()
    users_blocked = await count_users(blocked_users=True)
    users_lang_stat = await get_users_language_stat()
    final_text = f'Всего пользователей: {str(users_amount)}\n\nЗаблокированных: {str(users_blocked)}\n\n' + users_lang_stat
    await callback.answer()
    await callback.message.answer(final_text, parse_mode=types.ParseMode.MARKDOWN_V2)

    reply_message = await get_users_activity()
    await callback.answer()
    await callback.message.answer(reply_message)

    reply_message = await get_users_activity_by_functions()
    await callback.answer()
    await callback.message.answer(reply_message)

    reply_message = await get_new_users_by_weekdays()
    await callback.message.answer(reply_message, reply_markup=admin_menu, parse_mode=types.ParseMode.MARKDOWN_V2)


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
    for user_tg_id in users_tg_ids:
        try:
            await bot.send_message(user_tg_id, message['text'])
            messages_sent += 1
        except (BotKicked, BotBlocked, UserDeactivated):
            sql = 'UPDATE users SET blocked = true WHERE tg_id = $1'
            await db.pool.execute(sql, int(user_tg_id))
        except Exception as e:
            print(user_tg_id)
            print(e)
        await sleep(0.1)
    await message.answer(
        f'Рассылка завершена. Успешно отправлено <b>{str(messages_sent)}</b> сообщений из <b>{str(len(users_tg_ids))}</b>',
        parse_mode=types.ParseMode.HTML)



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
    ), parse_mode=types.ParseMode.HTML)


@dp.callback_query_handler(text="inactive_mailing_content")
async def invite_links(callback: CallbackQuery):
    invite_links = await get_setup_data()

    text_for_message = '\n\n<b>Текст и изображения для рассылки неактивным пользователям</b>'

    await callback.message.answer(text_for_message, parse_mode=types.ParseMode.HTML)

    for day in [['three', 3], ['seven', 7], ['onefive', 15]]:
        await callback.message.answer(f'<b>День {str(day[1])}</b>', parse_mode=types.ParseMode.HTML)
        try:
            text = invite_links[f'{day[0]}_days_inactive_mailing_text']
            if text:
                await callback.message.answer(text)
        except MessageTextIsEmpty:
            pass
        # try:
        #     photo = open(f'utils/images_for_mailing/{str(day[1])}.jpg', "rb")
        # except FileNotFoundError:
        #     continue
        try:
            if invite_links[f'{day[0]}_days_inactive_mailing_image']:
                await bot.send_photo(callback.message.chat.id, invite_links[f'{day[0]}_days_inactive_mailing_image'])
        except:
            root_logger.error(exc_info=True)

    await callback.message.answer('Выбери пункт', reply_markup=InlineKeyboardMarkup(
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
    await callback.message.answer(inactive_mailing_status, reply_markup=admin_menu, parse_mode=types.ParseMode.HTML)


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
        await update_inactive_mailing_image(str(days), None)
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
        try:
            file_id = message['document']['file_id']
        except TypeError:
            file_id = message['photo'][-1]['file_id']
        await update_inactive_mailing_image(str(days), file_id)
        # await bot.download_file(file.file_path, f'utils/images_for_mailing/{str(days)}.jpg')
        await state.finish()
        await message.answer('Сообщение для рассылки обновлено', reply_markup=admin_menu)



@dp.callback_query_handler(text="get_subscription_check_status", user_id=ADMINS)
async def get_subscription_check_status(callback: CallbackQuery):
    reply_message = f'Проверка подписки: {"Включена" if config.subscription_check else "Выключена"}.' \
                    f'\nКанал для подписки ru/eng:\n@{config.chanel_for_subs_ru_eng}' \
                    f'\nКанал для подписки остальные:\n@{config.chanel_for_subs_others}'
    await callback.message.answer(reply_message, reply_markup=referrals_status_menu)


@dp.callback_query_handler(text="change_subs_status", user_id=ADMINS)
async def change_ref_status_handler(callback: CallbackQuery):
    config.subscription_check = not config.subscription_check
    await toggle_subscription_check_status()
    reply_message = f'Статус подписки изменен на {"Включен" if config.subscription_check else "Выключен"}'
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