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
from src.telegram.keyboard.keyboards import Admin_keyb
from src.telegram.sendler.sendler import Sendler_msg


async def send_payments_state(message: Message, state: FSMContext):
    await Sendler_msg.log_client_message(message)

    summa = message.text.strip()

    keyboard = Admin_keyb().back_bets_menu()

    if not str(summa).isdigit():
        error_ = f'❌ Вы ввели не число, пожалуйста введите число'

        await Sendler_msg.send_msg_message(message, error_, keyboard)

        return False

    elif 0 < int(summa) < 50:
        await Sendler_msg.send_msg_message(message, f'❌ Суммы меньше 50 рублей не поддерживает платежный провайдер',
                                           keyboard)

        return False

    text = f'⚠️ Подтверждаете действие?\n\nВы ввели сумму: <b>{summa}</b>\n\n' \
           f'Если сумма не верная, то пришлите ещё раз'

    keyboard = Admin_keyb().approve_send_summa()

    await message.reply(text, reply_markup=keyboard)

    await state.update_data(summa=summa)

    return True
