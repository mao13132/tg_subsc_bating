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


async def send_payments(settings):
    summa = settings['summa']

    message = settings['message']

    payment_link = 'https://google.com'

    template = await text_manager.get_message('send_payment')

    btn_text = await text_manager.get_button_text('paid')

    # 3) Получаем список пользователей, которым нужно отправить сообщение
    # users = await BotDB.get_users_need_paid_false() or []
    users = await BotDB.users_read_by_filter(filters={'is_subs': True}) or []

    # 4) Рассылка по ID пользователей
    sent, failed = 0, 0
    for uid in users:
        client_payment_link = f"{payment_link}?utm_source={uid}"

        client_message = template.format(summa=summa, link=client_payment_link)

        keyboard = Admin_keyb().payment_keyb(btn_text, client_payment_link)

        try:
            res = await message.bot.send_message(int(uid), client_message, reply_markup=keyboard)

            await message.bot.pin_chat_message(chat_id=int(uid), message_id=res['message_id'])
        except:
            res = False

        if res:
            sent += 1
        else:
            failed += 1

        continue

    # 5) Возвращаем краткий итог
    return {"total": len(users), "sent": sent, "failed": failed}
