from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from aiogram import Dispatcher

from settings import ADMIN
from src.business.get_contact.get_contact_hanlder_ import get_contact_handler
from src.business.get_forecast.get_forecast_handler_ import get_forecast_handler
from src.business.managers.check_manager import check_manager
from src.business.managers.delete_managers import delete_managers
from src.business.start_one.start_one import start_one
from src.telegram.sendler.sendler import Sendler_msg


async def start(message: Message, state: FSMContext):
    if message.chat.type != 'private':
        return False
        
    await state.finish()

    if '/start' in str(message.text):
        skip_btn_menu = False
    else:
        skip_btn_menu = True

    result = await start_one(message, state, skip_btn_menu=skip_btn_menu)

    return result


def register_user(dp: Dispatcher):
    dp.register_message_handler(start, text_contains='/start', state='*')

    dp.register_message_handler(delete_managers, text_contains='/dels_')

    dp.register_message_handler(get_forecast_handler, text_contains='ПОЛУЧИТЬ ПРОГНОЗ')

    dp.register_message_handler(get_contact_handler, text_contains='Задать вопрос')

    dp.register_message_handler(start, text_contains='')
