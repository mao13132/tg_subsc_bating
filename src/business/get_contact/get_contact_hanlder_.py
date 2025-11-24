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

from src.business.text_manager.text_manager import text_manager
from src.telegram.sendler.sendler import Sendler_msg


async def get_contact_handler(message: Message, state: FSMContext):
    await Sendler_msg.log_client_message(message)

    await state.finish()

    _msg = await text_manager.get_message('contact')

    await Sendler_msg.send_msg_message(message, _msg, None)

    try:
        await message.delete()
    except:
        pass

    return True
