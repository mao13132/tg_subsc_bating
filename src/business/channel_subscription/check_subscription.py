# ---------------------------------------------
# Program by @developer_telegrams
#
# Модуль проверки подписки на канал
# Version   Date        Info
# 1.0       2024    Initial Version
# 1.1       2024    Добавлена поддержка ID каналов
#
# ---------------------------------------------

from aiogram import Bot
from aiogram.utils.exceptions import ChatNotFound, BotBlocked, UserDeactivated
from typing import Union
import logging

from src.utils.logger._logger import logger_msg


class ChannelSubscriptionChecker:
    """
    Класс для проверки подписки пользователя на канал
    Поддерживает как URL ссылки, так и ID каналов
    """

    def __init__(self, bot: Bot, channel_identifier: Union[str, int]):
        """
        Инициализация проверщика подписки
        
        Args:
            bot: Экземпляр бота aiogram
            channel_identifier: URL канала, username (@channel) или ID канала (-100123456789)
        """
        self.bot = bot
        self.channel_identifier = self._process_channel_identifier(channel_identifier)

    def _process_channel_identifier(self, channel_identifier: Union[str, int]) -> Union[str, int, None]:
        """
        Обрабатывает идентификатор канала (URL, username или ID)
        
        Args:
            channel_identifier: URL канала, username (@channel) или ID канала (-100123456789)
            
        Returns:
            Union[str, int, None]: Обработанный идентификатор канала или None для приватных каналов
        """
        if not channel_identifier:
            return None

        # Если передан числовой ID канала
        if isinstance(channel_identifier, int):
            return channel_identifier

        # Если передана строка
        if isinstance(channel_identifier, str):
            # Если это уже username с @
            if channel_identifier.startswith('@'):
                return channel_identifier

            # Если это числовой ID в виде строки
            if channel_identifier.lstrip('-').isdigit():
                return int(channel_identifier)

            # Если это приглашение по ссылке (приватный канал)
            if '/+' in channel_identifier:
                logging.warning("Приватные каналы по invite-ссылкам не поддерживаются для проверки подписки")
                return None

            # Если это URL публичного канала
            if 't.me/' in channel_identifier:
                username = channel_identifier.split('t.me/')[-1]
                return f"@{username}" if not username.startswith('@') else username

            # Если это просто username без @
            return f"@{channel_identifier}"

        return None

    async def is_user_subscribed(self, user_id: int) -> bool:
        """
        Проверяет, подписан ли пользователь на канал
        
        Args:
            user_id: ID пользователя Telegram
            
        Returns:
            bool: True если подписан, False если нет
        """
        if not self.channel_identifier:
            # Если канал не определен, не можем проверить подписку
            logger_msg("Идентификатор канала не определен")
            return True

        try:
            # Получаем информацию о пользователе в канале
            member = await self.bot.get_chat_member(
                chat_id=self.channel_identifier,
                user_id=user_id
            )

            # Проверяем статус пользователя
            # 'member', 'administrator', 'creator' - подписан
            # 'left', 'kicked' - не подписан
            return member.status in ['member', 'administrator', 'creator']

        except ChatNotFound:
            logger_msg(f"Канал {self.channel_identifier} не найден")
            return True  # Возвращаем True чтобы не блокировать пользователей

        except (BotBlocked, UserDeactivated):
            logging.warning(f"Пользователь {user_id} заблокировал бота или деактивирован")
            return False

        except Exception as e:
            logger_msg(f"Ошибка при проверке подписки: {e}")
            return True  # В случае ошибки не блокируем пользователя

    async def get_subscription_status_message(self, user_id: int) -> tuple[bool, str]:
        """
        Получает статус подписки и соответствующее сообщение
        
        Args:
            user_id: ID пользователя
            
        Returns:
            tuple: (is_subscribed: bool, message: str)
        """
        is_subscribed = await self.is_user_subscribed(user_id)

        if is_subscribed:
            message = """
✅ Отлично! Ты подписан на канал.

Чисто для понимания эмоции девчонок, которые начинают тут делать первые деньги))
P.S. Не знаю что ты такого сделал, но тебе очень повезло здесь оказаться 🔥
"""
        else:
            message = """
❌ Для получения видео необходимо подписаться на канал!

После подписки нажми кнопку "Проверить подписку" ⬇️
"""

        return is_subscribed, message
