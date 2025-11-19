from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


class PostsKeyb:
    @staticmethod
    def collect_messages_keyb():
        keyboard = InlineKeyboardMarkup(row_width=1)

        keyboard.add(InlineKeyboardButton(text=f"✅ Загрузить", callback_data='send_user_messages'))

        keyboard.add(InlineKeyboardButton(text="🔙 Назад", callback_data='bet_menu'))

        keyboard.add(InlineKeyboardButton(text=f'🏚 Домой', callback_data='admin_panel'))

        return keyboard
