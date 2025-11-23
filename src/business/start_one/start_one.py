# ---------------------------------------------
# Program by @developer_telegrams
#
#
# Version   Date        Info
# 1.0       2023    Initial Version
#
# ---------------------------------------------
from settings import LOGO, ADMIN
from src.business.get_data_user.get_data_user import get_data_user
from src.business.managers.check_manager import check_manager
from src.business.text_manager.text_manager import text_manager
from src.telegram.keyboard.keyboards import Admin_keyb

from src.telegram.sendler.sendler import Sendler_msg

from aiogram.types import Message, ChatActions, ReplyKeyboardMarkup, KeyboardButton

from src.telegram.bot_core import BotDB
from src.business.payments.unpaid_notifier import notify_unpaid_if_needed

from aiogram.dispatcher import FSMContext


async def start_one(message: Message, state: FSMContext, skip_btn_menu=True):
    await state.finish()

    try:
        await message.bot.send_chat_action(message.chat.id, ChatActions.TYPING)
    except:
        pass

    id_user = message.chat.id

    access_admin = False

    is_manager = await check_manager(message)

    if str(id_user) in ADMIN or is_manager:
        access_admin = True

    data_user = await get_data_user(message)

    new_user = await BotDB.check_or_add_user(id_user, data_user)

    await Sendler_msg.log_client_message(message)

    # Проверка на не оплаченный счёт
    if await notify_unpaid_if_needed(message, access_admin=True):
        return False

    get_forecast_btn = await text_manager.get_button_text('get_forecast')

    settings_start_keyboard = {'access_admin': access_admin, 'get_forecast_btn': get_forecast_btn}

    keyb = Admin_keyb().start_keyb(settings_start_keyboard)

    start_message = await text_manager.get_message('welcome')

    await Sendler_msg().sendler_photo_message(message, LOGO, start_message, keyb)

    if not skip_btn_menu:
        reply_keyb = ReplyKeyboardMarkup(resize_keyboard=True)
        reply_keyb.add(KeyboardButton('ПОЛУЧИТЬ ПРОГНОЗ🌎🫷🏻'), KeyboardButton('Задать вопрос'))
        await message.bot.send_message(id_user, 'Меню', reply_markup=reply_keyb, disable_web_page_preview=True, protect_content=True)

    return True
