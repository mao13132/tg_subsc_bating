# ---------------------------------------------
# Program by @developer_telegrams
#
#
# Version   Date        Info
# 1.0       2023    Initial Version
#
# ---------------------------------------------
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

from settings import States
from src.telegram.keyboard.keyboards import Admin_keyb
from src.telegram.sendler.sendler import Sendler_msg


async def add_summa_bet_call(call: types.CallbackQuery, state: FSMContext):
    await Sendler_msg.log_client_call(call)

    id_user = call.message.chat.id

    _msg = (
        '♻️ Введите стоимость прогноза'
    )

    keyboard = Admin_keyb().back_bets_menu()

    res_send = await Sendler_msg.send_msg_call(call, _msg, keyboard)

    await States.get_summa_forecast.set()

    await state.update_data(old_msg_id=res_send.message_id)

    return True
