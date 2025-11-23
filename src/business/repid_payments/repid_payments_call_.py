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
from src.business.offers.offers_json import parse_id_users


async def repid_payments_call(call: types.CallbackQuery, state: FSMContext):
    await Sendler_msg.log_client_call(call)

    await state.finish()

    offers = await BotDB.offers.read_by_filter({}) or []
    now = datetime.utcnow()
    try:
        offers = [o for o in offers if (getattr(o, 'expire_at', None) is None) or (getattr(o, 'expire_at') > now)]
        offers.sort(key=lambda o: getattr(o, 'created_at', now), reverse=True)
        offer = offers[0] if offers else None
    except Exception:
        offer = offers[0] if offers else None

    if not offer:
        keyboard = Admin_keyb().bet_keyboard()
        _msg = f'❌ Актуальных предложений в боте нет'
        await Sendler_msg.send_msg_message(call.message, _msg, keyboard)
        return True

    _msg_from_users = await text_manager.get_message('offer_send')
    get_offer_btn = await text_manager.get_button_text('get_offer')
    _msg_from_users = (_msg_from_users or '').format(summa=getattr(offer, 'summa', 0))

    users = await BotDB.get_users_subscribed() or []
    total = len(users)
    sent = 0
    failed = 0
    pin_failed = 0
    already_paid = 0

    paid_list = parse_id_users(getattr(offer, 'paid_users', None))

    for uid in users:
        if str(uid) in paid_list:
            already_paid += 1
            continue
        keyboard = Admin_keyb().offers_client(offer_id=int(getattr(offer, 'id_pk')), get_offer_btn=get_offer_btn)
        try:
            res = await call.message.bot.send_message(int(uid), _msg_from_users, reply_markup=keyboard,
                                                      disable_web_page_preview=True, protect_content=True)
            try:
                await call.message.bot.pin_chat_message(chat_id=int(uid), message_id=res['message_id'])
            except:
                pin_failed += 1
            sent += 1
        except Exception as e:
            logger_msg(f"Resend offers: send error for {uid}: {e}")
            failed += 1

    keyboard = Admin_keyb().bet_keyboard()
    _msg = (
        f"✅ Повторная рассылка предложений завершена\n"
        f"Подписанных пользователей: {total}\n"
        f"Уже оплатили: {already_paid}\n"
        f"Отправлено: {sent}\n"
        f"Ошибки отправки: {failed}"
    )
    await Sendler_msg.send_msg_message(call.message, _msg, keyboard)
    return True
