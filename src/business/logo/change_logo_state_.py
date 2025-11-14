# ---------------------------------------------
# Program by @developer_telegrams
#
#
# Version   Date        Info
# 1.0       2023    Initial Version
#
# ---------------------------------------------
from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from src.business.logo.change_logo_keyboard import ChangeLogoKeyboard
from src.telegram.sendler.sendler import Sendler_msg


async def change_logo_state(message: Message, state: FSMContext):
    await Sendler_msg.log_client_message(message)

    keyboard = ChangeLogoKeyboard().back_admin()

    if message.content_type != 'photo':
        error_ = '❌ Вы прислали не изображение. Пожалуйста пришлите изображение'
        await Sendler_msg.send_msg_message(message, error_, None)
        return False

