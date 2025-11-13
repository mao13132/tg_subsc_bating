# ---------------------------------------------
# Program by @developer_telegrams
#
#
# Version   Date        Info
# 1.0       2023    Initial Version
#
# ---------------------------------------------
import json

from aiogram.types import Message

from src.business.managers.get_managers_ import get_managers
from src.business.managers.update_manager_id import update_manager_id


async def check_manager(message: Message) -> bool:
    """
    Проверяет является ли пользователь менеджером
    При первом обращении сохраняет ID пользователя если он менеджер
    
    Args:
        message: Сообщение от пользователя
        
    Returns:
        bool: True если пользователь является менеджером
    """
    id_user = message.chat.id
    login = message.chat.username

    try:
        login_lower = login.lower() if login else None
    except:
        login_lower = login

    managers = await get_managers()
    
    if not managers:
        return False

    for manager in managers:
        login_row = manager.get('login')
        chat_id_row = manager.get('chat_id')

        try:
            login_row_lower = str(login_row).lower() if login_row else None
        except:
            login_row_lower = login_row

        # Проверка по chat_id (приоритетная)
        if chat_id_row and id_user == chat_id_row:
            return True
        
        # Проверка по username
        if (login_lower and login_row_lower and 
            login_lower == login_row_lower):
            
            # Если chat_id еще не сохранен, сохраняем его
            if not chat_id_row:
                await update_manager_id(login, id_user)
            
            return True
        
        # Обратная совместимость: проверка ID как строки (старый формат)
        if id_user == login_row:
            return True

    return False
