import json
from types import SimpleNamespace
from typing import Optional

from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup

from src.telegram.bot_core import BotDB
from src.business.bet_menu.set_bet.message_content_codec import send_records_grouped


async def send_offer_content_to_user(bot: Bot,
                                     chat_id: int,
                                     offer_id: int,
                                     reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | None = None) -> bool:
    offer = await BotDB.offers.read_by_id(int(offer_id))
    if not offer:
        return False

    try:
        data_list = json.loads(getattr(offer, 'message_json', '') or '[]')
    except Exception:
        data_list = []

    records = []
    for it in data_list or []:
        content = (it.get('content') or '')
        mg_id = it.get('media_group_id')
        mg_index = it.get('mg_index')
        records.append(SimpleNamespace(content=content, media_group_id=mg_id, mg_index=mg_index, id_pk=None))

    if not records:
        return False

    return await send_records_grouped(bot, int(chat_id), records, reply_markup=reply_markup)
    