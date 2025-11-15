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
from src.business.posts_manager.posts_states import PostsStates
from src.telegram.keyboard.keyboards import Admin_keyb
from src.telegram.sendler.sendler import Sendler_msg


async def set_bet_call(call: types.CallbackQuery, state: FSMContext):
    await state.finish()

    keyboard = Admin_keyb().back_bets_menu()

    _msg = f'♻ Добавьте сообщение с прогнозом'

    await Sendler_msg().sendler_photo_call(call, LOGO, _msg, keyboard)

    await PostsStates.waiting_new_post.set()

    return True

