from typing import Optional

from aiogram import Bot


async def get_or_create_channel_link(bot: Bot, channel_id: int, chat=None) -> Optional[str]:
    link = None
    try:
        username = getattr(chat, 'username', None) if chat is not None else None
        if username:
            link = f'https://t.me/{username}'
        else:
            try:
                invite = await bot.create_chat_invite_link(chat_id=channel_id)
                link = invite.invite_link
            except Exception:
                try:
                    link = await bot.export_chat_invite_link(chat_id=channel_id)
                except Exception:
                    link = None
    except Exception:
        link = None

    return link
