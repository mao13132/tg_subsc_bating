from aiogram import types
from aiogram.dispatcher import FSMContext

from settings import LOGO, EditTextState
from src.telegram.bot_core import BotDB
from src.business.text_edit.edit_keyboard import Edit_keyb
from src.telegram.sendler.sendler import Sendler_msg


async def edit_text_button_call(call: types.CallbackQuery, state: FSMContext):
    """Начинает редактирование текста кнопки"""
    await Sendler_msg.log_client_call(call)

    text_key = call.data.split('-', 1)[1]

    # Получаем текущий текст напрямую через CRUD
    current_text = await BotDB.texts.get_text_by_key('buttons', text_key)

    if not current_text:
        await call.answer("Текст не найден")
        return

    await state.set_state(EditTextState.waiting_new_text)
    await state.update_data(text_type='buttons', text_key=text_key)

    keyb = Edit_keyb().edit_text_back('buttons')

    text = f"📝 Редактирование текста кнопки\n\n" \
           f"Ключ: `{text_key}`\n" \
           f"Текущий текст: {current_text}\n\n" \
           f"Отправьте новый текст:"

    await Sendler_msg().sendler_photo_call(call, LOGO, text, keyb)


async def edit_text_message_call(call: types.CallbackQuery, state: FSMContext):
    """Начинает редактирование текста сообщения"""
    await Sendler_msg.log_client_call(call)

    text_key = call.data.split('-', 1)[1]

    # Получаем текущий текст напрямую через CRUD
    current_text = await BotDB.texts.get_text_by_key('messages', text_key)

    if not current_text:
        await call.answer("Текст не найден")
        return

    await state.set_state(EditTextState.waiting_new_text)
    await state.update_data(text_type='messages', text_key=text_key)

    keyb = Edit_keyb().edit_text_back('messages')

    text = f"💬 Редактирование текста сообщения\n\n" \
           f"Ключ: `{text_key}`\n" \
           f"Текущий текст: {current_text}\n\n" \
           f"Отправьте новый текст:"

    await Sendler_msg().sendler_photo_call(call, LOGO, text, keyb)
