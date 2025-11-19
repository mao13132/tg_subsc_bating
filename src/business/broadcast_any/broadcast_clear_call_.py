from aiogram import types
from aiogram.dispatcher import FSMContext

from settings import LOGO
from src.telegram.sendler.sendler import Sendler_msg
from src.business.broadcast_any.broadcast_keyboard import BroadcastKeyb
from src.business.broadcast_any.broadcast_state_ import BROADCAST_ITEMS


async def broadcast_clear_call(call: types.CallbackQuery, state: FSMContext):
    await Sendler_msg.log_client_call(call)

    id_user = call.message.chat.id

    BROADCAST_ITEMS.pop(id_user, None)
    await state.update_data(collect_count=0, mg_counters={})

    keyb = BroadcastKeyb.collect_messages_keyb()

    _msg = '✅ Очередь очищена'

    await Sendler_msg().sendler_photo_call(call, LOGO, _msg, keyb)

    return True
    