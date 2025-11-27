import os

from aiogram.dispatcher.filters.state import StatesGroup, State
from dotenv import load_dotenv
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class States(StatesGroup):
    add_manager = State()

    add_admin_chat = State()

    write_summa = State()

    get_summa_forecast = State()

    get_timer_bet = State()

    get_summa_offer = State()

    confirm_repeat_offers = State()

    get_summa_motivation = State()


class EditTextState(StatesGroup):
    waiting_new_text = State()


project_path = os.path.dirname(__file__)

dotenv_path = os.path.join(os.path.dirname(__file__), 'src', '.env')

load_dotenv(dotenv_path)

DEVELOPER = 1422194909

ADMIN = ['1422194909', '322281327']

TOKEN = os.getenv('TOKEN')

SHOPKEY = os.getenv('SHOPKEY')

SECKEY = os.getenv('SECKEY')

DOMAIN_PAYMENT = os.getenv('DOMAIN_PAYMENT')

SERVCODE = os.getenv('SERVCODE')

SQL_URL = os.getenv('SQL_URL')

LOGO = r'src/telegram/media/logo.jpg'

LOGGER = True

MOKE_SCHEDULE = True

MOKE_SCHEDULE_PAYMENTS_TASK = True

SEND_SUCCESS_PAYMENTS = False

CHECK_PAYMENT_EVERY = 30

SETTINGS_CHATS = {
    'analytic_chat': {
        'name': 'Чат проверка на подписку'
    },
}
