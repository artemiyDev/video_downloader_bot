from aiogram import executor

from download_services.instagram import get_proxy
from loader import db
import middlewares, filters
from utils.db_api.setup import get_setup_data, get_group_for_subs_from_db

from utils.notify_admins import on_startup_notify
from data import config


async def on_startup(dp):
    await db.create()
    get_proxy()
    filters.setup(dp)
    middlewares.setup(dp)

    setup_data = await get_setup_data()
    config.subscription_check = setup_data['subscription_check']
    config.chanel_for_subs_ru_eng = setup_data['group_for_subc_ru_eng']
    config.chanel_for_subs_others = setup_data['group_for_subc_others']
    print(f'Refferals enabled: {config.referrals_enabled}')
    print(f'Channel for subs ru/eng: {config.chanel_for_subs_ru_eng}')
    print(f'Channel for subs others: {config.chanel_for_subs_others}')

    # aiosched.add_job(mail_to_inactive_users, 'interval', hours=1)
    # aiosched.start()
    await on_startup_notify(dp)


if __name__ == '__main__':
    from handlers import dp

    executor.start_polling(dp, on_startup=on_startup)
