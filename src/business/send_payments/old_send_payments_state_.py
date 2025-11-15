# ---------------------------------------------
# Program by @developer_telegrams
#
#
# Version   Date        Info
# 1.0       2023    Initial Version
#
# ---------------------------------------------
from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from settings import LOGO
from src.business.send_payments._send_payments import send_payments
from src.telegram.keyboard.keyboards import Admin_keyb
from src.telegram.sendler.sendler import Sendler_msg


async def send_payments_state(message: Message, state: FSMContext):
    await Sendler_msg.log_client_message(message)

    summa = message.text.strip()

    keyboard = Admin_keyb().back_bets_menu()

    if not str(summa).isdigit():
        error_ = f'❌ Вы ввели не число, пожалуйста введите число'

        await Sendler_msg().sendler_photo_message(message, LOGO, error_, keyboard)

        return False

    await state.finish()

    res_send = await send_payments({"message": message, "summa": summa})

    _msg = f'✅ Рассылка выполнена\nСумма: {summa}\nПользователей: {res_send["sent"]}\n' \
           f'Успешных доставок:{res_send["total"]}\nОшибки: {res_send["failed"]}'

    await Sendler_msg().sendler_photo_message(message, LOGO, _msg, keyboard)

    return True
