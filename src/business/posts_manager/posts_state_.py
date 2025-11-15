# ---------------------------------------------
# Program by @developer_telegrams
#
#
# Version   Date        Info
# 1.0       2023    Initial Version
#
# ---------------------------------------------
import asyncio
from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from settings import LOGO
from src.business.posts_manager.message_content_codec import pack_message_content
from src.business.posts_manager.posts_keyboard import PostsKeyb
from src.telegram.sendler.sendler import Sendler_msg
from src.telegram.bot_core import BotDB

GROUP_TASKS = {}


async def posts_state(message: Message, state: FSMContext):
    await Sendler_msg.log_client_message(message)

    id_user = message.chat.id

    keyb = PostsKeyb.collect_messages_keyb()

    mg_id = getattr(message, 'media_group_id', None)
    payload = pack_message_content(message)

    data = await state.get_data()
    batch_key = data.get('batch_key')

    if not batch_key:
        from datetime import datetime
        batch_key = f'posts_sendler_{id_user}_{int(datetime.now().timestamp())}'
        await state.update_data(batch_key=batch_key, collect_count=0, mg_counters={})  # сброс счётчиков медиа-групп

    data = await state.get_data()
    mg_counters = data.get('mg_counters', {})
    mg_idx = None
    if mg_id:
        mg_idx = int(mg_counters.get(str(mg_id), 0)) + 1  # порядок в группе
        mg_counters[str(mg_id)] = mg_idx
        await state.update_data(mg_counters=mg_counters)  # сохраняем счётчик в FSM

    await BotDB.user_messages.create({
        'id_user': str(id_user),
        'content': payload,
        'batch_key': str(batch_key),
        'media_group_id': str(mg_id) if mg_id else None,
        'mg_index': mg_idx,  # индекс сообщения в медиа-группе
    })

    data = await state.get_data()
    count = int(data.get('collect_count', 0)) + 1
    await state.update_data(collect_count=count)

    _msg = "♻ Пришлите ещё сообщение или нажмите кнопку"

    msg_out = f'Получено сообщений: {count}\n\n{_msg}'

    if mg_id:
        task = GROUP_TASKS.get(id_user)

        if task:
            try:
                task.cancel()
            except:
                pass

        async def _prompt():
            await asyncio.sleep(0.8)
            await Sendler_msg.send_msg_message(message, msg_out, keyb)

        GROUP_TASKS[id_user] = asyncio.create_task(_prompt())
    else:
        await Sendler_msg().sendler_photo_message(message, LOGO, msg_out, keyb)

    return True
