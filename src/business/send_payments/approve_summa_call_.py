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

from settings import LOGO
from src.business.send_payments._send_payments import send_payments
from src.telegram.keyboard.keyboards import Admin_keyb
from src.telegram.sendler.sendler import Sendler_msg
from src.telegram.bot_core import BotDB
from src.business.text_manager.text_manager import text_manager
from src.business.payments.repeat_old_payments_call_ import repeat_old_payments_for_debtors


async def approve_summa_call(call: types.CallbackQuery, state: FSMContext):
    await Sendler_msg.log_client_call(call)

    data_state = await state.get_data()

    summa = data_state.get('summa', False)

    keyboard = Admin_keyb().back_bets_menu()

    if not summa:
        error_ = f'Кнопка устарела, начните процедуру заново'

        await Sendler_msg.send_msg_call(call, error_, keyboard)

        return False

    await state.finish()

    try:
        await call.message.edit_reply_markup(reply_markup=Admin_keyb().wait_keyb())
    except:
        pass

    if str(summa) == '0':
        replacement_text = await text_manager.get_message('replacement')
        get_forecast_btn = await text_manager.get_button_text('get_forecast')
        keyb_forecast = Admin_keyb().forecast_call_keyb(get_forecast_btn)

        users = await BotDB.users_read_by_filter({'is_subs': True}) or []
        sent = 0
        failed = 0
        for user in users:
            uid = user.id_user
            try:
                res = await call.message.bot.send_message(int(uid), replacement_text,
                                                          reply_markup=keyb_forecast,
                                                          disable_web_page_preview=True,
                                                          protect_content=True)
                sent += 1
            except:
                failed += 1

        _msg = (
            f'✅ Рассылка выполнена (замена)\n'
            f'Пользователей: {len(users)}\n'
            f'Отправлено: {sent}\n'
            f'Ошибки: {failed}'
        )

        await Sendler_msg.send_msg_message(call.message, _msg, keyboard)
    else:
        res_send = await send_payments({"message": call.message, "summa": summa})

        _msg = (
            f'✅ Рассылка выполнена\n'
            f'Сумма: {summa}\n'
            f'Пользователей: {res_send["sent"]}\n'
            f'Успешных доставок:{res_send["total"]}\n'
            f'Ошибки: {res_send["failed"]}'
        )

        try:
            res_repeat = await repeat_old_payments_for_debtors(call.message.bot)
            _msg += (
                f'\n\n♻️ Повтор счетов должникам\n'
                f'Должники: {res_repeat["total"]}\n'
                f'Отправлено: {res_repeat["sent"]}\n'
                f'Ошибки отправки: {res_repeat["failed"]}'
            )
        except Exception:
            pass

        ok_ids = res_send.get("ok_ids", [])

        if ok_ids:
            try:
                await BotDB.set_need_paid_for_ids(ok_ids, True)
            except Exception:
                pass
            try:
                await BotDB.set_send_payments_for_ids(ok_ids, True)
            except Exception:
                pass

        await Sendler_msg.send_msg_message(call.message, _msg, keyboard)

    return True
