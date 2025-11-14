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

from settings import LOGO
from src.business.delete_old_msg.delete_old_msg_ import delete_old_msg
from src.business.logo.change_logo_keyboard import ChangeLogoKeyboard
from src.telegram.sendler.sendler import Sendler_msg
from src.telegram.bot_core import BotDB


async def change_logo_state(message: Message, state: FSMContext):
    await Sendler_msg.log_client_message(message)

    keyboard = ChangeLogoKeyboard().back_admin()

    if message.content_type != 'photo':
        error_ = '❌ Вы прислали не изображение. Пожалуйста пришлите изображение'
        await Sendler_msg.send_msg_message(message, error_, None)
        return False

    try:
        file_id = message.photo[-1].file_id
    except Exception:
        await Sendler_msg.send_msg_message(message, '❌ Не удалось получить изображение', keyboard)
        return False

    state_data = await state.get_data()

    old_msg_id = state_data.get('old_msg_id')

    id_user = message.chat.id

    saved = await BotDB.update_settings(key='logo_file_id', value=str(file_id))

    status_text = '✅ Логотип обновлён' if saved else '❌ Ошибка сохранения логотипа'

    await state.finish()

    await Sendler_msg().sendler_photo_message(message, LOGO, status_text, keyboard)

    await delete_old_msg(message, message.chat.id, old_msg_id)

    return True
