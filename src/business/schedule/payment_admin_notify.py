from settings import SEND_SUCCESS_PAYMENTS
from src.telegram.bot_core import BotDB
from src.telegram.sendler.sendler import Sendler_msg
from src.utils.logger._logger import logger_msg


async def send_admin_payment_info(bot, payment, norm_status: str) -> bool:
    if not SEND_SUCCESS_PAYMENTS:
        return False

    try:
        uid = getattr(payment, 'id_user', None)
        pid = getattr(payment, 'id_pk', None)
        reg = getattr(payment, 'reg_pay_num', None)
        created_at = getattr(payment, 'created_at', None)
        offer_id = getattr(payment, 'offer_id', None)
        amount = int(getattr(payment, 'amount', 0) or 0)

        user = await BotDB.get_user_bu_id_user(uid)
        user_login = getattr(user, 'login', None) if user else None
        user_first = getattr(user, 'first_name', None) if user else None
        user_last = getattr(user, 'last_name', None) if user else None
        is_subs = getattr(user, 'is_subs', False) if user else False
        need_paid = getattr(user, 'need_paid', False) if user else False
        received_forecast = getattr(user, 'received_forecast', False) if user else False
        send_payments = getattr(user, 'send_payments', False) if user else False

        fullname = f"{(user_first or '').strip()} {(user_last or '').strip()}".strip()
        created_iso = created_at.isoformat() if created_at else '-'

        offer_info = ''
        if offer_id:
            try:
                offer = await BotDB.offers.read_by_id(int(offer_id))
                offer_summa = getattr(offer, 'summa', None) if offer else None
                offer_info = f"\n• Offer ID: {int(offer_id)}" + (
                    f" (сумма: {int(offer_summa)})" if offer_summa is not None else "")
            except Exception as e:
                logger_msg(f"Ошибка чтения Offer {offer_id}: {e}")

        admin_text = (
                "💳 Оплата подтверждена\n"
                f"• Пользователь: {uid}"
                + (f" @{user_login}" if user_login else "")
                + (f" ({fullname})" if fullname else "")
                + f"\n• Сумма: {amount}"
                + f"\n• Платёж: id={int(pid)}; reg={reg}"
                + f"\n• Статус: {norm_status}"
                + f"\n• Создан: {created_iso}"
                + offer_info
        )

        await Sendler_msg.sendler_to_admin_mute_bot(bot, admin_text, None)
        return True
    except Exception as e:
        logger_msg(f"Ошибка отправки админам сведений об оплате {pid}: {e}")
        return False
