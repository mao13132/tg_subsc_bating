from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


class ChangeLogoKeyboard:
    def back_admin(self):
        keyboard = InlineKeyboardMarkup(row_width=1)

        keyboard.add(InlineKeyboardButton(text=f'🔙 Назад', callback_data='admin_panel'))

        return keyboard
