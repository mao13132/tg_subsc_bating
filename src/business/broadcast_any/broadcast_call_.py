from aiogram import types
from aiogram.dispatcher import FSMContext

from settings import LOGO
from src.telegram.sendler.sendler import Sendler_msg
from src.business.broadcast_any.broadcast_keyboard import BroadcastKeyb


async def broadcast_any_call(call: types.CallbackQuery, state: FSMContext):
    await Sendler_msg.log_client_call(call)

    await state.finish()

    _msg = '♻ Добавьте сообщения для рассылки'

    keyb = BroadcastKeyb.collect_messages_keyb()

    await Sendler_msg().sendler_photo_call(call, LOGO, _msg, keyb)

    from src.business.broadcast_any.broadcast_states import BroadcastStates
    await BroadcastStates.waiting_broadcast.set()

    return True
