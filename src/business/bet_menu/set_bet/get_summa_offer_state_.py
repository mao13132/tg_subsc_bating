from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from settings import States
from src.business.delete_old_msg.delete_old_msg_ import delete_old_msg
from src.telegram.keyboard.keyboards import Admin_keyb
from src.telegram.sendler.sendler import Sendler_msg


async def get_summa_offer_state(message: Message, state: FSMContext):
    await Sendler_msg.log_client_message(message)

    text_in = (message.text or '').strip()

    keyboard = Admin_keyb().back_bets_menu()

    if not text_in.isdigit():
        await Sendler_msg.send_msg_message(message, '❌ Напишите число (можно 0)', keyboard)
        return False

    data = await state.get_data()
    old_msg_id = data.get('old_msg_id')

    await state.update_data(summa=text_in)

    _q = '♻️ Переотправлять предложения?'
    keyb = Admin_keyb().repeat_offers_confirm()
    res = await Sendler_msg.send_msg_message(message, _q, keyb)

    await state.update_data(old_msg_id=res.message_id)

    await delete_old_msg(message, message.chat.id, old_msg_id)

    await States.confirm_repeat_offers.set()

    return True
    