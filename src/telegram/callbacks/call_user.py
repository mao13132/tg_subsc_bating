from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext

from settings import LOGO
from src.business.bet_menu.bet_menu_call_ import bet_menu_call
from src.business.bet_menu.clear_bet.clear_bet_call_ import clear_bet_call
from src.business.bet_menu.send_me_bet.send_me_bet_call_ import send_me_bet_call
from src.business.bet_menu.set_bet.set_bet_call_ import set_bet_call
from src.business.chat_admin.add_chat_admin_call_ import add_chat_admin_call
from src.business.chat_admin.chat_admin_call_ import chat_admin_call
from src.business.get_forecast.get_forecast_call_ import get_forecast_call
from src.business.logo.logo_change_call_ import logo_change_call
from src.business.managers.add_managers_call import add_managers_call
from src.business.managers.check_manager import check_manager
from src.business.managers.managers_call import managers_call
from src.business.posts_manager.finish_get_posts_call_ import finish_get_posts_call
from src.business.repid_payments.repid_payments_call_ import repid_payments_call
from src.business.send_forecast.approve_forecast_call_ import approve_forecast_call
from src.business.send_forecast.send_forecast_call_ import send_forecast_call
from src.business.send_payments.approve_summa_call_ import approve_summa_call
from src.business.send_payments.send_payments_call_ import send_payments_call
from src.business.start_one.start_one import start_one
from src.business.text_edit.edit_text_call import edit_text_button_call, edit_text_message_call
from src.business.text_edit.text_keyboards_call import text_keyboards_call
from src.business.text_edit.text_msg_call import text_msg_call
from src.telegram.sendler.sendler import *

from src.telegram.keyboard.keyboards import *


async def over_state(call: types.CallbackQuery, state: FSMContext):
    await Sendler_msg.log_client_call(call)

    await state.finish()

    await Sendler_msg.log_client_call(call)

    await start_one(call.message, state)

    return True


async def admin_panel(call: types.CallbackQuery):
    await Sendler_msg.log_client_call(call)

    is_manager = await check_manager(call.message)

    keyb = Admin_keyb().admin_keyboard(is_manager)

    text_admin = 'Панель управления'

    await Sendler_msg().sendler_photo_call(call, LOGO, text_admin, keyb)

    return True


def register_callbacks(dp: Dispatcher):
    dp.register_callback_query_handler(managers_call, text='managers', state='*')

    dp.register_callback_query_handler(add_managers_call, text='add_managers', state='*')

    dp.register_callback_query_handler(over_state, text='over_state', state='*')

    dp.register_callback_query_handler(admin_panel, text_contains='admin_panel', state='*')

    dp.register_callback_query_handler(text_keyboards_call, text='text_keyboards', state='*')
    dp.register_callback_query_handler(text_msg_call, text='text_msg', state='*')
    dp.register_callback_query_handler(edit_text_button_call, text_contains='edit_text_button-', state='*')
    dp.register_callback_query_handler(edit_text_message_call, text_contains='edit_text_message-', state='*')

    dp.register_callback_query_handler(add_chat_admin_call, text_contains='admin_chat-', state='*')

    dp.register_callback_query_handler(chat_admin_call, text='chat_admin_call', state='*')

    dp.register_callback_query_handler(get_forecast_call, text='get_forecast', state='*')

    dp.register_callback_query_handler(logo_change_call, text='logo_change_call', state='*')

    dp.register_callback_query_handler(bet_menu_call, text='bet_menu', state='*')

    dp.register_callback_query_handler(set_bet_call, text='set_bet', state='*')

    dp.register_callback_query_handler(finish_get_posts_call, text='send_user_messages', state='*')

    dp.register_callback_query_handler(clear_bet_call, text='clear_bet', state='*')

    dp.register_callback_query_handler(send_me_bet_call, text='send_me_bet', state='*')

    dp.register_callback_query_handler(send_payments_call, text='send_payments', state='*')

    dp.register_callback_query_handler(approve_summa_call, text='approve_summa', state='*')

    dp.register_callback_query_handler(send_forecast_call, text='send_forecast', state='*')

    dp.register_callback_query_handler(approve_forecast_call, text='approve_forecast', state='*')

    dp.register_callback_query_handler(repid_payments_call, text='repid_payments', state='*')
