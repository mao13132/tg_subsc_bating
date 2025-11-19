from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


class Edit_keyb:
    def edit_text_back(self, text_type):
        keyboard = InlineKeyboardMarkup(row_width=1)
        back_callback = 'text_keyboards' if text_type == 'buttons' else 'text_msg'
        keyboard.add(InlineKeyboardButton(text='🔙 Назад', callback_data=back_callback))
        keyboard.add(InlineKeyboardButton(text=f'🏚 Домой', callback_data='admin_panel'))
        return keyboard

    def text_keyboards(self, texts_list):
        keyboard = InlineKeyboardMarkup(row_width=1)
        for text_key, text_value in texts_list:
            keyboard.add(InlineKeyboardButton(
                text=f"🔧 {text_key}: {str(text_value)[:30]}...",
                callback_data=f'edit_text_button-{text_key}'
            ))
        keyboard.add(InlineKeyboardButton(text=f'🏚 Домой', callback_data='admin_panel'))
        return keyboard

    def text_msg(self, texts_list):
        keyboard = InlineKeyboardMarkup(row_width=1)
        for text_key, text_value in texts_list:
            keyboard.add(InlineKeyboardButton(
                text=f"💬 {text_key}: {str(text_value)[:30]}...",
                callback_data=f'edit_text_message-{text_key}'
            ))
        keyboard.add(InlineKeyboardButton(text=f'🏚 Домой', callback_data='admin_panel'))
        return keyboard
