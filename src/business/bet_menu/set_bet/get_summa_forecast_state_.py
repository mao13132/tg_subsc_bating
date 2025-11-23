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

from settings import LOGO, States
from src.business.delete_old_msg.delete_old_msg_ import delete_old_msg
from src.telegram.keyboard.keyboards import Admin_keyb
from src.telegram.sendler.sendler import Sendler_msg
from src.utils.datetime_parser import parse_user_datetime


async def get_summa_forecast_state(message: Message, state: FSMContext):
    await Sendler_msg.log_client_message(message)

    summa = message.text.strip()

    keyboard = Admin_keyb().back_bets_menu()

    if not str(summa).isdigit() or int(summa) <= 0:
        await Sendler_msg.send_msg_message(message, f'❌ Вы ввели не сумму, пожалуйста, напишите сумму', keyboard)
        return False

    data_state = await state.get_data()

    old_msg_id = data_state.get('old_msg_id', False)

    _msg = (
        '♻️ Введите дату и время, после которого прогноз удаляется\n\n'
        'Поддерживаемые варианты ввода:\n'
        '• 25.12.2025 14:30\n'
        '• 25.12 14:30 (год — текущий)\n'
        '• 2025-12-25 14:30\n'
        '• 14:30 25.12.2025\n'
        '• сегодня 09:00\n'
        '• завтра 09:00\n'
        '• через 30 мин\n'
        '• через 2 часа\n\n'
        '⚠️ Дата/время должны быть в будущем'
    )

    keyboard = Admin_keyb().back_bets_menu()

    res_send = await Sendler_msg.send_msg_message(message, _msg, keyboard)

    await state.update_data(summa=summa, old_msg_id=res_send.message_id)

    await delete_old_msg(message, message.chat.id, old_msg_id)

    await States.get_timer_bet.set()

    return True
