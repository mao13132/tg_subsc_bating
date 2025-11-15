# ---------------------------------------------
# Program by @developer_telegrams
#
#
# Version   Date        Info
# 1.0       2023    Initial Version
#
# ---------------------------------------------
from aiogram.dispatcher.filters.state import StatesGroup, State


class PostsStates(StatesGroup):
    waiting_new_post = State()
