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

from src.business.channel_subscription.check_subscription import ChannelSubscriptionChecker
from src.business.text_manager.text_manager import text_manager
from src.telegram.keyboard.keyboards import Admin_keyb
from src.telegram.sendler.sendler import Sendler_msg

from src.telegram.bot_core import BotDB
from src.utils.logger._logger import logger_msg
from datetime import datetime
from src.business.offers.offers_json import parse_id_users, add_id_user
from src.business.payments.payment_service import ensure_payment_link

CHANNEL_KEY = 'analytic_chat'


async def get_forecast_handler(message: Message, state: FSMContext):
    """
    Обрабатывает нажатие «Получить прогноз».

    Алгоритм:
    1) Логирует событие и завершает текущее FSM-состояние.
    2) Получает id пользователя и id канала проверки.
    3) Если канал не задан — уведомляет админа и завершается.
    4) Проверяет подписку пользователя на канал.
    5) При отсутствии подписки — информирует пользователя и завершается.
    6) Отмечает пользователя как подписанного в БД.
    7) Получает актуальный оффер (не истёкший, самый свежий).
    8) При отсутствии оффера — отправляет сообщение и завершается.
    9) Проверяет, что пользователь не числится как оплативший оффер.
    10) Отправляет упакованный контент оффера пользователю.
    11) Отправляет сообщение с кнопкой получения оффера.
    """
    # 1) Логирование и завершение состояния
    await Sendler_msg.log_client_message(message)

    await state.finish()

    # 2) Идентификаторы пользователя и канала
    id_user = message.chat.id

    data_user = await BotDB.get_user_bu_id_user(id_user)

    if data_user.need_paid:
        template = await text_manager.get_message('no_paid_msg')
        btn_text = await text_manager.get_button_text('paid')
        result = await ensure_payment_link(str(id_user))
        link_payment = result.get('link')
        amount = int(result.get('amount') or 0)
        if link_payment:
            keyboard = Admin_keyb().payment_keyb(btn_text, link_payment)
            text_msg = (template or '').format(summa=amount, link=link_payment)
            await Sendler_msg.send_msg_message(message, text_msg, keyboard)
            return True
        else:
            await Sendler_msg.send_msg_message(message, template or 'Ссылка на оплату недоступна', None)
            return True

    id_channel = await BotDB.get_setting(CHANNEL_KEY)

    # 3) Нет канала — предупреждение админам и выход
    if not id_channel:
        await Sendler_msg.sendler_to_admin_mute(message,
                                                '❌Не установлен чат, на подписку которого проверяем, '
                                                'установите его в админ панели', None)

        return False

    # 4) Проверка подписки на канал
    subscription_checker = ChannelSubscriptionChecker(message.bot, id_channel)

    is_subscription = await subscription_checker.is_user_subscribed(id_user)

    # 5) Нет подписки — информируем и выходим
    if not is_subscription:
        error_ = await text_manager.get_message('no_subs')

        await Sendler_msg.send_msg_message(message, error_, None)

        logger_msg(f'Пользователь {message.chat.id} без подписки, нажимал кнопку "Получить прогноз"')

        return False

    # 6) Отмечаем пользователя подписанным
    update_user = await BotDB.edit_user('is_subs', True, id_user)

    # 6.1) Отмечаем желание клиента получить прогноз
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
