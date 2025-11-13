# ---------------------------------------------
# Program by @developer_telegrams
#
# Функция для извлечения username из различных форматов Telegram ссылок
# Version   Date        Info
# 1.0       2023    Initial Version
#
# ---------------------------------------------
import re
from typing import Optional


def extract_username_for_get_chat(input_string: str) -> Optional[str]:
    """
    Извлекает username из различных форматов Telegram ссылок для использования с bot.get_chat
    
    Поддерживаемые форматы:
    - https://t.me/username
    - http://t.me/username
    - t.me/username
    - @username
    - username (без префиксов)
    - https://telegram.me/username
    - tg://resolve?domain=username
    
    Args:
        input_string (str): Строка с ссылкой или username
        
    Returns:
        Optional[str]: Очищенный username для bot.get_chat или None если не удалось извлечь
        
    Examples:
        >>> extract_username_for_get_chat('https://t.me/example_user')
        'example_user'
        >>> extract_username_for_get_chat('@example_user')
        'example_user'
        >>> extract_username_for_get_chat('example_user')
        'example_user'
    """
    if not input_string or not isinstance(input_string, str):
        return None

    # Убираем лишние пробелы
    input_string = input_string.strip()

    if not input_string:
        return None

    # Паттерны для различных форматов ссылок
    patterns = [
        # https://t.me/username или http://t.me/username
        r'https?://t\.me/([a-zA-Z0-9_]+)',
        # https://telegram.me/username или http://telegram.me/username  
        r'https?://telegram\.me/([a-zA-Z0-9_]+)',
        # t.me/username (без протокола)
        r't\.me/([a-zA-Z0-9_]+)',
        # telegram.me/username (без протокола)
        r'telegram\.me/([a-zA-Z0-9_]+)',
        # tg://resolve?domain=username
        r'tg://resolve\?domain=([a-zA-Z0-9_]+)',
        # @username
        r'^@([a-zA-Z0-9_]+)$',
    ]

    # Проверяем каждый паттерн
    for pattern in patterns:
        match = re.search(pattern, input_string, re.IGNORECASE)
        if match:
            username = match.group(1)
            # Проверяем валидность username (только буквы, цифры и подчеркивания)
            if re.match(r'^[a-zA-Z0-9_]+$', username) and len(username) >= 5:
                return username

    # Если это просто username без префиксов
    if re.match(r'^[a-zA-Z0-9_]+$', input_string) and len(input_string) >= 5:
        return input_string

    return None
