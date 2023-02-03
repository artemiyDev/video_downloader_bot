from loader import db



async def get_group_for_subs_from_db(group_type):
    sql = 'SELECT * FROM setup_data'
    return (await db.pool.fetchrow(sql))[group_type]

async def get_setup_data():
    sql = 'SELECT * FROM setup_data WHERE id = 1'
    return await db.pool.fetchrow(sql)