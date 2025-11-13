import os

from aiogram.dispatcher.filters.state import StatesGroup, State
from dotenv import load_dotenv
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class States(StatesGroup):
    add_manager = State()


class EditTextState(StatesGroup):
    waiting_new_text = State()


project_path = os.path.dirname(__file__)

dotenv_path = os.path.join(os.path.dirname(__file__), 'src', '.env')

load_dotenv(dotenv_path)

DEVELOPER = 1422194909

ADMIN = ['1422194909']

TOKEN = os.getenv('TOKEN')

SQL_URL = os.getenv('SQL_URL')

START_MESSAGE = 'Меню бота'

LOGO = r'src/telegram/media/logo.jpg'

LOGGER = True
