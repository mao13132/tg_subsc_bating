from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from settings import States

from src.business.bet_menu.bet_menu_call_ import bet_menu_call
from src.business.bet_menu.clear_bet.clear_bet_call_ import clear_bet_call
from src.business.bet_menu.send_me_bet.send_me_bet_call_ import send_me_bet_call
from src.business.bet_menu.set_bet.add_timer_bet_call_ import add_time_bet_call
from src.business.bet_menu.set_bet.set_bet_call_ import set_bet_call
from src.business.chat_admin.add_chat_admin_call_ import add_chat_admin_call
from src.business.chat_admin.chat_admin_call_ import chat_admin_call
from src.business.get_forecast.get_forecast_call_ import get_forecast_call
from src.business.get_offer_client.get_offer_client_call_ import get_offer_client_call
from src.business.logo.logo_change_call_ import logo_change_call
from src.business.managers.add_managers_call import add_managers_call
from src.business.managers.check_manager import check_manager
from src.business.managers.managers_call import managers_call
from src.business.motivation.build_motivation_call_ import build_motivation_call
from src.business.repid_motivations.repid_motivations_call_ import repid_motivations_call
from src.business.send_forecast.approve_forecast_call_ import approve_forecast_call
from src.business.send_forecast.send_forecast_call_ import send_forecast_call
from src.business.send_payments.approve_summa_call_ import approve_summa_call
from src.business.bet_menu.set_bet.start_summa_offer_call_ import start_summa_offer_call
from src.business.bet_menu.set_bet.repeat_offers_confirm_call_ import repeat_offers_confirm_call
from src.business.send_payments.send_payments_call_ import send_payments_call
from src.business.payments.repeat_old_payments_call_ import repeat_old_payments_call
from src.business.payments.create_payment_call_ import create_payment_call, pay_other_call, back_payment_choose_call
from src.business.start_one.start_one import start_one
from src.business.text_edit.edit_text_call import edit_text_button_call, edit_text_message_call
from src.business.text_edit.text_keyboards_call import text_keyboards_call
from src.business.text_edit.text_msg_call import text_msg_call
from src.business.users.users_call_ import users_call, users_find_call, users_find_list_call
from src.business.users.user_item_call_ import user_item_call
from src.business.users.user_reset_call_ import user_reset_all_call, user_reset_bill_call
from src.telegram.sendler.sendler import *

from src.telegram.keyboard.keyboards import *
from src.business.broadcast_any.broadcast_call_ import broadcast_any_call
from src.business.broadcast_any.broadcast_send_call_ import broadcast_send_call
from src.business.broadcast_any.broadcast_clear_call_ import broadcast_clear_call
from src.business.users_stats.users_stats_call_ import users_stats_call


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

    await Sendler_msg.send_msg_call(call, text_admin, keyb)

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

    dp.register_callback_query_handler(get_forecast_call, text_contains='get_forecast', state='*')

    dp.register_callback_query_handler(logo_change_call, text='logo_change_call', state='*')

    dp.register_callback_query_handler(bet_menu_call, text='bet_menu', state='*')

    dp.register_callback_query_handler(set_bet_call, text='set_bet', state='*')

    dp.register_callback_query_handler(add_time_bet_call, text='send_user_messages', state='*')
    # dp.register_callback_query_handler(add_summa_bet_call, text='send_user_messages', state='*')

    dp.register_callback_query_handler(broadcast_any_call, text='broadcast_any', state='*')
    dp.register_callback_query_handler(broadcast_send_call, text='broadcast_send', state='*')
    dp.register_callback_query_handler(broadcast_clear_call, text='broadcast_clear', state='*')

    dp.register_callback_query_handler(clear_bet_call, text='clear_bet', state='*')

    dp.register_callback_query_handler(send_me_bet_call, text='send_me_bet', state='*')

    dp.register_callback_query_handler(send_payments_call, text='send_payments', state='*')
    dp.register_callback_query_handler(repeat_old_payments_call, text='repeat_old_payments', state='*')
    dp.register_callback_query_handler(users_stats_call, text='users_stats', state='*')

    dp.register_callback_query_handler(approve_summa_call, text='approve_summa', state='*')
    dp.register_callback_query_handler(start_summa_offer_call, text='approve_timer_bet', state='*')

    dp.register_callback_query_handler(send_forecast_call, text='send_forecast', state='*')

    dp.register_callback_query_handler(approve_forecast_call, text='approve_forecast', state='*')

    dp.register_callback_query_handler(repid_motivations_call, text='repid_motivations', state='*')

    dp.register_callback_query_handler(repeat_offers_confirm_call, text_contains='repeat_offers', state=States.confirm_repeat_offers)

    dp.register_callback_query_handler(get_offer_client_call, text='get_offer_client', state='*')

    # dp.register_callback_query_handler(get_offer_call, text_contains='get_offer-', state='*')

    dp.register_callback_query_handler(build_motivation_call, text='motivation', state='*')

    dp.register_callback_query_handler(create_payment_call, text_contains='create_payment-', state='*')
    dp.register_callback_query_handler(pay_other_call, text='pay_other', state='*')
    dp.register_callback_query_handler(back_payment_choose_call, text_contains='back_payment_choose-', state='*')

    dp.register_callback_query_handler(users_call, text='users', state='*')
    dp.register_callback_query_handler(users_call, text_contains='users_list-', state='*')
    dp.register_callback_query_handler(users_find_call, text='users_find', state='*')
    dp.register_callback_query_handler(users_find_list_call, text_contains='users_find_list-', state='*')
    dp.register_callback_query_handler(user_item_call, text_contains='user_item-', state='*')
    dp.register_callback_query_handler(user_reset_all_call, text_contains='user_reset_all-', state='*')
    dp.register_callback_query_handler(user_reset_bill_call, text_contains='user_reset_bill-', state='*')
