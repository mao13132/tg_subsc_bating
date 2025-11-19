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
from src.business.logo.change_logo_keyboard import ChangeLogoKeyboard
from src.business.logo.logo_states import EditLogoStates
from src.telegram.sendler.sendler import Sendler_msg


async def logo_change_call(call: types.CallbackQuery, state: FSMContext):
    await state.finish()

    _msg = "♻️ Пришлите следующим сообщением изображение, которое хотите установить как логотип в боте"

    keyboard = ChangeLogoKeyboard().back_admin()

    res_send = await Sendler_msg.send_msg_call(call, _msg, keyboard)

    await EditLogoStates.chane_logo.set()

    await state.update_data(old_msg_id=res_send.message_id)

    return True
