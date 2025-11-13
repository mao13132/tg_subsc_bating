# ---------------------------------------------
# Program by @developer_telegrams
#
#
# Version   Date        Info
# 1.0       2023    Initial Version
#
# ---------------------------------------------
from aiogram.types import Message

from settings import ADMIN_CHANEL


async def no_command(message: Message):
    print()

    await message.send_copy(ADMIN_CHANEL, message.message_thread_id)

    # await message.forward(ADMIN_CHANEL, message.message_thread_id)
