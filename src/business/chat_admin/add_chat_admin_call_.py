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

from settings import States, LOGO
from src.business.chat_admin.add_chat_keyboard import ChatAdminKeyb
from src.telegram.sendler.sendler import Sendler_msg
from src.utils.logger._logger import logger_msg


async def add_chat_admin_call(call: types.CallbackQuery, state: FSMContext):
    await state.finish()

    try:
        _, target = str(call.data).split('-')
    except:

        error = f'⚠️ Ошибка при разборе add_chat_admin_call'

        logger_msg(error)

        await Sendler_msg.send_msg_call(call, error, None)

        return False

    _msg = "♻️ Пришлите ID канала (например: -1001234567890):\n\n" \
           "💡 <b>Как получить ID чата:</b>\n" \
           "1. Нажмите что бы попасть в бота по определению ID 👉 <a href='https://t.me/username_to_id_bot?start=developer_telegrams'>@username_to_id_bot</a>\n" \
           "2. Отправьте команду /start\n" \
           "3. На клавиатуре нажмите Chat\n" \
           "4. Укажите свой чат\n" \
           "5. Бот покажет ID канала"

    keyboard = ChatAdminKeyb().back_add_chat()

    res_send = await Sendler_msg().sendler_photo_call(call, LOGO, _msg, keyboard)

    await States.add_admin_chat.set()

    await state.update_data(target=target, old_msg_id=res_send.message_id)

    return True
