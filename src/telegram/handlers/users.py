from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from aiogram import Dispatcher

from settings import ADMIN
from src.business.managers.check_manager import check_manager
from src.business.managers.delete_managers import delete_managers
from src.business.start_one.start_one import start_one
from src.telegram.sendler.sendler import Sendler_msg


async def start(message: Message, state: FSMContext):
    if message.chat.type != 'private':
        return False
        
    await state.finish()

    id_user = message.chat.id

    is_manager = await check_manager(message)

    # if str(id_user) not in ADMIN and not is_manager:
    #     await Sendler_msg.send_msg_message(message, '⛔️ В доступе отказано', None)
    # 
    #     return False

    result = await start_one(message, state)

    return result


def register_user(dp: Dispatcher):
    dp.register_message_handler(start, text_contains='/start', state='*')

    dp.register_message_handler(delete_managers, text_contains='/dels_')

    dp.register_message_handler(start, text_contains='')
