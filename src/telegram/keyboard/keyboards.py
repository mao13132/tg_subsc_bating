from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


class Admin_keyb:
    def start_keyb(self, settings):
        access_admin = settings['access_admin']
        get_forecast_btn = settings['get_forecast_btn']

        self._start_key = InlineKeyboardMarkup(row_width=1)

        self._start_key.add(InlineKeyboardButton(text=get_forecast_btn, callback_data='get_forecast'))

        if access_admin:
            self._start_key.add(InlineKeyboardButton(text=f'⚙️ Админ панель', callback_data='admin_panel'))

        return self._start_key

    def admin_keyboard(self, is_manager):
        self._start_key = InlineKeyboardMarkup(row_width=1)

        if not is_manager:
            self._start_key.add(InlineKeyboardButton(text=f'📎 Менеджеры', callback_data='managers'))

        self._start_key.add(InlineKeyboardButton(text=f'🗂️ Настройка каналов', callback_data='chat_admin_call'))

        self._start_key.add(InlineKeyboardButton(text=f'✏️ Текста кнопок', callback_data='text_keyboards'))

        self._start_key.add(InlineKeyboardButton(text=f'✏️ Текста сообщений', callback_data='text_msg'))

        self._start_key.add(InlineKeyboardButton(text=f'🏞 Логотип к сообщениям', callback_data='logo_change_call'))

        self._start_key.add(InlineKeyboardButton(text=f'🔙 Назад', callback_data='over_state'))

        return self._start_key
