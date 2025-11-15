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

from settings import States, LOGO
from src.telegram.keyboard.keyboards import Admin_keyb
from src.telegram.sendler.sendler import Sendler_msg


async def send_payments_call(call: types.CallbackQuery, state: FSMContext):
    await Sendler_msg.log_client_call(call)

    await state.finish()

    _msg = f'♻️ Введите сумму к оплате'

    keyboard = Admin_keyb().back_bets_menu()

    await Sendler_msg().sendler_photo_call(call, LOGO, _msg, keyboard)

    await States.write_summa.set()

    return True
