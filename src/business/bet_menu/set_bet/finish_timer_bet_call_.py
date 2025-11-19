from aiogram import types
from aiogram.dispatcher import FSMContext

from settings import LOGO
from src.telegram.keyboard.keyboards import Admin_keyb
from src.telegram.sendler.sendler import Sendler_msg
from src.telegram.bot_core import BotDB
from datetime import datetime
from src.business.send_forecast._send_forecast import send_forecast_broadcast


async def finish_timer_bet_call(call: types.CallbackQuery, state: FSMContext):
    await Sendler_msg.log_client_call(call)

    id_user = call.message.chat.id

    data = await state.get_data()
    batch_key = data.get('batch_key')
    dt_iso = data.get('timer_bet_dt_iso')
    dt_str = data.get('timer_bet_dt_str')

    await BotDB.user_messages.delete_not_batch_key(id_user, batch_key)

    if dt_iso:
        dt = datetime.fromisoformat(str(dt_iso))
        await BotDB.user_messages.set_expire_by_batch_key(id_user, batch_key, dt)
        if not dt_str:
            dt_str = dt.strftime('%d.%m.%Y %H:%M')

    await state.finish()

    keyboard = Admin_keyb().back_bets_menu()

    forecast_message = await BotDB.user_messages.read_by_filter({})

    if not forecast_message:
        keyboard = Admin_keyb().new_back_bets_menu()
        no_load = f'❌ Прогноз не загружен'
        await Sendler_msg.send_msg_call(call, no_load, keyboard)
        return True

    await BotDB.bulk_update_users_by_filter({}, {"received_forecast": False})

    res_send = await send_forecast_broadcast({"message": call.message, "messages": forecast_message})

    # После рассылки отмечаем только тех, кому успешно доставлено
    ok_ids = res_send.get("ok_ids") or []
    if ok_ids:
        await BotDB.set_received_forecast_for_ids(ok_ids, True)

    _msg = (
        f'✅ Рассылка выполнена\nПользователей: {res_send["sent"]}\n'
        f'Успешных доставок:{res_send["total"]}\nОшибки: {res_send["failed"]}\n'
        f'🗓 Дата удаления прогноза: {dt_str or "не задана"}'
    )

    await Sendler_msg.send_msg_message(call.message, _msg, keyboard)

    return True
