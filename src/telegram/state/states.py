from aiogram import Dispatcher, types

from settings import States, EditTextState
from src.business.logo.logo_states import EditLogoStates
from src.business.logo.change_logo_state_ import change_logo_state
from src.business.chat_admin.add_chat_admin_state_ import add_chat_admin_state
from src.business.managers.add_manager_state import add_manager_state
from src.business.posts_manager.posts_state_ import posts_state
from src.business.posts_manager.posts_states import PostsStates
from src.business.text_edit.edit_text_handler import handle_new_text


def register_state(dp: Dispatcher):
    dp.register_message_handler(add_manager_state, state=States.add_manager)

    dp.register_message_handler(handle_new_text, state=EditTextState.waiting_new_text, content_types=['text'])

    dp.register_message_handler(add_chat_admin_state, state=States.add_admin_chat)

    dp.register_message_handler(change_logo_state, state=EditLogoStates.chane_logo, content_types=['photo'])

    dp.register_message_handler(posts_state, state=PostsStates.waiting_new_post, content_types=[types.ContentType.ANY])
