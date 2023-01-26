from asyncpg.exceptions import UniqueViolationError
from data.config import test
from loader import db

async def write_youtube_to_db(youtube_url, file_id):
    if test:
        return
    sql = 'INSERT INTO used_youtubes (youtube_url,tg_file_id) VALUES ($1,$2)'
    try:
        await db.pool.execute(sql, youtube_url, file_id)
    except UniqueViolationError:
        pass


async def get_used_youtube_from_db(youtube_url):
    sql = "SELECT * FROM used_youtubes where youtube_url = $1;"
    result = await db.pool.fetchrow(sql, youtube_url)
    if result:
        await db.pool.execute(
            "UPDATE used_youtubes set download_times_counter = download_times_counter + 1 where youtube_url = $1;",
            youtube_url)
    return result
