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


async def approve_summa_call(call: types.CallbackQuery, state: FSMContext):
    data_state = await state.get_data()

    summa = data_state.get('summa', False)

    keyboard = Admin_keyb().back_bets_menu()

    if not summa:
        error_ = f'Кнопка устарела, начните процедуру заново'

        await Sendler_msg().sendler_photo_call(call, LOGO, error_, keyboard)

        return False

    await state.finish()

    res_send = await send_payments({"message": call.message, "summa": summa})

    await BotDB.bulk_set_need_paid_true()

    _msg = f'✅ Рассылка выполнена\nСумма: {summa}\nПользователей: {res_send["sent"]}\n' \
           f'Успешных доставок:{res_send["total"]}\nОшибки: {res_send["failed"]}'

    await Sendler_msg().sendler_photo_message(call.message, LOGO, _msg, keyboard)

    return True
