# ---------------------------------------------
# Program by @developer_telegrams
#
#
# Version   Date        Info
# 1.0       2023    Initial Version
#
# ---------------------------------------------
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

from settings import States
from src.telegram.keyboard.keyboards import Admin_keyb
from src.telegram.sendler.sendler import Sendler_msg


async def add_time_bet_call(call: types.CallbackQuery, state: FSMContext):
    await Sendler_msg.log_client_call(call)

    id_user = call.message.chat.id

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

    res_send = await Sendler_msg.send_msg_call(call, _msg, keyboard)

    await States.get_timer_bet.set()

    await state.update_data(old_msg_id=res_send.message_id)

    return True
