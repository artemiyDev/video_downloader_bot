from asyncpg.exceptions import UniqueViolationError
from data.config import test
from loader import db

async def write_tiktok_to_db(tiktok_url, file_id):
    if test:
        return
    sql = 'INSERT INTO used_tiktoks (tiktok_url,tg_file_id) VALUES ($1,$2)'
    try:
        await db.pool.execute(sql, tiktok_url, file_id)
    except UniqueViolationError:
        pass


async def get_used_tiktok_from_db(tiktok_url):
    sql = "SELECT * FROM used_tiktoks where tiktok_url = $1;"
    result = await db.pool.fetchrow(sql, tiktok_url)
    if result:
        await db.pool.execute(
            "UPDATE used_tiktoks set download_times_counter = download_times_counter + 1 where tiktok_url = $1;",
            tiktok_url)
    return result
