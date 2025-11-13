# ---------------------------------------------
# Program by @developer_telegrams
#
#
# Version   Date        Info
# 1.0       2023    Initial Version
#
# ---------------------------------------------
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


class ManagersKeyboard:
    @staticmethod
    def back_managers():
        keyboard = InlineKeyboardMarkup(row_width=1)

        keyboard.add(InlineKeyboardButton(text=f'🔙 Назад', callback_data='managers'))

        return keyboard

    @staticmethod
    def managers():
        keyboard = InlineKeyboardMarkup(row_width=1)

        keyboard.add(InlineKeyboardButton(text=f'➕ Добавить менеджера', callback_data='add_managers'))

        keyboard.add(InlineKeyboardButton(text=f'🔙 Назад', callback_data='admin_panel'))

        return keyboard
