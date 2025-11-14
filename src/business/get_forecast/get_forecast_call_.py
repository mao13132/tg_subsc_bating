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

from src.telegram.sendler.sendler import Sendler_msg


async def get_forecast_call(call: types.CallbackQuery, state: FSMContext):
    await Sendler_msg.log_client_call(call)

    await state.finish()
