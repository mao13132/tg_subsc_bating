# ---------------------------------------------
# Program by @developer_telegrams
#
#
# Version   Date        Info
# 1.0       2023    Initial Version
#
# ---------------------------------------------
from aiogram.types import Message
from typing import Optional
from src.telegram.bot_core import BotDB
from src.utils.logger._logger import logger_msg


async def delete_old_msg(message: Message, id_user, old_msg_id, no_del_message=False):
    if not old_msg_id:
        return False

    try:
        await message.bot.delete_message(id_user, old_msg_id)
    except:
        pass

    if not no_del_message:
        try:
            await message.delete()
        except:
            pass

    return True


async def delete_messages_by_batch_key(bot, bot_db: BotDB, batch_key: str, remove_registry: bool = True) -> int:
    """
    Массовое удаление всех сообщений, записанных в реестр по одному `batch_key`.

    Использование:
    - Сначала сохраняем все сообщения (альбом, reply и т.д.) в `message_registry`
      под единым ключом (например: "install_request:{id}:purple_album").
    - Затем вызываем эту функцию, чтобы удалить всё разом.

    Args:
        bot: Экземпляр бота для вызова delete_message.
        bot_db: Экземпляр BotDB с доступом к `message_registry` CRUD.
        batch_key: Ключ группировки записей для удаления.
        remove_registry: Если True — после удаления сообщений удаляем и записи из реестра.

    Returns:
        Количество успешно удалённых сообщений (по попыткам удаления).
    """
    if not batch_key:
        return 0

    deleted_count = 0

    try:
        # 1) Получаем все записи по ключу
        records = await bot_db.message_registry.read_by_filter({'batch_key': batch_key})

        # 2) Удаляем каждое сообщение
        for rec in records:
            chat_id_str = getattr(rec, 'chat_id', None)
            msg_id = getattr(rec, 'message_id', None)
            if not chat_id_str or msg_id is None:
                continue

            try:
                await bot.delete_message(int(chat_id_str), int(msg_id))
                deleted_count += 1
            except Exception as es_del:
                # Не падаем, логируем и идём дальше
                logger_msg(f"Не удалось удалить сообщение {chat_id_str}/{msg_id}: {es_del}")

        # 3) Очищаем реестр (опционально)
        if remove_registry:
            try:
                await bot_db.message_registry.delete_by_batch_key(batch_key)
            except Exception as es_rm:
                logger_msg(f"Не удалось очистить записи реестра для '{batch_key}': {es_rm}")

    except Exception as es:
        logger_msg(f"Сбой массового удаления по batch_key '{batch_key}': {es}")

    return deleted_count
