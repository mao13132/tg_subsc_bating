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
from src.business.offers.offers_json import parse_id_users

CHANNEL_KEY = 'analytic_chat'


async def get_forecast_handler(message: Message, state: FSMContext):
    await Sendler_msg.log_client_message(message)

    await state.finish()

    id_user = message.chat.id

    id_channel = await BotDB.get_setting(CHANNEL_KEY)

    if not id_channel:
        await Sendler_msg.sendler_to_admin_mute(message,
                                                '❌Не установлен чат, на подписку которого проверяем, '
                                                'установите его в админ панели', None)

        return False

    subscription_checker = ChannelSubscriptionChecker(message.bot, id_channel)

    is_subscription = await subscription_checker.is_user_subscribed(id_user)

    if not is_subscription:
        error_ = await text_manager.get_message('no_subs')

        await Sendler_msg.send_msg_message(message, error_, None)

        logger_msg(f'Пользователь {message.chat.id} без подписки, нажимал кнопку "Получить прогноз"')

        return False

    update_user = await BotDB.edit_user('is_subs', True, id_user)

    back = await text_manager.get_button_text('back')

    user_data = await BotDB.get_user_bu_id_user(id_user)

    # Проверка на не оплаченный счёт
    # if await notify_unpaid_if_needed(call):
    #     return False

    offers = await BotDB.offers.read_by_filter({}) or []
    now = datetime.utcnow()
    try:
        offers = [o for o in offers if (getattr(o, 'expire_at', None) is None) or (getattr(o, 'expire_at') > now)]
        offers.sort(key=lambda o: getattr(o, 'created_at', now), reverse=True)
        offer = offers[0] if offers else None
    except Exception:
        offer = offers[0] if offers else None

    if not offer:
        no_load = await text_manager.get_message('no_load')
        await Sendler_msg.send_msg_message(message, no_load, Admin_keyb().back_main_menu(back))
        return True

    paid_list = parse_id_users(getattr(offer, 'paid_users', None))
    if str(id_user) in paid_list:
        no_load = await text_manager.get_message('already_paid_offer')
        await Sendler_msg.send_msg_message(message, no_load, Admin_keyb().back_main_menu(back))
        return True

    _msg_from_users = await text_manager.get_message('offer_send')
    get_offer_btn = await text_manager.get_button_text('get_offer')
    _msg_from_users = (_msg_from_users or '').format(summa=getattr(offer, 'summa', 0))

    back_text = await text_manager.get_button_text('back')

    keyboard = Admin_keyb().offers_client(offer_id=offer.id_pk, get_offer_btn=get_offer_btn, back_text=back_text,
                                          back_callback='over_state')

    await Sendler_msg.send_msg_message(message, _msg_from_users, keyboard)

    return True
