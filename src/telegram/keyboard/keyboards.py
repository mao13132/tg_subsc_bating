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

        self._start_key.add(InlineKeyboardButton(text=f'🎲 Настройка прогноза', callback_data='bet_menu'))

        self._start_key.add(InlineKeyboardButton(text=f'🗂️ Настройка каналов', callback_data='chat_admin_call'))

        self._start_key.add(InlineKeyboardButton(text=f'✏️ Текста кнопок', callback_data='text_keyboards'))

        self._start_key.add(InlineKeyboardButton(text=f'✏️ Текста сообщений', callback_data='text_msg'))

        self._start_key.add(InlineKeyboardButton(text=f'🏞 Логотип к сообщениям', callback_data='logo_change_call'))

        self._start_key.add(InlineKeyboardButton(text=f'🔙 Назад', callback_data='over_state'))

        return self._start_key

    def bet_keyboard(self):
        self._start_key = InlineKeyboardMarkup(row_width=1)

        self._start_key.add(InlineKeyboardButton(text=f'⌨️ Загрузить прогноз', callback_data='set_bet'))

        self._start_key.add(InlineKeyboardButton(text=f'🗑 Очистить прогноз', callback_data='clear_bet'))

        self._start_key.add(InlineKeyboardButton(text=f'🗞 Прислать мне', callback_data='send_me_bet'))

        self._start_key.add(InlineKeyboardButton(text=f'✅ Выслать счета', callback_data='send_payments'))

        self._start_key.add(InlineKeyboardButton(text=f'♻️ Повторить предложения', callback_data='repid_payments'))

        self._start_key.add(InlineKeyboardButton(text=f'🏚 Домой', callback_data='admin_panel'))

        return self._start_key

    def back_bets_menu(self):
        self._start_key = InlineKeyboardMarkup(row_width=1)

        self._start_key.add(InlineKeyboardButton(text=f'🔙 Назад', callback_data='bet_menu'))

        self._start_key.add(InlineKeyboardButton(text=f'🏚 Домой', callback_data='admin_panel'))

        return self._start_key

    def new_back_bets_menu(self):
        self._start_key = InlineKeyboardMarkup(row_width=1)

        self._start_key.add(InlineKeyboardButton(text=f'⌨️ Загрузить прогноз', callback_data='set_bet'))

        self._start_key.add(InlineKeyboardButton(text=f'🔙 Назад', callback_data='bet_menu'))

        return self._start_key

    def wait_keyb(self):
        self._start_key = InlineKeyboardMarkup(row_width=1)

        self._start_key.add(InlineKeyboardButton(text=f'⏳ Идёт создание и рассылка платежей', callback_data='wait'))

        return self._start_key

    def approve_send_summa(self):
        self._start_key = InlineKeyboardMarkup(row_width=1)

        self._start_key.add(InlineKeyboardButton(text=f'✅ Подтверждаю', callback_data='approve_summa'))

        self._start_key.add(InlineKeyboardButton(text=f'🔙 Назад', callback_data='bet_menu'))

        self._start_key.add(InlineKeyboardButton(text=f'🏚 Домой', callback_data='admin_panel'))

        return self._start_key

    def finish_timer_bet(self):
        self._start_key = InlineKeyboardMarkup(row_width=1)

        self._start_key.add(InlineKeyboardButton(text=f'✅ Подтверждаю', callback_data='approve_timer_bet'))

        self._start_key.add(InlineKeyboardButton(text=f'🔙 Назад', callback_data='bet_menu'))

        self._start_key.add(InlineKeyboardButton(text=f'🏚 Домой', callback_data='admin_panel'))

        return self._start_key

    def back_main_menu(self, back_text):
        self._start_key = InlineKeyboardMarkup(row_width=1)

        self._start_key.add(InlineKeyboardButton(text=back_text, callback_data='over_state'))

        return self._start_key

    def no_paid(self, access_admin, pay_text=None, client_payment_link=None):
        self._start_key = InlineKeyboardMarkup(row_width=1)

        if pay_text and client_payment_link:
            self._start_key.add(InlineKeyboardButton(text=pay_text, url=client_payment_link))

        if access_admin:
            self._start_key.add(InlineKeyboardButton(text=f'⚙️ Админ панель', callback_data='admin_panel'))

        return self._start_key

    def payment_keyb(self, btn_text, client_payment_link):
        self._start_key = InlineKeyboardMarkup(row_width=1)

        self._start_key.add(InlineKeyboardButton(text=btn_text, url=client_payment_link))

        return self._start_key

    def approve_send_forecast(self):
        self._start_key = InlineKeyboardMarkup(row_width=1)

        self._start_key.add(InlineKeyboardButton(text=f'✅ Подтверждаю', callback_data='approve_forecast'))

        self._start_key.add(InlineKeyboardButton(text=f'🔙 Назад', callback_data='bet_menu'))

        self._start_key.add(InlineKeyboardButton(text=f'🏚 Домой', callback_data='admin_panel'))

        return self._start_key

    def good_payments(self, get_forecast_btn, admin_text, admin_link):
        self._start_key = InlineKeyboardMarkup(row_width=1)

        self._start_key.add(InlineKeyboardButton(text=get_forecast_btn, callback_data='get_forecast'))

        self._start_key.add(InlineKeyboardButton(text=admin_text, url=admin_link))

        return self._start_key
