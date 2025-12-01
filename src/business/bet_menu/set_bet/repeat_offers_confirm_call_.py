from datetime import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext

from src.business.repid_motivations.repid_motivations_call_ import repid_motivations_call
from src.telegram.sendler.sendler import Sendler_msg
from src.business.bet_menu.set_bet.finish_timer_bet_call_ import finish_timer_bet_call
from src.utils.logger._logger import logger_msg

from src.telegram.bot_core import BotDB


async def repeat_offers_confirm_call(call: types.CallbackQuery, state: FSMContext):
    await Sendler_msg.log_client_call(call)

    try:
        response = str(call.data).split('-')[-1]
    except Exception as es:
        msg = f'Ошибка при запуске repeat_offers_confirm_call: {es}'
        logger_msg(msg)
        return False

    state_data = await state.get_data()

    summa = state_data.get('summa', False)

    motivations = await BotDB.motivations.read_by_filter({}) or []
    if not motivations:
        try:
            sum_int = int(str(summa)) if str(summa).isdigit() else 0
            await BotDB.motivations.create({"summa": sum_int, "id_users": None})
        except Exception as es:
            logger_msg(f"Create motivation error: {es}")

    await state.update_data(resend_motivation=response)

    # Идёт вветку переотправки, там же обновим сумму
    if str(response) == 'yes':
        await repid_motivations_call(call, state, resend_from_create_offer=True, new_summa=summa)
    else:
        # Если не пересоздавать, то обновим сумму на всякий.
        motivations = await BotDB.motivations.read_by_filter({}) or []
        try:
            motivations.sort(key=lambda m: getattr(m, 'created_at', datetime.utcnow()), reverse=True)
            motivation = motivations[0] if motivations else None
        except Exception:
            motivation = motivations[0] if motivations else None

        if motivation:
            await BotDB.motivations.update_by_id(int(getattr(motivation, 'id_pk')), {"summa": int(summa)})

    await finish_timer_bet_call(call, state)

    return True
