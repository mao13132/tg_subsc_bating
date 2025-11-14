from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


class ChatAdminKeyb:
    def back_add_chat(self):
        keyboard = InlineKeyboardMarkup(row_width=1)

        keyboard.add(InlineKeyboardButton(text=f'🔙 Назад', callback_data=f'chat_admin_call'))

        return keyboard

    def chat_admin_btns(self, settings_in_sql):
        keyboard = InlineKeyboardMarkup(row_width=1)

        for key, data in settings_in_sql.items():
            keyboard.add(InlineKeyboardButton(text=f"🗂️ {data['name']}", callback_data=f'admin_chat-{key}'))

            continue

        keyboard.add(InlineKeyboardButton(text=f'🔙 Назад', callback_data=f'admin_panel'))

        return keyboard
