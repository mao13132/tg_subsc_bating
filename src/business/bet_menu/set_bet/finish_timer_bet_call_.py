from aiogram import types
from aiogram.dispatcher import FSMContext

from settings import LOGO
from src.business.text_manager.text_manager import text_manager
from src.telegram.keyboard.keyboards import Admin_keyb
from src.telegram.sendler.sendler import Sendler_msg
from src.telegram.bot_core import BotDB
from datetime import datetime
from src.business.send_offer._send_offer import send_offer_to_audience
from src.business.offers.offers_json import add_id_users
import json
from types import SimpleNamespace


async def finish_timer_bet_call(call: types.CallbackQuery, state: FSMContext):
    """
    Завершает настройку предложения:
    1) Фиксирует срок удаления для собранного контента
    2) Создаёт Offer со всей партией сообщений и суммой
    3) Формирует текст для рассылки из шаблона messages.offer_send
    4) Рассылает текст всем подписанным пользователям
    5) Сохраняет ID успешных получателей в Offer
    6) Возвращает администратору краткую сводку
    """
    # 1. Логирование вызова
    await Sendler_msg.log_client_call(call)

    id_user = call.message.chat.id

    # 2. Чтение данных из FSM
    data = await state.get_data()
    batch_key = data.get('batch_key')
    summa = data.get('summa')
    dt_iso = data.get('timer_bet_dt_iso')
    dt_str = data.get('timer_bet_dt_str')

    # 3. Очистка чужих партий текущего пользователя
    if batch_key:
        await BotDB.user_messages.delete_not_batch_key(id_user, batch_key)

    # 4. Проставляем срок удаления для партийных сообщений
    if dt_iso:
        dt = datetime.fromisoformat(str(dt_iso))
        await BotDB.user_messages.set_expire_by_batch_key(id_user, batch_key, dt)
        if not dt_str:
            dt_str = dt.strftime('%d.%m.%Y %H:%M')

    # 5. Завершаем FSM
    await state.finish()

    # 6. Сбрасываем флаг полученного прогноза для всех
    await BotDB.bulk_update_users_by_filter({}, {"received_forecast": False})

    # 7. Читаем собранные сообщения текущего пользователя
    records = await BotDB.user_messages.read_by_filter({
        'id_user': str(id_user),
        'batch_key': str(batch_key)
    })

    offer_payload_list = []
    for r in records:
        offer_payload_list.append({
            'content': getattr(r, 'content', '') or '',
            'media_group_id': getattr(r, 'media_group_id', None),
            'mg_index': getattr(r, 'mg_index', None),
        })

    # 8. Создаём Offer, сохраняем всю партию сообщений
    offer_json = json.dumps(offer_payload_list, ensure_ascii=False)
    offer_data = {
        "id_user": str(id_user),
        "summa": int(str(summa)) if str(summa).isdigit() else 0,
        "message_json": offer_json,
        "expire_at": datetime.fromisoformat(str(dt_iso)) if dt_iso else None,
    }

    offer_id = await BotDB.offers.create(offer_data)

    # 9. Получаем текст шаблона предложения и кнопку
    _msg_from_users = await text_manager.get_message('offer_send')

    get_offer_btn = await text_manager.get_button_text('get_offer')

    _msg_from_users = _msg_from_users.format(summa=summa)

    # 10. Получаем аудиторию — все подписаны
    audience_ids = await BotDB.get_users_subscribed() or []

    # 11. Рассылаем текст аудитории
    ok_ids = await send_offer_to_audience({
        "message": call.message,
        "text": _msg_from_users,
        "audience_ids": audience_ids,
        "get_offer_btn": get_offer_btn,
        "offer_id": offer_id,
    })

    # 12. Сохраняем ID успешных получателей в Offer
    ids_json = add_id_users(None, ok_ids)
    await BotDB.offers.update_by_id(int(offer_id), {"id_users": ids_json})

    total = len(audience_ids)
    sent = len(ok_ids)
    failed = max(total - sent, 0)

    # 13. Готовим сводку администратору
    summary_msg = (
        f'✅ Предложение разослано\n'
        f'Пользователей: {total}\n'
        f'Успешных доставок: {sent}\n'
        f'Ошибки: {failed}\n'
        f'🗓 Дата удаления прогноза: {dt_str or "не задана"}'
    )

    # 14. Отдаём сводку и клавиатуру
    keyboard = Admin_keyb().bet_keyboard()

    await Sendler_msg.send_msg_call(call, summary_msg, keyboard)

    return True
