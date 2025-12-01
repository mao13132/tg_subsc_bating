# ---------------------------------------------
# Program by @developer_telegrams
#
# Управление элементом пользователя (колбэк по кнопке списка).
# Минимальный обработчик: загружает пользователя и показывает краткую карточку.
# ---------------------------------------------
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.telegram.sendler.sendler import Sendler_msg
from src.telegram.bot_core import BotDB


async def user_item_call(call: types.CallbackQuery, state: FSMContext):
    """
    Обработчик кнопки пользователя: "user_item-<id_user>"

    Действия:
    - Парсит id_user из колбэка;
    - Загружает данные пользователя из БД;
    - Показывает краткую карточку и кнопки навигации.
    """
    await Sendler_msg.log_client_call(call)

    try:
        # Извлекаем id пользователя и страницу из callback_data
        callback_data = str(call.data or '')
        payload = callback_data.split('user_item-')[-1]
        tokens = payload.split('-')
        user_id = tokens[0]
        try:
            current_page = int(tokens[1]) if len(tokens) > 1 else 1
        except Exception:
            current_page = 1
        context_tag = tokens[2] if len(tokens) > 2 else 'u'

        # Получаем пользователя из БД
        user = await BotDB.get_user_bu_id_user(user_id)
        if not user:
            await call.answer('Пользователь не найден')
            return False

        # Готовим текст карточки
        first_name = getattr(user, 'first_name', '') or ''
        last_name = getattr(user, 'last_name', '') or ''
        login = getattr(user, 'login', '') or ''
        premium = getattr(user, 'premium', '') or ''
        has_subscription = bool(getattr(user, 'is_subs', False))
        needs_payment = bool(getattr(user, 'need_paid', False))
        get_offer_flag = bool(getattr(user, 'get_offer', False))

        title = (f"{first_name} {last_name}" if (first_name or last_name) else login) or f"ID: {user_id}"

        card_text = (
            f"👤 {title.strip()}\n"
            f"ID: {user_id}\n"
            f"Premium: {premium or '—'}\n"
            f"Подписка: {'✅' if has_subscription else '❌'}\n"
            f"Нужен платёж: {'✅' if needs_payment else '❌'}\n"
            f"Нажал получить предложение: {'✅' if get_offer_flag else '❌'}"
        )

        # Кнопки навигации: назад к списку пользователей и в админ-панель
        keyboard = InlineKeyboardMarkup(row_width=1)
        if context_tag == 'f':
            keyboard.add(InlineKeyboardButton(text='🔙 К странице', callback_data=f'users_find_list-{current_page}'))
        else:
            keyboard.add(InlineKeyboardButton(text='🔙 К странице', callback_data=f'users_list-{current_page}'))
        keyboard.add(InlineKeyboardButton(text='🧹 Обнулить', callback_data=f'user_reset_all-{user_id}-{current_page}-{context_tag}'))
        keyboard.add(InlineKeyboardButton(text='🧮 Обнулить счёт', callback_data=f'user_reset_bill-{user_id}-{current_page}-{context_tag}'))
        keyboard.add(InlineKeyboardButton(text='🏚 Домой', callback_data='admin_panel'))

        await Sendler_msg.send_msg_call(call, card_text, keyboard)
        return True
    except Exception as es:
        await call.answer(f'Ошибка: {es}', show_alert=False)
        return False
        