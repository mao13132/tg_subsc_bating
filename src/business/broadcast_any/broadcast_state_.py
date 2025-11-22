import asyncio
from types import SimpleNamespace
from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from src.telegram.sendler.sendler import Sendler_msg
from src.telegram.bot_core import BotDB
from src.business.bet_menu.set_bet.message_content_codec import pack_message_content, send_packed_content, \
    send_records_grouped
from src.business.broadcast_any.broadcast_keyboard import BroadcastKeyb

GROUP_TASKS = {}
BROADCAST_ITEMS = {}


async def _broadcast_packed(bot, packed):
    users = await BotDB.get_all_users() or []
    sent = 0
    failed = 0
    for uid in users:
        try:
            ok = await send_packed_content(bot, int(uid), packed)
        except:
            ok = False
        if ok:
            sent += 1
        else:
            failed += 1
    return {"total": len(users), "sent": sent, "failed": failed}


async def _broadcast_records(bot, records):
    users = await BotDB.get_all_users() or []
    sent = 0
    failed = 0
    for uid in users:
        try:
            ok = await send_records_grouped(bot, int(uid), records)
        except:
            ok = False
        if ok:
            sent += 1
        else:
            failed += 1
    return {"total": len(users), "sent": sent, "failed": failed}


async def broadcast_state(message: Message, state: FSMContext):
    await Sendler_msg.log_client_message(message)

    id_user = message.chat.id

    keyb = BroadcastKeyb.collect_messages_keyb()

    mg_id = getattr(message, 'media_group_id', None)
    payload = pack_message_content(message)

    data = await state.get_data()
    batch_key = data.get('batch_key')
    if not batch_key:
        from datetime import datetime
        batch_key = f'broadcast_{id_user}_{int(datetime.now().timestamp())}'
        await state.update_data(batch_key=batch_key, collect_count=0, mg_counters={})

    data = await state.get_data()
    mg_counters = data.get('mg_counters', {})

    if mg_id:
        mg_idx = int(mg_counters.get(str(mg_id), 0)) + 1
        mg_counters[str(mg_id)] = mg_idx
        await state.update_data(mg_counters=mg_counters)

        items = BROADCAST_ITEMS.get(id_user) or []
        items.append(SimpleNamespace(content=payload, media_group_id=str(mg_id), mg_index=mg_idx, id_pk=None))
        BROADCAST_ITEMS[id_user] = items

        task = GROUP_TASKS.get(id_user)
        if task:
            try:
                task.cancel()
            except:
                pass

        async def _run():
            await asyncio.sleep(0.8)
            data2 = await state.get_data()
            count = int(data2.get('collect_count', 0)) + 1
            await state.update_data(collect_count=count)
            _msg = "♻ Пришлите ещё сообщение или нажмите кнопку"
            msg_out = f'Получено сообщений: {count}\n\n{_msg}'
            await Sendler_msg.send_msg_message(message, msg_out, keyb)

        GROUP_TASKS[id_user] = asyncio.create_task(_run())
        return True
    else:
        items = BROADCAST_ITEMS.get(id_user) or []
        items.append(SimpleNamespace(content=payload, media_group_id=None, mg_index=None, id_pk=None))
        BROADCAST_ITEMS[id_user] = items

        data2 = await state.get_data()
        count = int(data2.get('collect_count', 0)) + 1
        await state.update_data(collect_count=count)
        _msg = "♻ Пришлите ещё сообщение или нажмите кнопку"
        msg_out = f'Получено сообщений: {count}\n\n{_msg}'
        await Sendler_msg.send_msg_message(message, msg_out, keyb)
        return True
