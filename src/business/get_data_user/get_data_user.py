# ---------------------------------------------
# Program by @developer_telegrams
#
#
# Version   Date        Info
# 1.0       2023    Initial Version
#
# ---------------------------------------------
from aiogram.types import Message


async def get_data_user(message: Message):
    try:
        username = message.from_user.username if message.from_user.username else 'Не указан'
    except:
        username = f'Не указан'

    try:
        first_name = message.from_user.first_name if message.from_user.first_name else 'Не указано'
    except:
        first_name = f'Не указано'

    try:
        last_name = message.from_user.last_name if message.from_user.last_name else 'Не указана'
    except:
        last_name = f'Не указана'

    try:
        premium = 'Да' if message.from_user.is_premium else 'Нет'
    except:
        premium = f'Не указано'

    return_dict = {
        'login': username,
        'first_name': first_name,
        'last_name': last_name,
        'premium': premium,
    }

    return return_dict
