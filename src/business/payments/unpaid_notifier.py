from aiogram.types import Message, CallbackQuery

from settings import LOGO
from src.telegram.bot_core import BotDB
from src.business.payments.payment_service import ensure_payment_link
from src.business.text_manager.text_manager import text_manager
from src.telegram.keyboard.keyboards import Admin_keyb
from src.telegram.sendler.sendler import Sendler_msg


async def notify_unpaid_if_needed(ctx, access_admin=False) -> bool:
    if isinstance(ctx, CallbackQuery):
        id_user = ctx.message.chat.id
        sender = Sendler_msg.send_msg_call
    else:
        id_user = ctx.chat.id
        sender = Sendler_msg.send_msg_message

    user_data = await BotDB.get_user_bu_id_user(id_user)

    if not getattr(user_data, 'need_paid', False):
        return False

    info = await ensure_payment_link(str(id_user))
    link = info.get('link')
    amount = info.get('amount')

    no_paid_msg = await text_manager.get_message('no_paid_msg')
    no_paid_msg = no_paid_msg.format(summa=amount, link=link)

    paid_text = await text_manager.get_button_text('paid')
    keyboard = Admin_keyb().no_paid(access_admin, paid_text, link)

    await sender(ctx, no_paid_msg, keyboard)

    return True
    