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

from src.telegram.sendler.sendler import Sendler_msg
from src.business.text_manager.text_manager import text_manager
from src.telegram.bot_core import BotDB
from src.telegram.keyboard.keyboards import Admin_keyb
from src.utils.logger._logger import logger_msg
from datetime import datetime


async def repid_motivations_call(call: types.CallbackQuery, state: FSMContext,
                                 resend_from_create_offer=False, new_summa=False):
    await Sendler_msg.log_client_call(call)

    motivations = await BotDB.motivations.read_by_filter({}) or []
    try:
        motivations.sort(key=lambda m: getattr(m, 'created_at', datetime.utcnow()), reverse=True)
        motivation = motivations[0] if motivations else None
    except Exception:
        motivation = motivations[0] if motivations else None

    if not motivation:
        keyboard = Admin_keyb().bet_keyboard()
        _msg = f'❌ Нет предложения которое можно повторить. Создай новое предложение!'
        await Sendler_msg.send_msg_message(call.message, _msg, keyboard)
        return True

    # 3) текст сообщения и кнопка
    _msg_from_users = await text_manager.get_message('motivation_send')
    get_offer_btn = await text_manager.get_button_text('get_motivation')

    # Если передана, новая сумма, то вставляем её, если нет, то от последнего предложения
    if new_summa:
        _msg_from_users = (_msg_from_users or '').format(summa=int(new_summa))
        try:
            current_summa = int(getattr(motivation, 'summa', 0))
            if int(new_summa) != int(current_summa):
                await BotDB.motivations.update_by_id(int(getattr(motivation, 'id_pk')), {"summa": int(new_summa)})
        except Exception:
            pass
    else:
        _msg_from_users = (_msg_from_users or '').format(summa=getattr(motivation, 'summa', 0))

    # 4) подписчики
    # Если переотправка при создание офера, то отправляем только тем кто не соглашался ещё на предложение
    if resend_from_create_offer:
        msg_ = ' + не нажавшие кнопку ранее'
        users = await BotDB.get_users_by_filter(filters={'get_offer': False})
    else:
        msg_ = ''
        users = await BotDB.get_users_by_filter(filters={})

    total = len(users)
    sent = 0
    failed = 0
    pin_failed = 0
    ok_ids = []

    # 5) рассылка оффера
    for user_data in users:
        uid = user_data.id_user

        keyboard = Admin_keyb().offers_client(get_offer_btn=get_offer_btn)
        try:
            # 5) отправка и попытка закрепить сообщение
            res = await call.message.bot.send_message(int(uid), _msg_from_users, reply_markup=keyboard,
                                                      disable_web_page_preview=True, protect_content=True)
            sent += 1
            ok_ids.append(str(uid))
        except Exception as e:
            logger_msg(f"Resend offers: send error for {uid}: {e}")
            failed += 1

    try:
        from src.business.offers.offers_json import add_id_users
        ids_json = add_id_users(getattr(motivation, 'id_users', None), ok_ids)
        await BotDB.motivations.update_by_id(int(getattr(motivation, 'id_pk')), {"id_users": ids_json})
    except Exception as e:
        logger_msg(f"Update motivation recipients error: {e}")

    # 6) итоговый отчёт администратору
    keyboard = Admin_keyb().bet_keyboard()

    _msg = (
        f"✅ Повторная рассылка предложений завершена\n"
        f"Подписанных{msg_} (на группу) пользователей: {total}\n"
        f"Отправлено: {sent}\n"
        f"Ошибки отправки: {failed}"
    )

    if resend_from_create_offer:
        keyboard = None

    await Sendler_msg.send_msg_message(call.message, _msg, keyboard)
    return True
