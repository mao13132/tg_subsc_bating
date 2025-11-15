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

from settings import LOGO
from src.business.channel_subscription.check_subscription import ChannelSubscriptionChecker
from src.business.text_manager.text_manager import text_manager
from src.telegram.sendler.sendler import Sendler_msg

from src.telegram.bot_core import BotDB
from src.utils.logger._logger import logger_msg

CHANNEL_KEY = 'analytic_chat'


async def get_forecast_call(call: types.CallbackQuery, state: FSMContext):
    # await Sendler_msg.log_client_call(call)

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

    await call.answer('Подписан', show_alert=True)



