from datetime import datetime, timedelta

from loader import db
from tabulate import tabulate
from langcodes import Language


async def increase_stat(column):
    if column == 'instagram':
        sql = "UPDATE stat set instagram = instagram + 1 WHERE date = CURRENT_DATE"
    elif column == 'pinterest':
        sql = "UPDATE stat set pinterest = pinterest + 1 WHERE date = CURRENT_DATE"
    elif column == 'tiktok':
        sql = "UPDATE stat set tiktok = tiktok + 1 WHERE date = CURRENT_DATE"
    elif column == 'youtube':
        sql = "UPDATE stat set youtube = youtube + 1 WHERE date = CURRENT_DATE"

    if await db.pool.execute(sql, column) == 'UPDATE 0':
        try:
            await db.pool.execute("INSERT into stat DEFAULT VALUES")
        except:
            pass
        await increase_stat(column)

async def update_subscriber(tg_id):
    sql = 'UPDATE users SET subscribed_to_channel = true WHERE tg_id = $1'
    await db.pool.execute(sql, int(tg_id))

async def update_last_message_and_last_action_timestamp(tg_id, message):
    sql = 'UPDATE users SET last_message = $1, last_action_timestamp=now(),subscribed_to_channel = true WHERE tg_id = $2'
    await db.pool.execute(sql, message, int(tg_id))

    sql = 'UPDATE users SET subscribed_to_channel = true WHERE tg_id = $1'
    await db.pool.execute(sql, int(tg_id))


async def count_users(blocked_users=False):
    if blocked_users:
        return await db.pool.fetchval("SELECT COUNT(*) FROM users where blocked = true")
    else:
        return await db.pool.fetchval("SELECT COUNT(*) FROM users")


async def get_users_language_stat():
    sql = "SELECT language_code, COUNT(*) FROM users WHERE language_code IS NOT NULL GROUP BY language_code ORDER BY " \
          "COUNT(*) DESC LIMIT 10; "
    result = await db.pool.fetch(sql)
    data_to_table = [[Language.make(language=x['language_code']).display_name(), x['count']] for x in result]
    table_data = tabulate(data_to_table, headers=["Язык", "Пользователей"], tablefmt="github")
    result_string = f"""Топ 10 языков пользователей\n```
{table_data}```"""
    return result_string


async def get_users_activity_by_functions():
    one_week_result = [0, 0, 0, 0]
    one_month_result = [0, 0, 0, 0]
    one_day = \
        await db.pool.fetch("SELECT * FROM stat where date = CURRENT_DATE;")
    one_day_result = [one_day[0]['instagram'], one_day[0]['pinterest'], one_day[0]['tiktok'],
                      one_day[0]['youtube']]
    one_week = \
        await db.pool.fetch(
            "SELECT *  FROM stat where date <= CURRENT_DATE AND date > CURRENT_DATE - INTERVAL '7 DAYS';")
    for row in one_week:
        one_week_result[0] += row['instagram']
        one_week_result[1] += row['pinterest']
        one_week_result[2] += row['tiktok']
        one_week_result[3] += row['youtube']
    one_month = \
        await db.pool.fetch(
            "SELECT *  FROM stat where date <= CURRENT_DATE AND date > CURRENT_DATE - INTERVAL '1 MONTH';")
    for row in one_month:
        one_month_result[0] += row['instagram']
        one_month_result[1] += row['pinterest']
        one_month_result[2] += row['tiktok']
        one_month_result[3] += row['youtube']

    return '\n'.join([
        f'За сегодня:\nInstagram: {str(one_day_result[0])}\nPinterest: {str(one_day_result[1])}\nTiktok: {str(one_day_result[2])}\nYoutube: {str(one_day_result[3])}\n',
        f'За неделю:\nInstagram: {str(one_week_result[0])}\nPinterest: {str(one_week_result[1])}\nTiktok: {str(one_week_result[2])}\nYoutube: {str(one_week_result[3])}\n',
        f'За месяц: \nInstagram: {str(one_month_result[0])}\nPinterest: {str(one_month_result[1])}\nTiktok: {str(one_month_result[2])}\nYoutube: {str(one_month_result[3])}\n'])


async def get_users_activity():
    more_than_one_week = \
        await db.pool.fetchval("SELECT count(*) FROM users where DATE(last_action_timestamp) = CURRENT_DATE")
    more_than_two_weeks = \
        await db.pool.fetchval(
            "SELECT count(*)  FROM users where DATE(last_action_timestamp)<= CURRENT_DATE AND DATE(last_action_timestamp) > CURRENT_DATE - INTERVAL '7 DAYS';")
    more_than_one_month = \
        await db.pool.fetchval(
            "SELECT count(*)  FROM users where DATE(last_action_timestamp) <= CURRENT_DATE AND DATE(last_action_timestamp) > CURRENT_DATE - INTERVAL '1 MONTH';")
    return '\n'.join([f'Активных пользователей за сегодня: \n{str(more_than_one_week)}',
                      f'Активных пользователей за неделю: \n{str(more_than_two_weeks)}',
                      f'Активных пользователей за месяц: \n{str(more_than_one_month)}'])


async def get_new_users_by_weekdays():
    activity_by_days = []
    for i in range(0, 7):
        sql = "SELECT count(*)  FROM users where DATE(start_date_timestamp) = $1;"
        sql2 = "SELECT count(*)  FROM users where DATE(start_date_timestamp) = $1 and last_action_timestamp is not null;"
        sql3 = "SELECT count(*)  FROM users where DATE(start_date_timestamp) = $1 and blocked = true;"
        date = datetime.now() - timedelta(days=i)
        activity_by_days.append([await db.pool.fetchval(sql, date),
                                 await db.pool.fetchval(sql2, date),
                                 await db.pool.fetchval(sql3, date),
                                 date.strftime('%d.%m')])
    activity_by_days = [[x[3], x[0], x[1], x[2]] for x in activity_by_days]
    table_data = tabulate(activity_by_days, headers=["Дата", "Нов", "Акт", "Блок"],
                          tablefmt="github", maxheadercolwidths=[4, 3, 3, 4], maxcolwidths=[5, 5, 5, 5])

    result_string = f"""Статистика за последние 7 дней\n```
{table_data}```"""

    return result_string
