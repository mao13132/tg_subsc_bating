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

from settings import LOGO, SETTINGS_CHATS
from src.business.chat_admin.add_chat_keyboard import ChatAdminKeyb
from src.telegram.sendler.sendler import Sendler_msg


async def chat_admin_call(call: types.CallbackQuery, state: FSMContext):
    await state.finish()

    keyboard = ChatAdminKeyb().chat_admin_btns(SETTINGS_CHATS)

    _msg = f'Выберите пункт для изменения'

    await Sendler_msg().sendler_photo_call(call, LOGO, _msg, keyboard)

    return True
