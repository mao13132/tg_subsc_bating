# ---------------------------------------------
# Program by @developer_telegrams
#
#
# Version   Date        Info
# 1.0       2023    Initial Version
#
# ---------------------------------------------
from aiogram import types
from aiogram.dispatcher import FSMContext

from src.business.text_manager.text_manager import text_manager
from src.telegram.bot_core import BotDB
from src.telegram.keyboard.keyboards import Admin_keyb
from src.telegram.sendler.sendler import Sendler_msg
from src.business.access_checks import check_need_paid, ensure_subscription


async def get_offer_client_call(call: types.CallbackQuery, state: FSMContext):
    # 1) Идентификатор пользователя
    id_user = call.message.chat.id

    # 2) Проверка необходимости оплаты
    if await check_need_paid(call):
        return True

    # 3) Проверка подписки
    if not await ensure_subscription(call):
        return False

    # 4) Отмечаем намерение пользователя получить оффер
    await BotDB.edit_user('get_offer', True, id_user)

    # 5) Сообщение-подтверждение действия (alert)
    _msg = await text_manager.get_message('get_offer')
    await call.answer(_msg, show_alert=True)

    # 6) Логирование клика
    await Sendler_msg.log_client_call(call)

    # 7) Обновление клавиатуры (кнопка «Получить мотивацию» станет активной)
    back = await text_manager.get_button_text('back')
    try:
        await call.message.edit_reply_markup(Admin_keyb().actual_motivation(back, '', user_get_offer=True))
    except:
        pass

    # 8) Успешное завершение
    return True
