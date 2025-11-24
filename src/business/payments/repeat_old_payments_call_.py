from aiogram import types
from aiogram.dispatcher import FSMContext

from src.telegram.sendler.sendler import Sendler_msg
from src.business.text_manager.text_manager import text_manager
from src.telegram.bot_core import BotDB
from src.telegram.keyboard.keyboards import Admin_keyb
from src.utils.logger._logger import logger_msg
from src.business.payments.payment_service import ensure_payment_link


async def repeat_old_payments_call(call: types.CallbackQuery, state: FSMContext):
    await Sendler_msg.log_client_call(call)

    await state.finish()

    users = await BotDB.users_read_by_filter({'need_paid': True, 'is_subs': True}) or []

    template = await text_manager.get_message('send_payment')
    btn_text = await text_manager.get_button_text('paid')

    total = len(users)
    sent = 0
    failed = 0

    for user in users:
        uid = getattr(user, 'id_user', None)
        if not uid:
            continue

        try:
            ensured = await ensure_payment_link(str(uid))
            link_payment = ensured.get('link') or ''
            amount = int(ensured.get('amount') or 0)
        except Exception as e:
            logger_msg(f"Repeat payments: ensure link error for {uid}: {e}")
            failed += 1
            continue

        if not link_payment or amount <= 0:
            failed += 1
            continue

        keyboard = Admin_keyb().payment_keyb(btn_text, link_payment)

        client_message = (template or '').format(summa=amount, link=f"<a href='{link_payment}'>Оплатить</a>")

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
    