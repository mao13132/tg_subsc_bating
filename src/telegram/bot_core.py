import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from settings import TOKEN

from src.sql.connector import BotDB

bot = Bot(token=TOKEN, parse_mode='HTML')

logger = logging.getLogger()

logging.basicConfig(handlers=[logging.FileHandler(filename="./logs.txt",
                                                  encoding='utf-8', mode='a+')],
                    format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
                    datefmt="%F %A %T",
                    level=logging.ERROR)


class Core:
    def __init__(self):
        storage = MemoryStorage()

        dp = Dispatcher(bot, storage=storage)

        self.bot = bot

        self.storage = storage

        self.dp = dp

        self.BotDB = BotDB

        print(f'\nБот запущен\n')
