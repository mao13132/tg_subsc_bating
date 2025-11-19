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


async def clear_bet_call(call: types.CallbackQuery, state: FSMContext):
    await state.finish()

    res_clear = await BotDB.user_messages.delete_by_filter({})

    keyboard = Admin_keyb().bet_keyboard()

    _msg = f'✅ Успешно очистил загруженный прогноз'

    await Sendler_msg.send_msg_call(call, _msg, keyboard)

    return True

