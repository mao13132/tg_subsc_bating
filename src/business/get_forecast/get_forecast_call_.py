# ---------------------------------------------
# Program by @developer_telegrams
#
#
# Version   Date        Info
# 1.0       2023    Initial Version
#
# ---------------------------------------------
from aiogram import types
from aiogram.dispatcher import FSMContext

from settings import LOGO, ADMIN
from src.business.channel_subscription.check_subscription import ChannelSubscriptionChecker
from src.business.get_forecast.send_forecast_ import send_forecast
from src.business.text_manager.text_manager import text_manager
from src.telegram.keyboard.keyboards import Admin_keyb
from src.telegram.sendler.sendler import Sendler_msg

from src.telegram.bot_core import BotDB
from src.utils.logger._logger import logger_msg

CHANNEL_KEY = 'analytic_chat'


async def get_forecast_call(call: types.CallbackQuery, state: FSMContext):
    await Sendler_msg.log_client_call(call)

    await state.finish()

    id_user = call.message.chat.id

    id_channel = await BotDB.get_setting(CHANNEL_KEY)

    if not id_channel:
        await Sendler_msg.sendler_to_admin_mute(call.message,
                                                '❌Не установлен чат, на подписку которого проверяем, '
                                                'установите его в админ панели', None)

        return False

    subscription_checker = ChannelSubscriptionChecker(call.bot, id_channel)

    is_subscription = await subscription_checker.is_user_subscribed(id_user)

    if not is_subscription:
        error_ = await text_manager.get_message('no_subs')

        await Sendler_msg().sendler_photo_call(call, LOGO, error_, None)

        logger_msg(f'Пользователь {call.message.chat.id} без подписки, нажимал кнопку "Получить прогноз"')

        return False

    update_user = await BotDB.edit_user('is_subs', True, id_user)

    back = await text_manager.get_button_text('back')

    user_data = await BotDB.get_user_bu_id_user(id_user)

    if user_data.need_paid:
        payment = await BotDB.payments.read_latest_by_user(str(id_user))
        link = getattr(payment, 'link', None) if payment else None
        summa = getattr(payment, 'amount', None) if payment else None

        no_paid_msg = await text_manager.get_message('no_paid_msg')

        no_paid_msg = no_paid_msg.format(summa=summa, link=link)

        paid_text = await text_manager.get_button_text('paid')

        keyboard = Admin_keyb().no_paid(back, paid_text, link)

        await Sendler_msg().sendler_photo_call(call, LOGO, no_paid_msg, keyboard)

        return False

    keyboard = Admin_keyb().back_main_menu(back)

    forecast_message = await BotDB.user_messages.read_by_filter({})

    if not forecast_message:
        no_load = await text_manager.get_message('no_load')

        await Sendler_msg().sendler_photo_call(call, LOGO, no_load, keyboard)

        return True

    res_send = await send_forecast({'message': call.message, "messages": forecast_message})

    res_update_user = await BotDB.edit_user('need_paid', True, id_user)

    return True
