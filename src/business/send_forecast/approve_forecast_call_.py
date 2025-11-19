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
from src.business.send_forecast._send_forecast import send_forecast_broadcast
from src.telegram.keyboard.keyboards import Admin_keyb
from src.telegram.sendler.sendler import Sendler_msg
from src.telegram.bot_core import BotDB


async def approve_forecast_call(call: types.CallbackQuery, state: FSMContext):
    await Sendler_msg.log_client_call(call)

    keyboard = Admin_keyb().back_bets_menu()

    await state.finish()

    forecast_message = await BotDB.user_messages.read_by_filter({})

    if not forecast_message:
        keyboard = Admin_keyb().new_back_bets_menu()

        no_load = f'❌ Прогноз не загружен'
        await Sendler_msg().sendler_photo_call(call, LOGO, no_load, keyboard)
        return True

    res_send = await send_forecast_broadcast({"message": call.message, "messages": forecast_message})

    _msg = f'✅ Рассылка выполнена\nПользователей: {res_send["sent"]}\n' \
           f'Успешных доставок:{res_send["total"]}\nОшибки: {res_send["failed"]}'

    await Sendler_msg().sendler_photo_message(call.message, LOGO, _msg, keyboard)

    return True
