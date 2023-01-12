from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

admin_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Статистика по пользователям', callback_data='get_total_users_stat')],
        [InlineKeyboardButton(text='Активность пользователей', callback_data='get_user_activity')],
        [InlineKeyboardButton(text='Активность пользователей по функциям', callback_data='get_user_activity_by_functions')],
        [InlineKeyboardButton(text='Новые пользователи за неделю по дням', callback_data='get_new_users_by_weekdays')],
        [InlineKeyboardButton(text='Создать рассылку', callback_data='create_mailing')],
        [InlineKeyboardButton(text='Рефералы', callback_data='get_admin_referals_status')],
        [InlineKeyboardButton(text='Ссылки для приглашений', callback_data='invite_links')],
        [InlineKeyboardButton(text='Рассылка неактивным', callback_data='inactive_mailing')],
        [InlineKeyboardButton(text='Сторис шпион', callback_data='admin_stories_spy')],
        [InlineKeyboardButton(text='Топ 5 скачанных постов', callback_data='top_five_posts')],
        [InlineKeyboardButton(text='Главное меню', callback_data='main_menu')]
    ],
    resize_keyboard=True
)

referrals_status_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Изменить статус рефералов', callback_data='change_ref_status')],
        [InlineKeyboardButton(text='Изменить канал для подписки (ru, eng)', callback_data='change_group_for_subs_ru_eng')],
        [InlineKeyboardButton(text='Изменить канал для подписки (остальные)', callback_data='change_group_for_subs_others')],
        [InlineKeyboardButton(text='Главное меню', callback_data='main_menu')]
    ],
    resize_keyboard=True
)
