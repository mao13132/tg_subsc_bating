# ---------------------------------------------
# Program by @developer_telegrams
#
#
# Version   Date        Info
# 1.0       2023    Initial Version
#
# ---------------------------------------------
from settings import LOGO, START_MESSAGE, ADMIN
from src.business.get_data_user.get_data_user import get_data_user
from src.business.managers.check_manager import check_manager
from src.telegram.keyboard.keyboards import Admin_keyb

from src.telegram.sendler.sendler import Sendler_msg

from aiogram.types import Message, ChatActions

from src.telegram.bot_core import BotDB

from aiogram.dispatcher import FSMContext


async def start_one(message: Message, state: FSMContext):
    await state.finish()

    try:
        await message.bot.send_chat_action(message.chat.id, ChatActions.TYPING)
    except:
        pass

    id_user = message.chat.id

    access_admin = False

    is_manager = await check_manager(message)

    if str(id_user) in ADMIN or is_manager:
        access_admin = True

    data_user = await get_data_user(message)

    new_user = await BotDB.check_or_add_user(id_user, data_user)

    await Sendler_msg.log_client_message(message)

    keyb = Admin_keyb().start_keyb(access_admin)

    await Sendler_msg().sendler_photo_message(message, LOGO, START_MESSAGE, keyb)

    return True
