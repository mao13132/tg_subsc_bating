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
from src.telegram.bot_core import BotDB


async def send_forecast_call(call: types.CallbackQuery, state: FSMContext):
    await Sendler_msg.log_client_call(call)

    users = await BotDB.get_users_need_paid_false() or []
    count = len(users)

    _msg = f'⚠️ Подтвердите рассылку прогноза пользователям?\n\nВсего без задолженности: <b>{count}</b>'

    keyboard = Admin_keyb().approve_send_forecast()

    await Sendler_msg.send_msg_call(call, _msg, keyboard)

    return True
