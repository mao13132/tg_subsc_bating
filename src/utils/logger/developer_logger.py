# ---------------------------------------------
# Program by @developer_telegrams
#
#
# Version   Date        Info
# 1.0       2023    Initial Version
#
# ---------------------------------------------
import base64

from settings import DEVELOPER, LOGGER


async def developer_logger(message, id_user, msg_):
    if LOGGER and id_user != DEVELOPER:
        try:
            await message.bot.send_message(DEVELOPER, f"Пользователь '{id_user}' "
                                                      f"'{message.chat.full_name}' отправил голосовой запрос: '{msg_}'",
                                           disable_notification=True)
        except:
            pass


async def developer_img_logger(message, id_user, image_base64, caption_):
    if LOGGER and id_user != DEVELOPER:

        try:
            await message.bot.send_photo(DEVELOPER, photo=base64.b64decode(image_base64),
                                         caption=caption_[:1000])
        except:
            pass
