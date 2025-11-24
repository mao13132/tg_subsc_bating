from src.utils.logger._logger import logger_msg
from src.telegram.bot_core import BotDB
from src.business.bet_menu.set_bet.message_content_codec import send_records_grouped
from types import SimpleNamespace
import json


async def send_offer_to_audience(settings):
    message = settings['message']
    offer_id = settings.get('offer_id') or ''
    audience_ids = settings.get('audience_ids') or []

    offer = await BotDB.offers.read_by_id(int(offer_id))
    if not offer:
        return []

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
        return []

    ok_ids = []
    for user_data in audience_ids:
        uid = user_data.id_user
        try:
            sent = await send_records_grouped(message.bot, int(uid), records, reply_markup=None)
            if sent:
                ok_ids.append(str(uid))
        except Exception as es:
            error_ = f'Не смог отправить контент оффера "{str(uid)}" по причине: "{es}"'
            logger_msg(error_)
            continue

    return ok_ids
