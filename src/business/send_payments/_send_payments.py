# ---------------------------------------------
# Program by @developer_telegrams
#
#
# Version   Date        Info
# 1.0       2023    Initial Version
#
# ---------------------------------------------
from src.business.text_manager.text_manager import text_manager
from src.telegram.bot_core import BotDB
from src.telegram.keyboard.keyboards import Admin_keyb


async def send_payments(settings):
    """
    Рассылает приглашение к оплате без генерации ссылок.

    Шаги:
    1) Читаем сумму и контекст `message` из настроек.
    2) Загружаем тексты: шаблон сообщения и подписи кнопок.
    3) Получаем целевую аудиторию пользователей по фильтрам.
    4) Для каждого пользователя отправляем сообщение с клавиатурой выбора способа оплаты и пинним его.
    5) Считаем метрики отправки (sent/failed/ok_ids).
    6) Проставляем `send_payments=True` только успешным.
    7) Возвращаем краткую сводку для админа.
    """

    # 1) Вход: сумма и объект сообщения
    summa = int(settings['summa'])
    message = settings['message']

    # 2) Тексты интерфейса
    template_choose = await text_manager.get_message('payment_choose')
    pay_rub_text = await text_manager.get_button_text('pay_rub')
    pay_other_text = await text_manager.get_button_text('pay_other')

    # 3) Аудитория: подписаны, не получали рассылку счетов, получили прогноз
    users = await BotDB.users_read_by_filter(
        filters={'is_subs': True, 'send_payments': False, 'received_forecast': True}
    ) or []

    # 4) Отправка приглашения без создания счёта
    sent, failed = 0, 0
    ok_ids = []
    for user in users:
        uid = user.id_user

        # Клавиатура с выбором способа оплаты
        keyboard = Admin_keyb().payment_choose(pay_rub_text, pay_other_text, summa)

        # Текст с подстановкой суммы
        client_message = template_choose.format(summa=summa)

        try:
            res = await message.bot.send_message(
                int(uid), client_message, reply_markup=keyboard,
                disable_web_page_preview=True, protect_content=True
            )
            # Пин сообщения у пользователя
            # await message.bot.pin_chat_message(chat_id=int(uid), message_id=res['message_id'])
        except Exception:
            res = False

        # Учёт метрик
        if res:
            sent += 1
            ok_ids.append(str(uid))
        else:
            failed += 1

    # 6) Маркируем только тем, кому доставлено
    if ok_ids:
        try:
            await BotDB.set_send_payments_for_ids(ok_ids, True)
        except Exception:
            pass

    # 7) Сводка
    return {"total": len(users), "sent": sent, "failed": failed, "ok_ids": ok_ids}
