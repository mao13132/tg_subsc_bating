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

from settings import LOGO
from src.telegram.keyboard.keyboards import Admin_keyb
from src.telegram.sendler.sendler import Sendler_msg


async def bet_menu_call(call: types.CallbackQuery, state: FSMContext):
    await state.finish()

    _msg = f'Меню управления прогнозами'

    keyboard = Admin_keyb().bet_keyboard()

    await Sendler_msg.send_msg_call(call, _msg, keyboard)

    return True
