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
from src.business.delete_old_msg.delete_old_msg_ import delete_old_msg
from src.telegram.keyboard.keyboards import Admin_keyb
from src.telegram.sendler.sendler import Sendler_msg
from src.utils.datetime_parser import parse_user_datetime


async def get_timer_bet_state(message: Message, state: FSMContext):
    await Sendler_msg.log_client_message(message)

    date_in = message.text.strip()

    keyboard = Admin_keyb().back_bets_menu()

    parsed = parse_user_datetime(date_in)

    data_state = await state.get_data()

    old_msg_id = data_state.get('old_msg_id', False)

    if not parsed['ok']:
        await Sendler_msg.send_msg_message(message, parsed['error'], keyboard)
        return False

    dt_str = parsed['dt_str']

    text = (
        f'⚠️ Подтверждаете действие?\n\n'
        f'Дата удаления прогноза: <b>{dt_str}</b>\n\n'
        f'Если дата не верная, пришлите ещё раз'
    )

    keyboard = Admin_keyb().finish_timer_bet()

    await message.reply(text, reply_markup=keyboard)

    await state.update_data(timer_bet_dt_iso=parsed['dt'].isoformat(), timer_bet_dt_str=dt_str)

    await delete_old_msg(message, message.chat.id, old_msg_id)

    return True
