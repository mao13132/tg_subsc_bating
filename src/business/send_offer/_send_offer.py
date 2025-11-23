from src.telegram.keyboard.keyboards import Admin_keyb


async def send_offer_to_audience(settings):
    message = settings['message']
    text = settings.get('text') or ''
    get_offer_btn = settings.get('get_offer_btn') or ''
    offer_id = settings.get('offer_id') or ''
    audience_ids = settings.get('audience_ids') or []

    ok_ids = []
    for uid in audience_ids:

        keyboard = Admin_keyb().offers_client(offer_id, get_offer_btn)

        try:
            res = await message.bot.send_message(int(uid), text, protect_content=True, disable_web_page_preview=True,
                                                 reply_markup=keyboard)
            ok_ids.append(str(uid))

            try:
                await message.bot.pin_chat_message(chat_id=int(uid), message_id=res['message_id'])
            except:
                pass
        except:
            pass

    return ok_ids
