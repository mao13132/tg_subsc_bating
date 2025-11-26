from aiogram import types
from aiogram.dispatcher import FSMContext

from settings import States
from src.telegram.keyboard.keyboards import Admin_keyb
from src.telegram.sendler.sendler import Sendler_msg


async def start_summa_offer_call(call: types.CallbackQuery, state: FSMContext):
    await Sendler_msg.log_client_call(call)

    keyboard = Admin_keyb().back_bets_menu()

    _msg = '♻️ Введите стоимость прогноза (можно 0)'

    res_send = await Sendler_msg.send_msg_call(call, _msg, keyboard)

    await States.get_summa_offer.set()

    await state.update_data(old_msg_id=res_send.message_id)

    return True
    