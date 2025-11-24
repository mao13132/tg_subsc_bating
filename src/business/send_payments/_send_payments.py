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
from src.business.payments.payment_service import create_ckassa_payment, record_payment


async def send_payments(settings):
    summa = int(settings['summa'])
    message = settings['message']

    name_shop = 'Основной Магазин'
    service_code = '1000-13864-2'

    template = await text_manager.get_message('send_payment')
    btn_text = await text_manager.get_button_text('paid')

    users = await BotDB.users_read_by_filter(filters={'is_subs': True, 'send_payments': False}) or []

    # 4) Рассылка по ID пользователей
    sent, failed = 0, 0
    ok_ids = []
    for user in users:
        uid = user.id_user

        try:
            created = await create_ckassa_payment(uid, summa, service_code=service_code, name_shop=name_shop)
            link_payment = created['payUrl']
            reg_pay_num = created['regPayNum']
        except Exception:
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
            ok_ids.append(str(uid))
        else:
            failed += 1

        await record_payment(uid, summa, reg_pay_num, link_payment, 'sent' if res else 'failed')

        continue

    if ok_ids:
        try:
            await BotDB.set_send_payments_for_ids(ok_ids, True)
        except Exception:
            pass

    # 5) Возвращаем краткий итог
    return {"total": len(users), "sent": sent, "failed": failed, "ok_ids": ok_ids}
