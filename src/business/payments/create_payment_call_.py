# ---------------------------------------------
# Program by @developer_telegrams
#
#
# Version   Date        Info
# 1.0       2025    Create payment via callback
#
# ---------------------------------------------
from aiogram import types
from aiogram.dispatcher import FSMContext

from src.telegram.sendler.sendler import Sendler_msg
from src.business.text_manager.text_manager import text_manager
from src.telegram.keyboard.keyboards import Admin_keyb
from src.business.payments.payment_service import ensure_payment_link, create_ckassa_payment, record_payment
from src.telegram.bot_core import BotDB
import re


async def create_payment_call(call: types.CallbackQuery, state: FSMContext):
    """
    Создаёт и отправляет ссылку на оплату по клику «Оплата рублями».

    Алгоритм:
    1) Логируем колбэк (аудит).
    2) Определяем `uid` пользователя из `CallbackQuery`.
    3) Парсим сумму из `callback_data` формата `create_payment-<summa>`.
    4) Загружаем тексты интерфейса (кнопка «Оплатить», шаблон сообщения, админ‑ссылки).
    5) Пытаемся получить актуальную ссылку через `ensure_payment_link(uid)`.
    6) Если ссылки нет — создаём новый платёж и записываем его в БД.
    7) Если ссылку получить не удалось — показываем пользователю ошибку.
    8) Отправляем сообщение со ссылкой и закрепляем его у пользователя.
    9) Закрываем колбэк коротким ответом, без алерта.
    """

    # 1) Лог: фиксируем событие нажатия
    await Sendler_msg.log_client_call(call)

    try:
        await call.message.edit_reply_markup(reply_markup=Admin_keyb().payment_wait_keyb())
    except Exception:
        pass

    # 2) UID: берём из from_user, иначе из chat.id
    uid = str(
        getattr(call, 'from_user', None).id
        if getattr(call, 'from_user', None)
        else getattr(getattr(call, 'message', None), 'chat', None).id
    )

    # 3) Сумма из callback_data: create_payment-<summa>
    amount_rub = None
    try:
        data = str(call.data or '')
        if 'create_payment-' in data:
            amount_rub = int(data.split('create_payment-')[-1])
    except Exception:
        amount_rub = None

    # 4) Тексты интерфейса
    admin_link = await text_manager.get_button_text('admin_link')
    admin_text = await text_manager.get_button_text('admin_text')
    btn_text = await text_manager.get_button_text('paid')
    template = await text_manager.get_message('send_payment')

    # 5) Ссылка на оплату (если уже есть) и актуальная сумма
    pay_link = None
    final_amount = amount_rub or 0

    try:
        # 5.1) Пробуем получить свежую ссылку из последнего платежа
        link_data = await ensure_payment_link(uid, amount_rub)
        pay_link = link_data.get('link') or None
        if pay_link:
            try:
                final_amount = int(link_data.get('amount') or final_amount)
            except Exception:
                pass

        # 6) Если ссылки нет — создаём новый платёж и записываем его
        if not pay_link and amount_rub and int(amount_rub) > 0:
            created = await create_ckassa_payment(uid, int(amount_rub))
            pay_link = created['payUrl']
            reg_pay_num = created['regPayNum']
            await record_payment(uid, int(amount_rub), reg_pay_num, pay_link, 'created')
    except Exception:
        # Сбой интеграции: не получили ссылку
        pay_link = None

    # 7) Нет ссылки — сообщаем пользователю об ошибке
    if not pay_link:
        await call.answer('Не удалось создать платёж. Попробуйте позже.', show_alert=True)
        return False

    # 8) Редактирование текущего сообщения на ссылку оплаты (бесшовно)
    keyboard = Admin_keyb().payment_link_back_keyb(btn_text, pay_link, final_amount, admin_text, admin_link)
    client_message = template.format(summa=final_amount, link=f"<a href='{pay_link}'>Оплатить</a>")

    try:
        await call.message.edit_text(client_message, reply_markup=keyboard, disable_web_page_preview=True)
        try:
            await call.message.bot.pin_chat_message(chat_id=int(uid), message_id=int(call.message.message_id))
        except Exception:
            pass
        try:
            await BotDB.payment_messages.ensure_active(str(uid), int(call.message.message_id), int(final_amount))
        except Exception:
            pass
    except Exception:
        try:
            res = await call.message.bot.send_message(
                int(uid), client_message, reply_markup=keyboard,
                disable_web_page_preview=True, protect_content=True
            )
            try:
                await call.message.bot.pin_chat_message(chat_id=int(uid), message_id=int(res['message_id']))
            except Exception:
                pass
            try:
                msg_id = res['message_id'] if isinstance(res, dict) else getattr(res, 'message_id', None)
                if msg_id:
                    await BotDB.payment_messages.ensure_active(str(uid), int(msg_id), int(final_amount))
            except Exception:
                pass
        except Exception:
            await call.answer('Ошибка отправки ссылки', show_alert=True)
            return False

    # 9) Успех: закрываем колбэк
    await call.answer('Счёт сформирован', show_alert=False)
    return True


async def pay_other_call(call: types.CallbackQuery, state: FSMContext):
    await Sendler_msg.log_client_call(call)

    uid = str(
        getattr(call, 'from_user', None).id
        if getattr(call, 'from_user', None)
        else getattr(getattr(call, 'message', None), 'chat', None).id
    )

    amount = 0
    try:
        latest = await BotDB.payments.read_latest_by_user(str(uid))
        amount = int(getattr(latest, 'amount', 0) or 0) if latest else 0
    except Exception:
        amount = 0

    if amount <= 0:
        try:
            src = str(getattr(getattr(call, 'message', None), 'text', '') or '')
            m = re.search(r'(\d+)', src)
            if m:
                amount = int(m.group(1))
        except Exception:
            amount = 0

    template = await text_manager.get_message('pay_other_info')
    if not template:
        template = (
            "🌍 Для оплаты из других\n"
            "стран напишите @plutoshelp\n\n"
            "Обязательно отправьте ему\n"
            "номер аккаунт: 1078134881\n\n"
            "К оплате {summa} рублей (будет переведено на вашу валюту)"
        )
    client_message = template.format(summa=amount)

    keyboard = Admin_keyb().back_payment_choose(amount)
    try:
        await call.message.bot.send_message(
            int(uid), client_message, reply_markup=keyboard,
            disable_web_page_preview=True, protect_content=True
        )
        try:
            await call.message.delete()
        except Exception:
            pass
    except Exception:
        await call.answer('Ошибка отправки сообщения', show_alert=True)
        return False

    await call.answer('', show_alert=False)
    return True


async def back_payment_choose_call(call: types.CallbackQuery, state: FSMContext):
    await Sendler_msg.log_client_call(call)

    uid = str(
        getattr(call, 'from_user', None).id
        if getattr(call, 'from_user', None)
        else getattr(getattr(call, 'message', None), 'chat', None).id
    )

    amount = 0
    try:
        data = str(call.data or '')
        if 'back_payment_choose-' in data:
            amount = int(data.split('back_payment_choose-')[-1])
    except Exception:
        amount = 0

    template_choose = await text_manager.get_message('payment_choose')
    pay_rub_text = await text_manager.get_button_text('pay_rub')
    pay_other_text = await text_manager.get_button_text('pay_other')

    kb = Admin_keyb().payment_choose(pay_rub_text, pay_other_text, amount)
    client_message = (template_choose or '').format(summa=amount)

    try:
        await call.message.edit_text(client_message, reply_markup=kb, disable_web_page_preview=True)
    except Exception:
        try:
            await call.message.bot.send_message(int(uid), client_message, reply_markup=kb,
                                                disable_web_page_preview=True, protect_content=True)
        except Exception:
            await call.answer('Ошибка возврата', show_alert=True)
            return False

    await call.answer('', show_alert=False)
    return True
