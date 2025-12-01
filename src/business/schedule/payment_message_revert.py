from datetime import datetime, timedelta

from settings import PAYMENT_TIMEOUT_MINUTES
from src.telegram.bot_core import BotDB, bot
from src.business.text_manager.text_manager import text_manager
from src.telegram.keyboard.keyboards import Admin_keyb
from src.utils.logger._logger import logger_msg


async def revert_payment_messages_once() -> int:
    before = datetime.utcnow() - timedelta(minutes=int(PAYMENT_TIMEOUT_MINUTES))
    try:
        messages = await BotDB.payment_messages.read_active_older_than(before) or []
    except Exception as e:
        logger_msg(f"Payment messages select error: {e}")
        return 0

    if not messages:
        return 0

    template_choose = await text_manager.get_message('payment_choose')
    pay_rub_text = await text_manager.get_button_text('pay_rub')
    pay_other_text = await text_manager.get_button_text('pay_other')

    reverted = 0
    for pm in messages:
        try:
            chat_id = int(getattr(pm, 'chat_id'))
            message_id = int(getattr(pm, 'message_id'))
            amount = int(getattr(pm, 'amount') or 0)

            kb = Admin_keyb().payment_choose(pay_rub_text, pay_other_text, amount)

            client_message = (template_choose or '').format(summa=amount)

            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=client_message,
                reply_markup=kb,
                disable_web_page_preview=True
            )

            await BotDB.payment_messages.mark_reverted_by_id(int(getattr(pm, 'id_pk')))
            reverted += 1
        except Exception as e:
            logger_msg(f"Payment message revert error: {e}")
            try:
                await BotDB.payment_messages.mark_error_by_id(int(getattr(pm, 'id_pk')))
            except Exception:
                pass
    return reverted
    