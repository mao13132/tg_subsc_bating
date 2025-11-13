# ---------------------------------------------
# Program by @developer_telegrams
#
#
# Version   Date        Info
# 1.0       2023    Initial Version
#
# ---------------------------------------------
import json
from src.telegram.bot_core import BotDB
from src.business.managers.get_managers_ import get_managers


async def update_manager_id(username: str, chat_id: int) -> bool:
    """
    Обновляет ID менеджера в базе данных при первом обращении
    
    Args:
        username: Имя пользователя менеджера (без @)
        chat_id: ID чата пользователя
        
    Returns:
        bool: True если ID был обновлен, False если менеджер не найден
    """
    managers = await get_managers()
    
    if not managers:
        return False
    
    # Приводим username к нижнему регистру для сравнения
    username_lower = username.lower() if username else None
    
    updated = False
    
    for manager in managers:
        manager_login = manager.get('login', '')
        
        # Приводим логин менеджера к нижнему регистру
        try:
            manager_login_lower = str(manager_login).lower()
        except:
            manager_login_lower = manager_login
        
        # Проверяем совпадение по username и отсутствие chat_id
        if (username_lower == manager_login_lower and 
            username_lower is not None and 
            manager.get('chat_id') is None):
            
            # Обновляем chat_id менеджера
            manager['chat_id'] = chat_id
            updated = True
            break
    
    # Сохраняем обновленные данные в базу
    if updated:
        managers_json = json.dumps(managers)
        await BotDB.update_settings(key='managers', value=managers_json)
        return True
    
    return False