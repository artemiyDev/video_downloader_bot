from loader import db



async def increase_stat(column):
    if column == 'text_count':
        if await db.pool.execute("UPDATE stat set text_count = text_count + 1 WHERE date = CURRENT_DATE") == 'UPDATE 0':
            try:
                await db.pool.execute("INSERT into stat DEFAULT VALUES")
            except:
                pass
            await increase_stat('text_count')
    if column == 'hashtags_count':
        if await db.pool.execute(
                "UPDATE stat set hashtags_count = hashtags_count + 1 WHERE date = CURRENT_DATE") == 'UPDATE 0':
            try:
                await db.pool.execute("INSERT into stat DEFAULT VALUES")
            except:
                pass
            await increase_stat('hashtags_count')
    if column == 'download_count':
        if await db.pool.execute(
                "UPDATE stat set download_count = download_count + 1 WHERE date = CURRENT_DATE") == 'UPDATE 0':
            try:
                await db.pool.execute("INSERT into stat DEFAULT VALUES")
            except:
                pass
            await increase_stat('download_count')
    if column == 'pinterest':
        if await db.pool.execute(
                "UPDATE stat set pinterest = pinterest + 1 WHERE date = CURRENT_DATE") == 'UPDATE 0':
            try:
                await db.pool.execute("INSERT into stat DEFAULT VALUES")
            except:
                pass
            await increase_stat('pinterest')