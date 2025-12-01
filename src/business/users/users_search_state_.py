from aiogram import types
from aiogram.dispatcher import FSMContext

from src.telegram.sendler.sendler import Sendler_msg
from src.telegram.bot_core import BotDB
from src.business.users.users_call_ import set_search_results, build_search_results_keyboard

USERS_PER_PAGE = 10


async def users_search_state(message: types.Message, state: FSMContext):
    await Sendler_msg.log_client_message(message)
    query_text = (message.text or '').strip()
    matched_users = await BotDB.search_users(query_text)
    set_search_results(message.chat.id, matched_users)

    current_page = 1
    keyb = build_search_results_keyboard(matched_users, current_page, USERS_PER_PAGE)
    total = len(matched_users)
    pages = max(1, (total + USERS_PER_PAGE - 1) // USERS_PER_PAGE)
    text = (
        f'🔎 Поиск пользователей\n'
        f'Запрос: {query_text}\n'
        f'Найдено: {total}\n'
        f'Страница: {current_page}/{pages}'
    )
    await state.finish()
    await Sendler_msg.send_msg_message(message, text, keyb)
    return True
    