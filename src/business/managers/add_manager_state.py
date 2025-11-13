# ---------------------------------------------
# Program by @developer_telegrams
#
#
# Version   Date        Info
# 1.0       2023    Initial Version
#
# ---------------------------------------------
import json

from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from settings import LOGO
from src.business.devision_msg.devision_msg import division_message
from src.business.managers._get_last_id import get_last_id
from src.business.managers.keyboard_managers import ManagersKeyboard
from src.business.managers.username_extractor import extract_username_for_get_chat
from src.telegram.sendler.sendler import Sendler_msg
from src.telegram.bot_core import BotDB


async def add_manager_state(message: Message, state: FSMContext):
    """
    Добавляет нового менеджера в систему
    Теперь поддерживает как username, так и ID пользователей
    """
    await Sendler_msg.log_client_message(message)

    manager_text = message.text.strip()

    manager_input = extract_username_for_get_chat(manager_text)

    if not manager_input:
        manager_input = manager_text

    try:
        is_numeric_id = int(manager_input)
    except:
        is_numeric_id = False
    
    if is_numeric_id:
        # Если введен числовой ID, сохраняем как chat_id
        manager_login = None
        manager_chat_id = int(manager_input)
    else:
        # Если введен username, сохраняем как login
        try:
            manager_login = manager_input.lower()
        except:
            manager_login = manager_input
        manager_chat_id = None

    managers = await BotDB.get_setting('managers')

    if managers:
        managers = json.loads(managers)
    else:
        managers = []

    # Проверяем, не существует ли уже такой менеджер
    for existing_manager in managers:
        existing_login = existing_manager.get('login')
        existing_chat_id = existing_manager.get('chat_id')
        
        if (manager_login and existing_login and 
            manager_login.lower() == str(existing_login).lower()):
            # Менеджер с таким username уже существует
            _msg = f'❌ Менеджер с username {manager_login} уже существует'
            keyb = ManagersKeyboard.back_managers()
            await Sendler_msg().sendler_photo_message(message, LOGO, _msg, keyb)
            await state.finish()
            return False
            
        if (manager_chat_id and existing_chat_id and 
            manager_chat_id == existing_chat_id):
            # Менеджер с таким ID уже существует
            _msg = f'❌ Менеджер с ID {manager_chat_id} уже существует'
            keyb = ManagersKeyboard.back_managers()
            await Sendler_msg().sendler_photo_message(message, LOGO, _msg, keyb)
            await state.finish()
            return False

    id_new_manager = await get_last_id(managers)

    # Создаем объект менеджера с новой структурой
    manager = {
        'id': id_new_manager,
        'login': manager_login,
        'chat_id': manager_chat_id
    }

    managers.append(manager)
    managers_sql = json.dumps(managers)
    res_update = await BotDB.update_settings(key='managers', value=managers_sql)

    # Формируем сообщение об успешном добавлении
    if manager_login:
        manager_display = f'@{manager_login}'
    else:
        manager_display = f'ID: {manager_chat_id}'
    
    status_add = (f'✅ {manager_display} успешно добавлен\n\n' if res_update 
                  else f'❌ Не смог добавить {manager_display}\n\n')

    _msg = f'{status_add}<b>Список менеджеров:</b>\n\n'

    # Формируем список менеджеров для отображения
    for count, mgr in enumerate(managers):
        mgr_login = mgr.get('login')
        mgr_chat_id = mgr.get('chat_id')
        
        if mgr_login:
            display_name = f'@{mgr_login}'
        elif mgr_chat_id:
            display_name = f'ID: {mgr_chat_id}'
        else:
            display_name = 'Неизвестный'
            
        _msg += f'{count + 1}. {display_name} - Удалить /dels_{mgr["id"]}\n'

    keyb = ManagersKeyboard.managers()

    if len(_msg) < 1024:
        await Sendler_msg().sendler_photo_message(message, LOGO, _msg, keyb)
    else:
        await division_message(message, _msg, keyb)

    await state.finish()
    return True
