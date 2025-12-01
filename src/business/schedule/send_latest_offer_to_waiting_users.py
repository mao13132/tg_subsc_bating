from datetime import datetime

from src.telegram.bot_core import BotDB, bot
from src.business.offers.send_offer_content import send_offer_content_to_user
from src.business.offers.offers_json import add_id_user, parse_id_users
from src.utils.logger._logger import logger_msg


async def send_latest_offer_to_waiting_users():
    """Рассылает последний актуальный Offer всем ожидающим пользователям.

    Алгоритм:
    1) Находит последний неистёкший Offer
    2) Если оффера нет — возвращает False
    3) Получает пользователей с фильтром get_offer=True, is_subs=True, need_paid=False
    4) Если аудитория пуста — возвращает False
    5) Отправляет контент оффера каждому пользователю
    6) Добавляет успешных получателей в Offer.id_users
    7) Снимает флаг get_offer у всех успешно получивших и проставляет received_forecast=True
    8) Возвращает True при успешном прохождении шагов
    """
    # 1) Читаем список офферов и выбираем последний неистёкший
    offers = await BotDB.offers.read_by_filter({}) or []
    now = datetime.utcnow()
    try:
        offers = [o for o in offers if (getattr(o, 'expire_at', None) is None) or (getattr(o, 'expire_at') > now)]
        offers.sort(key=lambda o: getattr(o, 'created_at', now), reverse=True)
        offer = offers[0] if offers else None
    except Exception:
        offer = offers[0] if offers else None

    # 2) Нет оффера — завершаем
    if not offer:
        return False

    # 3) Получаем аудиторию для рассылки: ждут оффер, подписаны
    try:
        offer_summa = int(getattr(offer, 'summa', 0) or 0)
    except Exception:
        offer_summa = 0
    filters = {'get_offer': True, 'is_subs': True}
    if offer_summa > 0:
        filters['need_paid'] = False
    users = await BotDB.get_users_by_filter(filters=filters) or []
    # 4) Пустая аудитория — завершаем
    if not users:
        return False

    # 5) Рассылка контента оффера пользователям
    ok_uids = []
    recipients = parse_id_users(getattr(offer, 'id_users', None))
    for user_data in users:
        uid = getattr(user_data, 'id_user', None)
        if not uid:
            continue

        # 5.1) Пропускаем, если пользователю уже отправляли этот оффер
        if str(uid) in recipients:
            continue

        try:
            sent_ok = await send_offer_content_to_user(bot, int(uid), int(getattr(offer, 'id_pk', 0)))
        except Exception as e:
            logger_msg(f"Offer send error for {uid}: {e}")
            sent_ok = False

        # 6) Добавляем успешных получателей в Offer.id_users
        if sent_ok:
            ok_uids.append(str(uid))
            try:
                ids_json = add_id_user(getattr(offer, 'id_users', None), uid)
                await BotDB.offers.update_by_id(int(getattr(offer, 'id_pk', 0)), {"id_users": ids_json})
            except Exception as e:
                logger_msg(f"Update offer recipients error: {e}")

    # 7) Снимаем get_offer у получивших и ставим received_forecast=True
    for uid in ok_uids:
        try:
            await BotDB.edit_user_by_filter({'id_user': str(uid)}, {'get_offer': False, 'received_forecast': True})
        except Exception:
            pass

    # 8) Итог успешной рассылки
    return bool(ok_uids)
    