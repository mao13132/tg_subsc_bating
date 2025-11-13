from aiogram import types
from aiogram.dispatcher import FSMContext

from src.telegram.bot_core import BotDB
from src.business.text_edit.edit_keyboard import Edit_keyb
from src.telegram.sendler.sendler import Sendler_msg
from settings import LOGO


async def text_msg_call(call: types.CallbackQuery, state: FSMContext):
    """Отображает список текстов сообщений для редактирования"""
    texts = await BotDB.texts.get_all_texts('messages')

    if not texts:
        await call.answer("Тексты сообщений не найдены")
        return

    await Sendler_msg.log_client_call(call)

    keyb = Edit_keyb().text_msg(texts)

    text = "💬 Редактирование текстов сообщений\n\nВыберите текст для редактирования:"

    await Sendler_msg().sendler_photo_call(call, LOGO, text, keyb)

    return True
