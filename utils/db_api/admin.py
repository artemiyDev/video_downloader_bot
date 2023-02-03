from loader import db


async def get_all_users_tg_ids(without_blocked_users=False):
    if without_blocked_users:
        sql = 'SELECT tg_id FROM users where blocked = false'
    else:
        sql = 'SELECT tg_id FROM users'
    rows = await db.pool.fetch(sql)
    return [x[0] for x in rows]



async def get_inactive_mailing_user_stat():
    stat_text = 'Статистика по рассылке:\n\n'
    for day in [3, 7, 15]:
        sql = "SELECT count(*)  FROM users where mailing_to_inactive_users_sent_days = $1;"
        sql2 = "SELECT count(*)  FROM users where mailing_to_inactive_users_sent_days = $1 and last_action_date is not null;"
        sql3 = "SELECT count(*)  FROM users where mailing_to_inactive_users_sent_days = $1 and blocked = true;"
        sql4 = "SELECT count(*)  FROM users where mailing_to_inactive_users_sent_days = $1 and subscribed_to_channel = true;"
        stat_text += f'День {str(day)}\n\nОтправлено: {await db.pool.fetchval(sql, day)}\nАктивных: ' \
                     f'{await db.pool.fetchval(sql2, day)}\nЗаблокировали: {await db.pool.fetchval(sql3, day)}\n' \
                     f'Подписались: {await db.pool.fetchval(sql4, day)}\n\n'
    stat_text = stat_text.strip()
    return stat_text

async def get_inactive_mailing_status():
    sql = 'SELECT * FROM setup_data'
    return (await db.pool.fetchrow(sql))['inactive_mailing_enabled']


async def toggle_inactive_mailing_status():
    sql = 'UPDATE setup_data SET inactive_mailing_enabled = NOT inactive_mailing_enabled WHERE id = 1'
    return await db.pool.execute(sql)


async def update_inactive_mailing_image(days, file_id):
    if days == '3':
        days = 'three'
    elif days == '7':
        days = 'seven'
    elif days == '15':
        days = 'onefive'

    sql = f'UPDATE setup_data SET {str(days)}_days_inactive_mailing_image =$1'
    return await db.pool.execute(sql, file_id)

async def update_invite_link(days, text):
    if days == '3':
        days = 'three'
    elif days == '7':
        days = 'seven'
    elif days == '15':
        days = 'onefive'

    sql = f'UPDATE setup_data SET {str(days)}_days_inactive_mailing_text =$1'
    return await db.pool.execute(sql, text)


async def toggle_subscription_check_status():
    sql = 'UPDATE setup_data SET subscription_check = NOT subscription_check WHERE id = 1'
    return await db.pool.execute(sql)


async def change_group_for_subs_in_db(group_type, new_group):
    sql = f'UPDATE setup_data SET {group_type} =$1 '
    return await db.pool.execute(sql, new_group)


async def get_group_for_subs_from_db(group_type):
    sql = 'SELECT * FROM setup_data'
    return (await db.pool.fetchrow(sql))[group_type]