# ---------------------------------------------
# Program by @developer_telegrams
#
#
# Version   Date        Info
# 1.0       2023    Initial Version
#
# ---------------------------------------------
from aiogram import types
from aiogram.dispatcher import FSMContext

from settings import LOGO, States
from src.business.managers.keyboard_managers import ManagersKeyboard
from src.telegram.keyboard.keyboards import Admin_keyb
from src.telegram.sendler.sendler import Sendler_msg


async def add_managers_call(call: types.CallbackQuery, state: FSMContext):
    await Sendler_msg.log_client_call(call)

    await state.finish()

    id_user = call.message.chat.id

    _msg = f'Укажите телеграм ник или ID телеграмма менеджера'

    keyb = ManagersKeyboard.back_managers()

    await Sendler_msg.send_msg_call(call, _msg, keyb)

    await States.add_manager.set()

    return True
