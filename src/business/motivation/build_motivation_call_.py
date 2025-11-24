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
from src.telegram.sendler.sendler import Sendler_msg
from src.telegram.keyboard.keyboards import Admin_keyb


async def build_motivation_call(call: types.CallbackQuery, state: FSMContext):
    await Sendler_msg.log_client_call(call)

    await state.finish()

    _msg = f'Введите сумму для рассылки предложений'

    keyboard = Admin_keyb().back_bets_menu()

    res_send = await Sendler_msg().sendler_photo_call(call, LOGO, _msg, keyboard)

    await States.get_summa_motivation.set()

    await state.update_data(old_msg_id=res_send.message_id)

    return True
