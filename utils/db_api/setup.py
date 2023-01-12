from loader import db


async def get_refferals_status():
    sql = 'SELECT * FROM setup_data'
    return (await db.pool.fetchrow(sql))['referrals_enabled']


async def get_group_for_subs_from_db(group_type):
    sql = 'SELECT * FROM setup_data'
    return (await db.pool.fetchrow(sql))[group_type]
