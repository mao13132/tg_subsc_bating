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


from src.business.channel_subscription.check_subscription import ChannelSubscriptionChecker
from src.telegram.keyboard.keyboards import Admin_keyb
from src.telegram.sendler.sendler import Sendler_msg
from src.utils.logger._logger import logger_msg


async def check_sub_call(call: types.CallbackQuery, state: FSMContext):
    try:
        target = str(call.data).split('-')[-1]
    except Exception as es:
        msg = f'Ошибка при запуске check_sub_call: {es}'
        logger_msg(msg)
        return False

    channel = text_manager.get_message(f"channel")
    invite_link = text_manager.get_message(f"invite_link")

    id_user = call.message.chat.id

    subscription_checker = ChannelSubscriptionChecker(call.bot, channel)

    is_subscription = await subscription_checker.is_user_subscribed(id_user)

    if not is_subscription:
        no_subscription_text = text_manager.get_message(f"no_subscription_{target}")

        link_btn = text_manager.get_button_text('link')
        check_btn = text_manager.get_button_text('check_subs')
        back_btn = text_manager.get_button_text('back')

        keyword = Admin_keyb().no_subs(link_btn, check_btn, back_btn, invite_link, target)
        await Sendler_msg.send_call_message(call, no_subscription_text, keyword)

        return False

    if target == 'gift':
        await gift_call(call, state)
    if target == 'write':
        await write_finish_call(call.message, state)

    return True
