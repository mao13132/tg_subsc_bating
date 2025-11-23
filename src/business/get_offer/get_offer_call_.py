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

from src.business.text_manager.text_manager import text_manager
from src.telegram.keyboard.keyboards import Admin_keyb
from src.telegram.sendler.sendler import Sendler_msg
from src.utils.logger._logger import logger_msg
from src.telegram.bot_core import BotDB
from src.business.payments.payment_service import ensure_offer_payment


async def get_offer_call(call: types.CallbackQuery, state: FSMContext):
    try:
        offer_id = str(call.data).split('-')[-1]

        offer_id = int(offer_id)
    except Exception as es:
        msg = f'Ошибка при запуске get_offer_call: {es}'
        logger_msg(msg)
        return False

    offer = await BotDB.offers.read_by_id(offer_id)

    if not offer:
        error_ = f'❌ Прогноз не актуален'

        await call.answer(error_, show_alert=True)

        await call.message.delete()

        return False

    amount = int(getattr(offer, 'summa', 0) or 0)

    uid = call.message.chat.id

    try:
        ensured = await ensure_offer_payment(str(uid), offer.id_pk, amount)
        pay_url = ensured.get('link') or ''
    except Exception as e:
        logger_msg(f"CKassa: ensure_offer_payment ошибка для {uid}: {e}")
        await call.answer('Ошибка создания платежа, попробуйте позже', show_alert=True)
        return False

    template = await text_manager.get_message('send_payment')
    btn_text = await text_manager.get_button_text('paid')

    keyboard = Admin_keyb().payment_keyb(btn_text, pay_url)

    client_message = (template or '').format(summa=amount, link=f"<a href='{pay_url}'>Оплатить</a>")

    await call.message.bot.send_message(call.message.chat.id, client_message,
                                        reply_markup=keyboard, disable_web_page_preview=True,
                                        protect_content=True)

    try:
        await call.message.delete()
    except:
        pass

    await Sendler_msg.log_client_call(call)

    return True
