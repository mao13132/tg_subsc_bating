# ---------------------------------------------
# Program by @developer_telegrams
#
#
# Version   Date        Info
# 1.0       2023    Initial Version
#
# ---------------------------------------------
from src.business.posts_manager.message_content_codec import send_records_grouped


async def send_forecast(settings):
    message = settings['message']

    messages = settings['messages']

    await send_records_grouped(message.bot, message.chat.id, messages)

    return True
