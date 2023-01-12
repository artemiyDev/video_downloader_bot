from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware

from loader import db


class UpdateUserInfo(BaseMiddleware):
    async def on_process_update(self, update: types.Update,data):
        try:
            if update['my_chat_member']['new_chat_member']['status'] == 'kicked':
                user_tg_id =update['my_chat_member']['chat']['id']
                sql = 'UPDATE users SET blocked = true WHERE tg_id = $1'
                await db.pool.execute(sql, int(user_tg_id))
        except:
            pass
