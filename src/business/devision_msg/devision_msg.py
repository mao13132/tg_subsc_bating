from src.telegram.sendler.sendler import Sendler_msg

from aiogram.types import Message


async def division_message(message: Message, response, keyb):
    if len(response) > 4096:
        for x in range(0, len(response), 4096):
            await Sendler_msg.send_msg_message(message, response[x:x + 4096], keyb)
    else:
        await Sendler_msg.send_msg_message(message, response, keyb)
