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
from src.business.get_forecast.send_forecast_ import send_forecast
from src.telegram.keyboard.keyboards import Admin_keyb
from src.telegram.sendler.sendler import Sendler_msg

from src.telegram.bot_core import BotDB


async def send_me_bet_call(call: types.CallbackQuery, state: FSMContext):
    await Sendler_msg.log_client_call(call)

    await state.finish()

    keyboard = Admin_keyb().back_bets_menu()

    forecast_message = await BotDB.user_messages.read_by_filter({})

    if not forecast_message:
        no_load = f'❌ Прогноз не загружен'

        await Sendler_msg().sendler_photo_call(call, LOGO, no_load, keyboard)

        return True

    res_send = await send_forecast({'message': call.message, "messages": forecast_message})

    keyboard = Admin_keyb().bet_keyboard()

    _msg = f'Меню управления прогнозами'

    await Sendler_msg().new_sendler_photo_call(call, LOGO, _msg, keyboard)

    return True

