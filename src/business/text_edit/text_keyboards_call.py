from aiogram import types
from aiogram.dispatcher import FSMContext

from src.telegram.bot_core import BotDB
from src.business.text_edit.edit_keyboard import Edit_keyb
from src.telegram.sendler.sendler import Sendler_msg
from settings import LOGO


async def text_keyboards_call(call: types.CallbackQuery, state: FSMContext):
    """Отображает список текстов кнопок для редактирования"""
    # Получаем список пар (key, value) напрямую из CRUD
    texts = await BotDB.texts.get_all_texts('buttons')
    
    if not texts:
        await call.answer("Тексты кнопок не найдены")
        return

    await Sendler_msg.log_client_call(call)

    keyb = Edit_keyb().text_keyboards(texts)
    
    text = "📝 Редактирование текстов кнопок\n\nВыберите текст для редактирования:"
    
    await Sendler_msg().sendler_photo_call(call, LOGO, text, keyb)
    