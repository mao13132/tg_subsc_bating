from aiogram import Dispatcher, types

from settings import States, EditTextState
from src.business.users.users_search_state_ import users_search_state
from src.business.bet_menu.set_bet.get_summa_forecast_state_ import get_summa_forecast_state
from src.business.bet_menu.set_bet.get_timer_bet_state_ import get_timer_bet_state
from src.business.bet_menu.set_bet.get_summa_offer_state_ import get_summa_offer_state
from src.business.logo.logo_states import EditLogoStates
from src.business.logo.change_logo_state_ import change_logo_state
from src.business.chat_admin.add_chat_admin_state_ import add_chat_admin_state
from src.business.managers.add_manager_state import add_manager_state
from src.business.motivation.build_motivation_state_ import build_motivation_state
from src.business.posts_manager.posts_state_ import posts_state
from src.business.posts_manager.posts_states import PostsStates
from src.business.send_payments.send_payments_state_ import send_payments_state
from src.business.text_edit.edit_text_handler import handle_new_text
from src.business.broadcast_any.broadcast_state_ import broadcast_state
from src.business.broadcast_any.broadcast_states import BroadcastStates


def register_state(dp: Dispatcher):
    dp.register_message_handler(add_manager_state, state=States.add_manager)

    dp.register_message_handler(handle_new_text, state=EditTextState.waiting_new_text, content_types=['text'])

    dp.register_message_handler(add_chat_admin_state, state=States.add_admin_chat)

    dp.register_message_handler(send_payments_state, state=States.write_summa)

    dp.register_message_handler(get_summa_forecast_state, state=States.get_summa_forecast)

    dp.register_message_handler(get_timer_bet_state, state=States.get_timer_bet)

    dp.register_message_handler(get_summa_offer_state, state=States.get_summa_offer)

    dp.register_message_handler(build_motivation_state, state=States.get_summa_motivation)

    dp.register_message_handler(change_logo_state, state=EditLogoStates.chane_logo, content_types=['photo'])

    dp.register_message_handler(posts_state, state=PostsStates.waiting_new_post, content_types=[types.ContentType.ANY])

    dp.register_message_handler(broadcast_state, state=BroadcastStates.waiting_broadcast, content_types=[types.ContentType.ANY])

    dp.register_message_handler(users_search_state, state=States.find_user, content_types=['text'])
