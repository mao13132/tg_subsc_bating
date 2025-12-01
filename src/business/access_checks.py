# ---------------------------------------------
# Program by @developer_telegrams
#
#
# Version   Date        Info
# 1.0       2023    Initial Version
#
# ---------------------------------------------
from datetime import datetime

from aiogram import types
from aiogram.types import Message

from src.business.channel_subscription.check_subscription import ChannelSubscriptionChecker
from src.business.text_manager.text_manager import text_manager
from src.telegram.bot_core import BotDB
from src.telegram.keyboard.keyboards import Admin_keyb
from src.telegram.sendler.sendler import Sendler_msg
from src.utils.logger._logger import logger_msg
from src.business.payments.payment_service import ensure_payment_link

# 0) Ключ настройки канала для проверки подписки
CHANNEL_KEY = 'analytic_chat'


def _ctx_message(ctx):
    """
    1) Унифицирует контекст: принимает `Message` или `CallbackQuery`
    2) Возвращает объект `Message` для отправки ответов
    """
    # 1) Если уже `Message` — возвращаем как есть
    try:
        return ctx if isinstance(ctx, Message) else getattr(ctx, 'message', None)
    except:
        # 2) Иначе пытаемся извлечь `message` из `CallbackQuery`
        return getattr(ctx, 'message', None)


def _ctx_bot(ctx):
    """
    1) Унифицирует доступ к `bot` из `Message` или `CallbackQuery`
    2) Нужен для проверок подписки и отправки сообщений
    """
    # 1) Прямой доступ к bot если есть
    try:
        return ctx.bot if hasattr(ctx, 'bot') else getattr(getattr(ctx, 'message', None), 'bot', None)
    except:
        # 2) Достаём bot из вложенного message
        return getattr(getattr(ctx, 'message', None), 'bot', None)


def _ctx_user_id(ctx):
    """
    1) Унифицирует извлечение `id_user` из контекста
    2) Используется в обеих проверках
    """
    m = _ctx_message(ctx)
    return getattr(getattr(m, 'chat', None), 'id', None)


async def check_need_paid(ctx):
    """
    Проверка необходимости оплаты.

    Алгоритм:
    1) Получаем `id_user` из контекста
    2) Читаем данные пользователя из БД
    3) Если `need_paid=True`:
       3.1) Формируем текст и кнопку оплаты
       3.2) Отправляем сообщение с оплатой
       3.3) Возвращаем `True` (остановить дальнейшую обработку)
    4) Иначе — возвращаем `False` (продолжить обработку)
    """
    # 1) Идентификатор пользователя
    id_user = _ctx_user_id(ctx)
    if id_user is None:
        # Нет пользователя в контексте — считаем, что обработку продолжать нельзя
        return True

    # 2) Чтение пользователя из БД
    data_user = await BotDB.get_user_bu_id_user(id_user)

    # 3) Нужна оплата
    if getattr(data_user, 'need_paid', False):
        # Бесплатная мотивация: если активная мотивация с суммой 0 — пропускаем блокировку
        motivations = await BotDB.motivations.read_by_filter({}) or []
        now = datetime.utcnow()
        try:
            motivations.sort(key=lambda m: getattr(m, 'created_at', now), reverse=True)
            motivation = motivations[0] if motivations else None
        except Exception:
            motivation = motivations[0] if motivations else None

        try:
            is_free = bool(motivation) and int(getattr(motivation, 'summa', 0) or 0) == 0
        except Exception:
            is_free = False

        if is_free:
            return False
        # 3.1) Текст и кнопка
        template = await text_manager.get_message('no_paid_msg')
        btn_text = await text_manager.get_button_text('paid')
        result = await ensure_payment_link(str(id_user))
        link_payment = result.get('link')
        amount = int(result.get('amount') or 0)

        if link_payment:
            # 3.2) Отправка сообщения с кнопкой оплаты
            keyboard = Admin_keyb().payment_keyb(btn_text, link_payment)

            try:
                text_msg = (template or '').format(summa=amount, link=link_payment if link_payment else '')
            except:
                text_msg = template

            await Sendler_msg.send_msg_message(_ctx_message(ctx), text_msg, keyboard)
            # 3.3) Остановка дальнейшей обработки
            return True

        # 3.2*) Ссылка недоступна — отправляем информативное сообщение

        motivations = await BotDB.motivations.read_by_filter({}) or []
        now = datetime.utcnow()
        try:
            motivations.sort(key=lambda m: getattr(m, 'created_at', now), reverse=True)
            motivation = motivations[0] if motivations else None
        except Exception:
            motivation = motivations[0] if motivations else None

        if not motivation:
            no_load = await text_manager.get_message('no_load')
            await Sendler_msg.send_msg_message(_ctx_message(ctx), no_load, None)

            return True

        if template:
            try:
                template = (template or '').format(summa=motivation.summa, link=link_payment)
            except:
                pass

        await Sendler_msg.send_msg_message(_ctx_message(ctx), template or 'Ссылка на оплату недоступна', None)
        # 3.3) Остановка дальнейшей обработки
        return True

    # 4) Оплата не требуется — продолжаем
    return False


async def ensure_subscription(ctx):
    """
    Проверка подписки пользователя на целевой канал.

    Алгоритм:
    1) Получаем `id_user` из контекста
    2) Читаем `id_channel` из настроек (`CHANNEL_KEY`)
    3) Если канал не настроен — сообщаем админам и `False`
    4) Проверяем подписку через `ChannelSubscriptionChecker`
    5) Если не подписан — отправляем текст 'no_subs', логируем и `False`
    6) Если подписан — отмечаем `is_subs=True` в БД и `True`
    """
    # 1) Идентификатор пользователя
    id_user = _ctx_user_id(ctx)
    if id_user is None:
        return False

    # 2) Идентификатор канала
    id_channel = await BotDB.get_setting(CHANNEL_KEY)

    # 3) Нет канала — предупреждаем админов
    if not id_channel:
        await Sendler_msg.sendler_to_admin_mute(
            _ctx_message(ctx),
            '❌Не установлен чат, на подписку которого проверяем, установите его в админ панели',
            None
        )
        return False

    # 4) Проверка подписки
    checker = ChannelSubscriptionChecker(_ctx_bot(ctx), id_channel)
    is_subscription = await checker.is_user_subscribed(id_user)

    # 5) Нет подписки — информируем и логируем
    if not is_subscription:
        error_ = await text_manager.get_message('no_subs')
        await Sendler_msg.send_msg_message(_ctx_message(ctx), error_, None)
        logger_msg(f'Пользователь {id_user} без подписки, нажимал кнопку "Получить прогноз"')
        return False

    # 6) Отмечаем подписку в БД
    await BotDB.edit_user('is_subs', True, id_user)
    return True
