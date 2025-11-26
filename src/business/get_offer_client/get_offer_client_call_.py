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

from src.business.text_manager.text_manager import text_manager
from src.telegram.bot_core import BotDB
from src.telegram.keyboard.keyboards import Admin_keyb
from src.telegram.sendler.sendler import Sendler_msg


async def get_offer_client_call(call: types.CallbackQuery, state: FSMContext):
    id_user = call.message.chat.id

    data_user = await BotDB.get_user_bu_id_user(id_user)

    await BotDB.edit_user('get_offer', True, id_user)

    _msg = await text_manager.get_message('get_offer')

    await call.answer(_msg, show_alert=True)

    await Sendler_msg.log_client_call(call)

    back = await text_manager.get_button_text('back')

    try:
        await call.message.edit_reply_markup(Admin_keyb().actual_motivation(back, '', user_get_offer=True))
    except:
        pass

    return True
