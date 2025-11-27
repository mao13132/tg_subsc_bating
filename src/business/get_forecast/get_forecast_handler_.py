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

from src.business.text_manager.text_manager import text_manager
from src.telegram.keyboard.keyboards import Admin_keyb
from src.telegram.sendler.sendler import Sendler_msg

from src.telegram.bot_core import BotDB
from src.utils.logger._logger import logger_msg
from datetime import datetime
from src.business.offers.offers_json import parse_id_users, add_id_user
from src.business.access_checks import check_need_paid, ensure_subscription


async def get_forecast_handler(message: Message, state: FSMContext):
    """
    Обрабатывает нажатие «Получить прогноз».

    Алгоритм:
    1) Логирует событие и завершает текущее FSM-состояние.
    2) Получает id пользователя.
    3) Проверяет необходимость оплаты (если нужно — отправляет ссылку и завершает).
    4) Проверяет подписку (если нет — информирует и завершает).
    5) Отмечает желание клиента получить прогноз.
    6) Ищет актуальную мотивацию, формирует текст и клавиатуру.
    7) Отправляет сообщение пользователю и фиксирует его в мотивации.
    """
    # 1) Логирование и завершение состояния
    await Sendler_msg.log_client_message(message)

    await state.finish()

    # 2) Идентификатор пользователя
    id_user = message.chat.id

    data_user = await BotDB.get_user_bu_id_user(id_user)

    # 3) Проверка необходимости оплаты
    if await check_need_paid(message):
        return True

    # 4) Проверка подписки
    if not await ensure_subscription(message):
        return False

    # 5) Отмечаем желание клиента получить прогноз
    await BotDB.edit_user('wants_forecast', True, id_user)

    back = await text_manager.get_button_text('back')

    user_data = await BotDB.get_user_bu_id_user(id_user)

    # 7) Ищем актуальный оффер (не истёкший, последний)
    offers = await BotDB.offers.read_by_filter({}) or []
    now = datetime.utcnow()
    try:
        offers = [o for o in offers if (getattr(o, 'expire_at', None) is None) or (getattr(o, 'expire_at') > now)]
        offers.sort(key=lambda o: getattr(o, 'created_at', now), reverse=True)
        offer = offers[0] if offers else None
    except Exception:
        offer = offers[0] if offers else None

    # 9) Пользователь уже получал прогноз — сообщаем и выходим
    if offers:
        sends_list = parse_id_users(getattr(offer, 'id_users', None))
        if str(id_user) in sends_list:
            no_load = await text_manager.get_message('already_paid_offer')
            await Sendler_msg.send_msg_message(message, no_load, Admin_keyb().back_main_menu(back))
            return True

    motivations = await BotDB.motivations.read_by_filter({}) or []
    now = datetime.utcnow()
    try:
        motivations.sort(key=lambda m: getattr(m, 'created_at', now), reverse=True)
        motivation = motivations[0] if motivations else None
    except Exception:
        motivation = motivations[0] if motivations else None

    if not motivation:
        no_load = await text_manager.get_message('no_load')
        await Sendler_msg.send_msg_message(message, no_load, Admin_keyb().back_main_menu(back))

        return False

    tpl = await text_manager.get_message('motivation_main_text')
    text_out = (tpl or '').format(summa=int(getattr(motivation, 'summa', 0) or 0))

    user_get_offer = data_user.get_offer

    get_offer_btn = await text_manager.get_button_text('get_motivation')

    await Sendler_msg.send_msg_message(message, text_out, Admin_keyb().actual_motivation(back, get_offer_btn, user_get_offer))

    try:
        ids_json = add_id_user(getattr(motivation, 'id_users', None), id_user)
        await BotDB.motivations.update_by_id(int(getattr(motivation, 'id_pk')), {"id_users": ids_json})
    except Exception:
        pass

    try:
        await message.delete()
    except:
        pass

    # sent_ok = await send_offer_content_to_user(message.bot, int(id_user), int(getattr(offer, 'id_pk', 0)))
    # if sent_ok:
    #     ids_json = add_id_user(getattr(offer, 'id_users', None), id_user)
    #     await BotDB.offers.update_by_id(int(getattr(offer, 'id_pk', 0)), {"id_users": ids_json})
    #
    # try:
    #     await message.delete()
    # except:
    #     pass

    # await BotDB.edit_user('wants_forecast', False, id_user)
    # await BotDB.edit_user('received_forecast', True, id_user)

    return True
