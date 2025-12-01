# ---------------------------------------------
# Program by @developer_telegrams
#
#
# Version   Date        Info
# 1.0       2023    Initial Version
#
# ---------------------------------------------
from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from settings import LOGO
from src.business.delete_old_msg.delete_old_msg_ import delete_old_msg

from src.telegram.sendler.sendler import Sendler_msg
from src.business.text_manager.text_manager import text_manager
from src.telegram.bot_core import BotDB
from src.telegram.keyboard.keyboards import Admin_keyb
from src.utils.logger._logger import logger_msg


async def build_motivation_state(message: Message, state: FSMContext):
    await Sendler_msg.log_client_message(message)

    summa = message.text

    keyboard = Admin_keyb().back_bets_menu()

    if not str(summa).isdigit() or int(summa) < 0:
        error_ = f'❌ Вы ввели не корректную сумму предложения, пожалуйста введите ещё раз...'

        await Sendler_msg().sendler_photo_message(message, LOGO, error_, keyboard)

        return False

    id_user = message.chat.id

    data_state = await state.get_data()

    old_msg_id = data_state.get('old_msg_id', False)

    await state.finish()

    _msg_from_users = await text_manager.get_message('motivation_send')
    get_offer_btn = await text_manager.get_button_text('get_motivation')
    _msg_from_users = (_msg_from_users or '').format(summa=summa)

    # 4) Получение аудитории
    users = await BotDB.get_users_by_filter(filters={})
    total = len(users)
    sent = 0
    failed = 0
    ok_ids = []

    # 5) рассылка оффера
    for user_data in users:
        uid = user_data.id_user

        keyboard = Admin_keyb().offers_client(get_offer_btn=get_offer_btn)
        try:
            # 5) отправка и попытка закрепить сообщение
            res = await message.bot.send_message(int(uid), _msg_from_users, reply_markup=keyboard,
                                                 disable_web_page_preview=True, protect_content=True)

            sent += 1
            ok_ids.append(str(uid))
        except Exception as e:
            logger_msg(f"build_motivation_state: send error for {uid}: {e}")
            failed += 1

    try:
        from src.business.offers.offers_json import add_id_users
        await BotDB.motivations.delete_all()
        mot_data = {
            "summa": int(summa),
            "id_users": add_id_users(None, ok_ids),
        }
        await BotDB.motivations.create(mot_data)
    except Exception as e:
        logger_msg(f"Create motivation error: {e}")

    # 6) итоговый отчёт администратору
    keyboard = Admin_keyb().bet_keyboard()
    _msg = (
        f"✅ Рассылка предложений завершена\n"
        f"Подписанных (на группу) пользователей: {total}\n"
        f"Отправлено: {sent}\n"
        f"Ошибки отправки: {failed}"
    )
    await Sendler_msg.send_msg_message(message, _msg, keyboard)

    await delete_old_msg(message, id_user, old_msg_id)

    return True
