from aiogram import types
from aiogram.dispatcher import FSMContext

from settings import LOGO
from src.business.managers.check_manager import check_manager
from src.telegram.bot_core import BotDB
from src.business.text_edit.edit_keyboard import Edit_keyb
from src.telegram.keyboard.keyboards import Admin_keyb
from src.telegram.sendler.sendler import Sendler_msg


async def handle_new_text(message: types.Message, state: FSMContext):
    """Обрабатывает новый текст для обновления в базе данных"""
    data = await state.get_data()
    text_type = data.get('text_type')
    text_key = data.get('text_key')
    new_text = message.html_text

    if not text_type or not text_key:
        await message.answer("Ошибка: данные не найдены")
        await state.finish()
        return

    # Обновляем текст напрямую через CRUD: создаст или обновит запись по ключу
    success = await BotDB.texts.set_text_by_key(text_type, text_key, new_text)

    is_manager = await check_manager(message)

    keyboard = Admin_keyb().admin_keyboard(is_manager)

    if success:
        text = f"Текст обновлен: {text_type}.{text_key} = {new_text}"
    else:
        text = "❌ Ошибка при обновлении текста"

    await Sendler_msg().sendler_photo_message(message, LOGO, text, keyboard)

    await state.finish()

    return True
