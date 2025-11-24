from aiogram import types
from aiogram.dispatcher import FSMContext

from src.telegram.sendler.sendler import Sendler_msg
from src.telegram.bot_core import BotDB
from src.telegram.keyboard.keyboards import Admin_keyb
from src.business.managers.check_manager import check_manager


async def users_stats_call(call: types.CallbackQuery, state: FSMContext):
    await Sendler_msg.log_client_call(call)

    await state.finish()

    stats = await BotDB.get_users_stats()

    total = stats.get('total', 0)
    is_subs = stats.get('is_subs', 0)
    need_paid = stats.get('need_paid', 0)
    send_payments = stats.get('send_payments', 0)
    received_forecast = stats.get('received_forecast', 0)
    wants_forecast = stats.get('wants_forecast', 0)

    msg = (
        f"📊 Статистика пользователей\n\n"
        f"Всего: {total}\n"
        f"Подписаны: {is_subs}\n"
        f"Должники: {need_paid}\n"
        f"Отмечено отправленных счетов: {send_payments}\n"
        f"Получили последний прогноз: {received_forecast}\n"
        f"Запросили прогноз: {wants_forecast}"
    )

    is_manager = await check_manager(call.message)
    keyboard = Admin_keyb().admin_keyboard(is_manager)

    await Sendler_msg.send_msg_call(call, msg, keyboard)

    return True
