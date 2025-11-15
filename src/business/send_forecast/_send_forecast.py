# ---------------------------------------------
# Program by @developer_telegrams
#
# Массовая рассылка загруженного прогноза всем пользователям,
# у которых нет задолженности (need_paid == False).
# ---------------------------------------------
from src.business.posts_manager.message_content_codec import send_records_grouped
from src.telegram.bot_core import BotDB


async def send_forecast_broadcast(settings):
    """
    Разослать загруженный прогноз всем пользователям без задолженности.

    Параметры:
    - settings['message']: объект сообщения (для доступа к боту: message.bot)
    - settings['messages']: список записей прогноза из БД (если не передан, будет прочитан внутри)

    Возвращает:
    - dict: {"total": общее_число_пользователей, "sent": успешно_доставлено, "failed": ошибки}
    """
    message = settings['message']
    messages = settings.get('messages')

    # Если сообщения не переданы, читаем весь загруженный прогноз из БД
    if messages is None:
        messages = await BotDB.user_messages.read_by_filter({})

    # Берём только пользователей без задолженности
    users = await BotDB.get_users_need_paid_false() or []

    sent, failed = 0, 0

    # Отправка группированного контента каждому пользователю
    for uid in users:
        try:
            res = await send_records_grouped(message.bot, int(uid), messages)
        except:
            res = False

        if res:
            sent += 1
        else:
            failed += 1

    # Итоговая сводка для админа
    return {"total": len(users), "sent": sent, "failed": failed}
    