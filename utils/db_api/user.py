from asyncpg import UniqueViolationError

from loader import db


async def create_user(message):
    user_id = message.from_user['id']
    first_name = message.from_user['first_name']
    last_name = message.from_user['last_name']
    language_code = message.from_user['language_code']
    sql = 'INSERT INTO users(tg_id,last_message,first_name,last_name,language_code,start_referal_link) VALUES ($1,$2,$3,$4,$5,$6)'
    try:
        await db.pool.execute(sql, int(user_id), '', first_name, last_name, language_code, None)
        # invite_link_parameter = message.get_args()
        # if invite_link_parameter:
        #     await db.pool.execute(sql, int(user_id), '', None, '', first_name, last_name,
        #                           language_code, invite_link_parameter)
        #     invite_link = f'https://t.me/instaROCKbot?start={invite_link_parameter}'
        #     await db.pool.execute(
        #         "UPDATE invite_links set registered_users_number = registered_users_number + 1 WHERE invite_link = $1",
        #         invite_link)
        # else:
        #     await db.pool.execute(sql, int(user_id), '', None, '', first_name, last_name,
        #                           language_code, None)
    except UniqueViolationError:
        sql = 'UPDATE users SET first_name = $1, last_name =$2, language_code = $3, blocked = false WHERE tg_id = $4'
        await db.pool.execute(sql, first_name, last_name, language_code, int(user_id))
