from aiogram import Bot, Dispatcher, types
from aiogram.bot.api import TelegramAPIServer
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from data import config
from utils.db_api.postgresql import Database
import telebot
import logging



logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
                        level=logging.INFO)

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)  # or whatever
handler = logging.FileHandler('bot.log', 'a', 'utf-8')  # or whatever
handler.setFormatter(
    logging.Formatter(u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s'))  # or whatever
root_logger.addHandler(handler)


telebot = telebot.TeleBot(config.BOT_TOKEN, )

bot = Bot(token=config.BOT_TOKEN, server=TelegramAPIServer.from_base('http://38.242.238.106:8081'))
# bot = Bot(token=config.BOT_TOKEN)
storage = MemoryStorage()

dp = Dispatcher(bot, storage=storage)
db = Database()

executors = {'default': AsyncIOExecutor()}
job_defaults = {"coalesce": False, "max_instances": 1, "misfire_grace_time": 3600}

aiosched = AsyncIOScheduler(executors=executors, job_defaults=job_defaults)
