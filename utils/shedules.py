from asyncio import sleep
from loader import db
from aiogram.utils.exceptions import BotBlocked, UserDeactivated, BotKicked, ChatNotFound
from loader import bot, root_logger
import functools
from utils.db_api.db_setup_functions import get_inactive_mailing_texts, get_inactive_mailing_status


def force_async(fn):
    '''
    turns a sync function to async function using threads
    '''
    from concurrent.futures import ThreadPoolExecutor
    import asyncio
    pool = ThreadPoolExecutor()

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        future = pool.submit(fn, *args, **kwargs)
        return asyncio.wrap_future(future)  # make it awaitable

    return wrapper


async def mail_to_inactive_users():
    if not await get_inactive_mailing_status():
        print('inactive_mailing_status False')
        return
    mailing_texts = await get_inactive_mailing_texts()
    # for date in [['three', 3], ['seven', 7], ['onefive', 15]]:
    for date in [['three', 3], ['seven', 7]]:
        sql = f"select * from users WHERE last_action_timestamp is null and blocked = false and start_date_timestamp < now() - interval '{str(date[1])} days'"
        rows = await db.pool.fetch(sql)
        for row in rows:
            tg_id = row['tg_id']
            mailing_to_inactive_users_sent_days = row['mailing_to_inactive_users_sent_days']
            if mailing_to_inactive_users_sent_days:
                if date[1] <= mailing_to_inactive_users_sent_days:
                    continue
            # print(row)
            try:
                try:
                    photo = open(f'utils/images_for_mailing/{str(date[1])}.jpg', "rb")
                    await bot.send_photo(tg_id, photo, caption=mailing_texts[f'{date[0]}_days_inactive_mailing_text'])
                except FileNotFoundError:
                    try:
                        await bot.send_message(tg_id, mailing_texts[f'{date[0]}_days_inactive_mailing_text'])
                    except (BotKicked, BotBlocked, UserDeactivated, ChatNotFound):
                        sql = "UPDATE users SET blocked = true WHERE tg_id = $1"
                        await db.pool.execute(sql, tg_id)
                sql = "UPDATE users SET mailing_to_inactive_users_sent_days = $1 WHERE tg_id = $2"
                await db.pool.execute(sql, date[1], tg_id)
            except (BotKicked, BotBlocked, UserDeactivated, ChatNotFound):
                sql = "UPDATE users SET blocked = true WHERE tg_id = $1"
                await db.pool.execute(sql, tg_id)
            except:
                root_logger.error('Schedule error', exc_info=True)
            await sleep(0.05)
