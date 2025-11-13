# ---------------------------------------------
# Program by @developer_telegrams
#
#
# Version   Date        Info
# 1.0       2023    Initial Version
#
# ---------------------------------------------
import json

from aiogram import types
from aiogram.dispatcher import FSMContext

from settings import LOGO
from src.business.devision_msg.devision_msg import division_message
from src.business.managers.get_managers_ import get_managers
from src.business.managers.keyboard_managers import ManagersKeyboard
from src.telegram.sendler.sendler import Sendler_msg


async def managers_call(call: types.CallbackQuery, state: FSMContext):
    await Sendler_msg.log_client_call(call)

    await state.finish()

    id_user = call.message.chat.id

    keyb = ManagersKeyboard.managers()

    managers = await get_managers()

    if not managers:
        _msg = '⛔️ Список менеджеров пуст'

        await Sendler_msg.send_msg_call(call, _msg, keyb)

        return False

    _msg = '<b>Список менеджеров:</b>\n\n'

    _msg += f'\n'.join(f'{count + 1}. {manager["login"]} - Удалить '
                       f'/dels_{manager["id"]}' for count, manager in enumerate(managers))

    if len(_msg) < 1024:
        await Sendler_msg().sendler_photo_call(call, LOGO, _msg, keyb)
    else:
        await division_message(call.message, _msg, keyb)

    return True
