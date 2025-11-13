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

from settings import LOGO, ADMIN
from src.business.managers.check_manager import check_manager
from src.business.managers.get_managers_ import get_managers
from src.business.managers.keyboard_managers import ManagersKeyboard
from src.telegram.bot_core import BotDB
from src.telegram.sendler.sendler import Sendler_msg


async def _delete_manger(id_manger, managers):
    for count, manager in enumerate(managers):
        row_id = manager['id']

        if str(row_id) == str(id_manger):
            pop_manager = managers.pop(count)

            return managers

    return managers


async def delete_managers(message: Message):
    try:
        manager_id = str(message.text).split('_')[1]
    except Exception as es:
        msg = f'Ошибка при разборе для удаления delete_managers{es}'

        return False

    id_user = message.chat.id

    is_manager = await check_manager(message)

    if str(id_user) not in ADMIN and not is_manager:
        await Sendler_msg.send_msg_message(message, '⛔️ В доступе отказано', None)

        return False

    managers = await get_managers()

    managers = await _delete_manger(manager_id, managers)

    managers_sql = json.dumps(managers)

    res_update = await BotDB.update_settings(key='managers', value=managers_sql)

    if res_update:
        status_remove = f'✅ Менеджер удален\n\n'
    else:
        status_remove = f'❌ Ошибка удаления менеджер\n\n'

    if managers:
        msg = f'{status_remove}<b>Список менеджеров:</b>\n\n'
    else:
        msg = f'{status_remove}❌<b>Список менеджеров пуст</b>'

    msg += f'\n'.join(f'{count + 1}. {manager["login"]} - Удалить '
                      f'/dels_{manager["id"]}' for count, manager in enumerate(managers))

    keyboard = ManagersKeyboard.managers()

    await Sendler_msg().new_sendler_photo_message(message, LOGO, msg, keyboard)

    return True
