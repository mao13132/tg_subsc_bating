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
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.telegram.sendler.sendler import Sendler_msg
from src.telegram.bot_core import BotDB
from settings import States

# Хранилище результатов поиска для каждого администратора
SEARCH_RESULTS_BY_ADMIN = {}

def set_search_results(admin_chat_id: int, users_list):
    SEARCH_RESULTS_BY_ADMIN[int(admin_chat_id)] = users_list or []

def get_search_results(admin_chat_id: int):
    return SEARCH_RESULTS_BY_ADMIN.get(int(admin_chat_id), [])


# Параметры пагинации списка пользователей
USERS_PER_PAGE = 10


def build_users_keyboard(users_list, current_page: int, items_per_page: int) -> InlineKeyboardMarkup:
    """
    Генерация клавиатуры со списком пользователей и навигацией.

    Элемент: "user_item-<id_user>"
    Листание: "users_list-<page>"
    Назад: "admin_panel"
    """
    total_users = len(users_list)
    total_pages = max(1, (total_users + items_per_page - 1) // items_per_page)
    current_page = min(max(1, current_page), total_pages)

    start_index = (current_page - 1) * items_per_page
    end_index = start_index + items_per_page
    sorted_users = sorted(users_list, key=lambda u: getattr(u, 'id_pk', 0))
    page_users = sorted_users[start_index:end_index]

    keyboard = InlineKeyboardMarkup(row_width=1)

    # Кнопки пользователей: показываем имя/логин или id
    for idx, user in enumerate(page_users, 1):
        user_id = getattr(user, 'id_user', None)
        if not user_id:
            continue
        first_name = getattr(user, 'first_name', '') or ''
        last_name = getattr(user, 'last_name', '') or ''
        login = getattr(user, 'login', '') or ''
        title = (f"{first_name} {last_name}" if (first_name or last_name) else login) or f"ID: {user_id}"
        display_index = start_index + idx
        keyboard.add(InlineKeyboardButton(text=f"{display_index}. {title.strip()}", callback_data=f'user_item-{user_id}-{current_page}'))

    # Кнопки номеров страниц с сокращением через "..." и последней страницей
    def _page_buttons(total_pages: int, current_page_number: int):
        buttons = []

        if total_pages <= 6:
            for p in range(1, total_pages + 1):
                label = f'•{p}•' if p == current_page_number else str(p)
                buttons.append(InlineKeyboardButton(text=label, callback_data=f'users_list-{p}'))
            return buttons

        # Всегда показываем первую и последнюю
        first_label = f'•1•' if current_page_number == 1 else '1'
        buttons.append(InlineKeyboardButton(text=first_label, callback_data='users_list-1'))

        # Левая часть: соседи вокруг текущей
        left = max(2, current_page_number - 1)
        right = min(total_pages - 1, current_page_number + 1)

        # Эллипсис после первой, если есть большой разрыв
        if left > 2:
            buttons.append(InlineKeyboardButton(text='...', callback_data='noop'))

        for p in range(left, right + 1):
            label = f'•{p}•' if p == current_page_number else str(p)
            buttons.append(InlineKeyboardButton(text=label, callback_data=f'users_list-{p}'))

        # Эллипсис перед последней, если есть большой разрыв
        if right < total_pages - 1:
            buttons.append(InlineKeyboardButton(text='...', callback_data='noop'))

        last_label = f'•{total_pages}•' if current_page_number == total_pages else str(total_pages)
        buttons.append(InlineKeyboardButton(text=last_label, callback_data=f'users_list-{total_pages}'))

        return buttons

    page_buttons = _page_buttons(total_pages, current_page)
    if page_buttons:
        keyboard.row(*page_buttons)

    # Стрелки навигации
    navigation_buttons = []
    if total_pages > 1:
        if current_page > 1:
            navigation_buttons.append(InlineKeyboardButton(text='⬅️ Назад', callback_data=f'users_list-{current_page - 1}'))
        if current_page < total_pages:
            navigation_buttons.append(InlineKeyboardButton(text='➡️ Далее', callback_data=f'users_list-{current_page + 1}'))
    if navigation_buttons:
        keyboard.row(*navigation_buttons)

    keyboard.add(InlineKeyboardButton(text='🔎 Поиск', callback_data='users_find'))
    keyboard.add(InlineKeyboardButton(text='🔙 Назад', callback_data='admin_panel'))

    return keyboard


async def users_call(call: types.CallbackQuery, state: FSMContext):
    """
    Отображает список пользователей с пагинацией.

    Обрабатывает:
    - "users" — первая страница
    - "users_list-<page>" — переход между страницами
    """
    await Sendler_msg.log_client_call(call)

    try:
        # Парсим страницу из колбэка
        callback_data = str(call.data or '')
        current_page = 1
        if 'users_list-' in callback_data:
            try:
                current_page = int(callback_data.split('users_list-')[-1])
            except Exception:
                current_page = 1

        # Загружаем пользователей
        all_users = await BotDB.get_users_by_filter({}) or []

        # Собираем клавиатуру
        keyb = build_users_keyboard(all_users, current_page, USERS_PER_PAGE)

        # Текст сообщения
        total_users = len(all_users)
        total_pages = max(1, (total_users + USERS_PER_PAGE - 1) // USERS_PER_PAGE)
        text = (
            f"👥 Пользователи\n"
            f"Всего: {total_users}\n"
            f"Страница: {min(max(1, current_page), total_pages)}/{total_pages}\n\n"
            f"Выберите пользователя:"
        )

        await Sendler_msg.send_msg_call(call, text, keyb)
        return True
    except Exception as es:
        await call.answer(f'Ошибка: {es}', show_alert=False)
        return False


def build_search_results_keyboard(search_results, current_page: int, items_per_page: int) -> InlineKeyboardMarkup:
    total_results = len(search_results)
    total_pages = max(1, (total_results + items_per_page - 1) // items_per_page)
    current_page = min(max(1, current_page), total_pages)

    start_index = (current_page - 1) * items_per_page
    end_index = start_index + items_per_page
    sorted_results = sorted(search_results, key=lambda u: getattr(u, 'id_pk', 0))
    page_results = sorted_results[start_index:end_index]

    keyboard = InlineKeyboardMarkup(row_width=1)

    for idx, user in enumerate(page_results, 1):
        user_id = getattr(user, 'id_user', None)
        if not user_id:
            continue
        first_name = getattr(user, 'first_name', '') or ''
        last_name = getattr(user, 'last_name', '') or ''
        login = getattr(user, 'login', '') or ''
        title = (f"{first_name} {last_name}" if (first_name or last_name) else login) or f"ID: {user_id}"
        display_index = start_index + idx
        keyboard.add(InlineKeyboardButton(text=f"{display_index}. {title.strip()}", callback_data=f'user_item-{user_id}-{current_page}-f'))

    def _page_buttons(total_pages: int, current_page_number: int):
        buttons = []
        if total_pages <= 6:
            for p in range(1, total_pages + 1):
                label = f'•{p}•' if p == current_page_number else str(p)
                buttons.append(InlineKeyboardButton(text=label, callback_data=f'users_find_list-{p}'))
            return buttons
        first_label = f'•1•' if current_page_number == 1 else '1'
        buttons.append(InlineKeyboardButton(text=first_label, callback_data='users_find_list-1'))
        left = max(2, current_page_number - 1)
        right = min(total_pages - 1, current_page_number + 1)
        if left > 2:
            buttons.append(InlineKeyboardButton(text='...', callback_data='noop'))
        for p in range(left, right + 1):
            label = f'•{p}•' if p == current_page_number else str(p)
            buttons.append(InlineKeyboardButton(text=label, callback_data=f'users_find_list-{p}'))
        if right < total_pages - 1:
            buttons.append(InlineKeyboardButton(text='...', callback_data='noop'))
        last_label = f'•{total_pages}•' if current_page_number == total_pages else str(total_pages)
        buttons.append(InlineKeyboardButton(text=last_label, callback_data=f'users_find_list-{total_pages}'))
        return buttons

    page_buttons = _page_buttons(total_pages, current_page)
    if page_buttons:
        keyboard.row(*page_buttons)

    navigation_buttons = []
    if total_pages > 1:
        if current_page > 1:
            navigation_buttons.append(InlineKeyboardButton(text='⬅️ Назад', callback_data=f'users_find_list-{current_page - 1}'))
        if current_page < total_pages:
            navigation_buttons.append(InlineKeyboardButton(text='➡️ Далее', callback_data=f'users_find_list-{current_page + 1}'))
    if navigation_buttons:
        keyboard.row(*navigation_buttons)

    keyboard.add(InlineKeyboardButton(text='🔙 К пользователям', callback_data='users'))
    keyboard.add(InlineKeyboardButton(text='🏚 Домой', callback_data='admin_panel'))

    return keyboard


async def users_find_call(call: types.CallbackQuery, state: FSMContext):
    await Sendler_msg.log_client_call(call)
    await States.find_user.set()
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton(text='🔙 К пользователям', callback_data='users'))
    keyboard.add(InlineKeyboardButton(text='🏚 Домой', callback_data='admin_panel'))
    prompt = '🔎 Введите логин (@username или username), ID, или ссылку https://t.me/username'
    await Sendler_msg.send_msg_call(call, prompt, keyboard)
    return True


async def users_find_list_call(call: types.CallbackQuery, state: FSMContext):
    await Sendler_msg.log_client_call(call)
    try:
        callback_data = str(call.data or '')
        current_page = 1
        if 'users_find_list-' in callback_data:
            try:
                current_page = int(callback_data.split('users_find_list-')[-1])
            except Exception:
                current_page = 1
        admin_chat_id = call.message.chat.id
        search_results = get_search_results(admin_chat_id)
        keyb = build_search_results_keyboard(search_results, current_page, USERS_PER_PAGE)
        total_results = len(search_results)
        total_pages = max(1, (total_results + USERS_PER_PAGE - 1) // USERS_PER_PAGE)
        text = (
            f'🔎 Поиск пользователей\n'
            f'Найдено: {total_results}\n'
            f'Страница: {min(max(1, current_page), total_pages)}/{total_pages}'
        )
        await Sendler_msg.send_msg_call(call, text, keyb)
        return True
    except Exception as es:
        await call.answer(f'Ошибка: {es}', show_alert=False)
        return False
