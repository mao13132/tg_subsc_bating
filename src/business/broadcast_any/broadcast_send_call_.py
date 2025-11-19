from aiogram import types
from aiogram.dispatcher import FSMContext

from settings import LOGO
from src.telegram.sendler.sendler import Sendler_msg
from src.business.broadcast_any.broadcast_keyboard import BroadcastKeyb
from src.business.broadcast_any.broadcast_state_ import BROADCAST_ITEMS, _broadcast_records


async def broadcast_send_call(call: types.CallbackQuery, state: FSMContext):
    await Sendler_msg.log_client_call(call)

    id_user = call.message.chat.id

    records = BROADCAST_ITEMS.get(id_user) or []

    keyb = BroadcastKeyb.back_admin()

    if not records:
        _msg = '❌ Очередь пуста'
        await Sendler_msg.send_msg_call(call, _msg, keyb)
        return True

    await state.finish()

    try:
        res = await _broadcast_records(call.message.bot, records)
    except:
        res = {"total": 0, "sent": 0, "failed": 0}

    _msg = f'✅ Рассылка выполнена\nПользователей: {res["sent"]}\nУспешных доставок:{res["total"]}\nОшибки: {res["failed"]}'

    try:
        BROADCAST_ITEMS.pop(id_user, None)
    except:
        pass

    await Sendler_msg.send_msg_call(call, _msg, keyb)

    return True
    