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
from settings import LOGO
from src.business.payments.payment_service import create_ckassa_payment, record_payment, is_payment_bad


async def repid_payments_call(call: types.CallbackQuery, state: FSMContext):
    await Sendler_msg.log_client_call(call)

    await state.finish()

    users = await BotDB.users_read_by_filter({'need_paid': True, 'is_subs': True}) or []
    total = len(users)
    sent = 0
    failed = 0
    no_link = 0
    no_payment = 0
    pin_failed = 0

    template = await text_manager.get_message('payment_reminder') or await text_manager.get_message('no_paid_msg')
    btn_text = await text_manager.get_button_text('paid')

    for user in users:
        uid = user.id_user
        latest = await BotDB.payments.read_latest_by_user(uid)
        if not latest:
            no_payment += 1
            continue
        link = latest.link or ''
        need_recreate = is_payment_bad(latest)
        invalid_link = link in ('', 'created')

        new_reg = None
        if need_recreate:
            try:
                name_shop = 'Основной Магазин'
                service_code = '1000-13864-2'
                created = await create_ckassa_payment(uid, int(latest.amount), service_code=service_code, name_shop=name_shop)
                link = created['payUrl']
                new_reg = created['regPayNum']
            except Exception as e:
                logger_msg(f"Resend payments: recreate error for {uid}: {e}")
                no_link += 1
                continue
        else:
            if invalid_link:
                no_link += 1
                continue

        keyboard = Admin_keyb().payment_keyb(btn_text, link)
        client_message = template.format(summa=latest.amount, link=link)
        try:
            res = await call.message.bot.send_message(int(uid), client_message, reply_markup=keyboard,
                                                      disable_web_page_preview=True, protect_content=True)
            try:
                await call.message.bot.pin_chat_message(chat_id=int(uid), message_id=res['message_id'])
            except:
                pin_failed += 1
        except Exception as e:
            logger_msg(f"Resend payments: send error for {uid}: {e}")
            res = False

        status = 'resent' if res else 'resent_failed'
        if res:
            sent += 1
        else:
            failed += 1

        if need_recreate and new_reg:
            await record_payment(uid, int(latest.amount), new_reg, link, status)
        else:
            try:
                await BotDB.payments.update_by_id(latest.id_pk, {'status': status})
            except Exception as e:
                logger_msg(f"Payments status update error for {uid}: {e}")

    keyboard = Admin_keyb().bet_keyboard()
    _msg = (
        f"✅ Повторная рассылка счетов завершена\n"
        f"Всего должников: {total}\n"
        f"Отправлено: {sent}\n"
        f"Ошибки отправки: {failed}\n"
        f"Без ссылки: {no_link}\n"
        f"Нет записи платежа: {no_payment}"
    )
    await Sendler_msg().sendler_photo_message(call.message, LOGO, _msg, keyboard)
    return True
