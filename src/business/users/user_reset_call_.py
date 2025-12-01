from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.telegram.sendler.sendler import Sendler_msg
from src.telegram.bot_core import BotDB


async def _build_card_and_send(call: types.CallbackQuery, user_id: str, current_page: int, context_tag: str):
    user = await BotDB.get_user_bu_id_user(user_id)
    if not user:
        await call.answer('Пользователь не найден')
        return False

    first_name = getattr(user, 'first_name', '') or ''
    last_name = getattr(user, 'last_name', '') or ''
    login = getattr(user, 'login', '') or ''
    premium = getattr(user, 'premium', '') or ''
    has_subscription = bool(getattr(user, 'is_subs', False))
    needs_payment = bool(getattr(user, 'need_paid', False))
    get_offer_flag = bool(getattr(user, 'get_offer', False))

    title = (f"{first_name} {last_name}" if (first_name or last_name) else login) or f"ID: {user_id}"
    text = (
        f"👤 {title.strip()}\n"
        f"ID: {user_id}\n"
        f"Premium: {premium or '—'}\n"
        f"Подписка: {'✅' if has_subscription else '❌'}\n"
        f"Нужен платёж: {'✅' if needs_payment else '❌'}\n"
        f"Нажал получить предложение: {'✅' if get_offer_flag else '❌'}"
    )

    keyboard = InlineKeyboardMarkup(row_width=1)
    if context_tag == 'f':
        keyboard.add(InlineKeyboardButton(text='🔙 К странице', callback_data=f'users_find_list-{current_page}'))
    else:
        keyboard.add(InlineKeyboardButton(text='🔙 К странице', callback_data=f'users_list-{current_page}'))
    keyboard.add(InlineKeyboardButton(text='🧹 Обнулить', callback_data=f'user_reset_all-{user_id}-{current_page}-{context_tag}'))
    keyboard.add(InlineKeyboardButton(text='🧮 Обнулить счёт', callback_data=f'user_reset_bill-{user_id}-{current_page}-{context_tag}'))
    keyboard.add(InlineKeyboardButton(text='🏚 Домой', callback_data='admin_panel'))

    await Sendler_msg.send_msg_call(call, text, keyboard)
    return True


async def user_reset_all_call(call: types.CallbackQuery, state: FSMContext):
    await Sendler_msg.log_client_call(call)
    try:
        data = str(call.data or '')
        rest = data.split('user_reset_all-')[-1]
        parts = rest.split('-')
        user_id = parts[0]
        try:
            current_page = int(parts[1]) if len(parts) > 1 else 1
        except Exception:
            current_page = 1
        context_tag = parts[2] if len(parts) > 2 else 'u'

        values = {
            'need_paid': False,
            'received_forecast': False,
            'is_subs': False,
            'send_payments': False,
            'wants_forecast': False,
            'get_offer': False,
        }
        await BotDB.edit_user_by_filter({'id_user': str(user_id)}, values)
        await BotDB.payments.delete_by_filter({'id_user': str(user_id)})

        await _build_card_and_send(call, user_id, current_page, context_tag)
        return True
    except Exception as es:
        await call.answer(f'Ошибка: {es}', show_alert=False)
        return False


async def user_reset_bill_call(call: types.CallbackQuery, state: FSMContext):
    await Sendler_msg.log_client_call(call)
    try:
        data = str(call.data or '')
        rest = data.split('user_reset_bill-')[-1]
        parts = rest.split('-')
        user_id = parts[0]
        try:
            current_page = int(parts[1]) if len(parts) > 1 else 1
        except Exception:
            current_page = 1
        context_tag = parts[2] if len(parts) > 2 else 'u'

        await BotDB.edit_user_by_filter({'id_user': str(user_id)}, {'need_paid': False, 'send_payments': False})

        await _build_card_and_send(call, user_id, current_page, context_tag)
        return True
    except Exception as es:
        await call.answer(f'Ошибка: {es}', show_alert=False)
        return False
