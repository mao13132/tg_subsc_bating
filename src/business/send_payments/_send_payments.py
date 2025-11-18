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
from src.business.payments_api.create_payment_ckassa import CKassaPayment
from src.utils.logger._logger import logger_msg
from settings import SHOPKEY, SECKEY


async def send_payments(settings):
    summa = int(settings['summa'])
    amount_kop = summa * 100
    message = settings['message']

    name_shop = 'Основной Магазин'
    service_code = '1000-13864-2'

    template = await text_manager.get_message('send_payment')
    btn_text = await text_manager.get_button_text('paid')

    users = await BotDB.users_read_by_filter(filters={'is_subs': True}) or []

    # 4) Рассылка по ID пользователей
    sent, failed = 0, 0
    for user in users:
        uid = user.id_user

        payment_data = {
            "serviceCode": service_code,
            "amount": int(amount_kop),
            "comission": 0,
            "properties": [
                {"name": "ЛИЦЕВОЙ_СЧЕТ", "value": str(uid)}
            ]
        }

        try:
            reg_pay_num = await CKassaPayment(payment_data).create_payment(name_shop, SHOPKEY, SECKEY)

            link_payment = reg_pay_num['payUrl']
        except Exception as e:
            logger_msg(f"CKassa: ошибка создания платежа для {uid}: {e}")

            continue

        keyboard = Admin_keyb().payment_keyb(btn_text, link_payment)

        client_message = template.format(summa=summa, link=f"<a href='{link_payment}'>Оплатить</a>")

        try:
            res = await message.bot.send_message(int(uid), client_message, reply_markup=keyboard,
                                                 disable_web_page_preview=True, protect_content=True)
            await message.bot.pin_chat_message(chat_id=int(uid), message_id=res['message_id'])
        except:
            res = False

        if res:
            sent += 1
        else:
            failed += 1

        try:
            await BotDB.payments.create({
                'id_user': str(uid),
                'amount': int(summa),
                'reg_pay_num': reg_pay_num['regPayNum'],
                'status': 'sent' if res else 'failed',
                'link': link_payment
            })
        except Exception as e:
            logger_msg(f"SQL: ошибка записи платежа для {uid}: {e}")

        continue

    # 5) Возвращаем краткий итог
    return {"total": len(users), "sent": sent, "failed": failed}
