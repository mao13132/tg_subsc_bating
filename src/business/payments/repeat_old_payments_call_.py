from aiogram import types
from aiogram.dispatcher import FSMContext

from src.telegram.sendler.sendler import Sendler_msg
from src.business.text_manager.text_manager import text_manager
from src.telegram.bot_core import BotDB
from src.telegram.keyboard.keyboards import Admin_keyb
from src.utils.logger._logger import logger_msg
from src.business.text_manager.text_manager import text_manager


async def repeat_old_payments_for_debtors(bot):
    """
    Повторно шлём приглашение к оплате должникам без генерации ссылок.

    Шаги:
    1) Получаем должников (need_paid=True, is_subs=True).
    2) Загружаем тексты: шаблон «payment_choose» и подписи кнопок.
    3) Для каждого должника берём последнюю сумму из `payments`.
    4) Отправляем сообщение с клавиатурой выбора способа оплаты и пинним его.
    5) Считаем метрики и возвращаем итог.
    """

    users = await BotDB.users_read_by_filter({'need_paid': True, 'is_subs': True}) or []

    template_choose = await text_manager.get_message('payment_choose')
    pay_rub_text = await text_manager.get_button_text('pay_rub')
    pay_other_text = await text_manager.get_button_text('pay_other')

    total = len(users)
    sent = 0
    failed = 0

    for user in users:
        uid = getattr(user, 'id_user', None)
        if not uid:
            continue

        try:
            latest = await BotDB.payments.read_latest_by_user(str(uid))
            amount = int(getattr(latest, 'amount', 0) or 0) if latest else 0
        except Exception as e:
            logger_msg(f"Repeat payments: read latest payment error for {uid}: {e}")
            failed += 1
            continue

        if amount <= 0:
            failed += 1
            continue

        keyboard = Admin_keyb().payment_choose(pay_rub_text, pay_other_text, amount)
        client_message = (template_choose or '').format(summa=amount)

        try:
            res = await bot.send_message(int(uid), client_message, reply_markup=keyboard,
                                         disable_web_page_preview=True, protect_content=True)
            sent += 1
        except Exception as e:
            logger_msg(f"Repeat payments: send error for {uid}: {e}")
            failed += 1

    return {"total": total, "sent": sent, "failed": failed}


async def repeat_old_payments_call(call: types.CallbackQuery, state: FSMContext):
    """
    Колбэк: повторная рассылка приглашений к оплате для должников.

    1) Логируем, завершаем текущее состояние.
    2) Получаем должников и тексты.
    3) Для каждого берём последнюю сумму из `payments`.
    4) Отправляем сообщение с клавиатурой выбора способа оплаты и пинним его.
    5) Возвращаем администратору сводку.
    """
    await Sendler_msg.log_client_call(call)

    await state.finish()

    users = await BotDB.users_read_by_filter({'need_paid': True, 'is_subs': True}) or []

    template_choose = await text_manager.get_message('payment_choose')
    pay_rub_text = await text_manager.get_button_text('pay_rub')
    pay_other_text = await text_manager.get_button_text('pay_other')

    total = len(users)
    sent = 0
    failed = 0

    for user in users:
        uid = getattr(user, 'id_user', None)
        if not uid:
            continue

        try:
            latest = await BotDB.payments.read_latest_by_user(str(uid))
            amount = int(getattr(latest, 'amount', 0) or 0) if latest else 0
        except Exception as e:
            logger_msg(f"Repeat payments: read latest payment error for {uid}: {e}")
            failed += 1
            continue

        if amount <= 0:
            failed += 1
            continue

        keyboard = Admin_keyb().payment_choose(pay_rub_text, pay_other_text, amount)

        client_message = (template_choose or '').format(summa=amount)

        try:
            res = await call.message.bot.send_message(int(uid), client_message, reply_markup=keyboard,
                                                      disable_web_page_preview=True, protect_content=True)
            try:
                await call.message.bot.pin_chat_message(chat_id=int(uid), message_id=res['message_id'])
            except Exception:
                pass
            sent += 1
        except Exception as e:
            logger_msg(f"Repeat payments: send error for {uid}: {e}")
            failed += 1

    keyboard = Admin_keyb().bet_keyboard()
    _msg = (
        f"✅ Повторная рассылка счетов завершена\n"
        f"Должники: {total}\n"
        f"Отправлено: {sent}\n"
        f"Ошибки отправки: {failed}"
    )

    await Sendler_msg.send_msg_call(call, _msg, keyboard)

    return True
    