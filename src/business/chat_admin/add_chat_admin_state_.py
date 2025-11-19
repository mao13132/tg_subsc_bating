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

from src.business.chat_admin.add_chat_keyboard import ChatAdminKeyb
from src.telegram.bot_core import BotDB

from settings import SETTINGS_CHATS, LOGO
from src.telegram.sendler.sendler import Sendler_msg


async def add_chat_admin_state(message: Message, state: FSMContext):
    await Sendler_msg.log_client_message(message)

    channel_id_text = message.text.strip()

    id_user = message.chat.id

    keyboard = ChatAdminKeyb().back_add_chat()

    try:
        channel_id = int(channel_id_text)
        if channel_id >= 0:
            error_msg = f'❌ Вы ввели ID не в верном формате. попробуйте ещё раз'

            await Sendler_msg.send_msg_message(message, error_msg, keyboard)

            return False

    except ValueError:
        error_msg = f'❌ Вы ввели ID не в верном формате. попробуйте ещё раз'

        await Sendler_msg.send_msg_message(message, error_msg, keyboard)

        return False

    # Получаем данные состояния
    state_data = await state.get_data()

    try:
        target = state_data['target']

        old_msg_id = state_data['old_msg_id']
    except:
        error_ = f'Кнопка устарела, попробуйте заново'

        await Sendler_msg.send_msg_message(message, error_, None)

        return False

    # Проверяем, что бот имеет доступ к каналу
    try:
        chat = await message.bot.get_chat(channel_id)
        bot_member = await message.bot.get_chat_member(channel_id, message.bot.id)

        if bot_member.status not in ['administrator', 'creator']:
            msg = (
                f"❌ Бот должен быть администратором канала {channel_id}.\n"
                "Добавьте бота в канал как администратора и попробуйте еще раз"
            )

            await Sendler_msg.send_msg_message(message, msg, keyboard)

            if old_msg_id:
                try:
                    # Удаляем предыдущее сообщение бота
                    await message.bot.delete_message(id_user, old_msg_id)
                except Exception:
                    # Игнорируем ошибки удаления (сообщение могло быть уже удалено)
                    pass

                try:
                    # Удаляем сообщение пользователя с кодом
                    await message.delete()
                except Exception:
                    # Игнорируем ошибки удаления
                    pass

            return False

    except Exception as e:
        msg = (
            f"❌ Не удалось получить доступ к каналу {channel_id}. Убедитесь, что:\n"
            "1. ID канала указан правильно\n"
            "2. Бот добавлен в канал\n"
            "3. Бот имеет права администратора\n\n"
            "Попробуйте еще раз"
        )

        await Sendler_msg.send_msg_message(message, msg, keyboard)

        if old_msg_id:
            try:
                # Удаляем предыдущее сообщение бота
                await message.bot.delete_message(id_user, old_msg_id)
            except Exception:
                # Игнорируем ошибки удаления (сообщение могло быть уже удалено)
                pass

            try:
                # Удаляем сообщение пользователя с кодом
                await message.delete()
            except Exception:
                # Игнорируем ошибки удаления
                pass

        return

    # Завершаем состояние FSM
    save_chat = await BotDB.update_settings(key=target, value=str(channel_id))

    status_text = f'✅ Успешно добавил чат/канал' if save_chat else f'❌ Не смог добавить чат/канал'

    await state.finish()

    keyboard = ChatAdminKeyb().chat_admin_btns(SETTINGS_CHATS)

    await Sendler_msg.send_msg_message(message, status_text, keyboard)

    if old_msg_id:
        try:
            # Удаляем предыдущее сообщение бота
            await message.bot.delete_message(id_user, old_msg_id)
        except Exception:
            # Игнорируем ошибки удаления (сообщение могло быть уже удалено)
            pass

        try:
            # Удаляем сообщение пользователя с кодом
            await message.delete()
        except Exception:
            # Игнорируем ошибки удаления
            pass

    return True
