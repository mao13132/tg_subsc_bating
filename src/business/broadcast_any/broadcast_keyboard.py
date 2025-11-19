from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


class BroadcastKeyb:
    @staticmethod
    def back_admin():
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(InlineKeyboardButton(text='🏚 Домой', callback_data='admin_panel'))
        return keyboard

    @staticmethod
    def collect_messages_keyb():
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(InlineKeyboardButton(text='✅ Отправить', callback_data='broadcast_send'))
        keyboard.add(InlineKeyboardButton(text='🗑 Очистить', callback_data='broadcast_clear'))
        keyboard.add(InlineKeyboardButton(text='🏚 Домой', callback_data='admin_panel'))
        return keyboard
        