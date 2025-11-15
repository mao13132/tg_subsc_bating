# ---------------------------------------------
# Program by @developer_telegrams
#
# Универсальная упаковка/распаковка контента Telegram-сообщений
# для компактного хранения в БД и последующей отправки.
# ---------------------------------------------
import json
from typing import Optional, Dict, List, Tuple

from aiogram import Bot
from aiogram.types import Message, InlineKeyboardMarkup, ReplyKeyboardMarkup, InputMediaPhoto, InputMediaVideo


def _safe_caption(message: Message) -> str:
    try:
        cap = getattr(message, 'caption', None)
        if cap:
            try:
                html_cap = getattr(message, 'html_caption', None)
                return (html_cap or cap).strip()
            except Exception:
                return cap.strip()
        txt = getattr(message, 'text', None)
        if txt:
            try:
                html_txt = getattr(message, 'html_text', None)
                return (html_txt or txt).strip()
            except Exception:
                return txt.strip()
        return ''
    except Exception:
        return ''


def _safe_text(message: Message) -> str:
    try:
        txt = getattr(message, 'text', None)
        if txt:
            try:
                html_txt = getattr(message, 'html_text', None)
                return (html_txt or txt).strip()
            except Exception:
                return (txt or '').strip()
        return ''
    except Exception:
        return ''


def pack_message_content(message: Message) -> str:
    """
    Сериализует контент сообщения в JSON-строку единого формата.

    Формат (минимальный, без лишних полей):
    - text:     {"type": "text",     "text": "..."}
    - photo:    {"type": "photo",    "file_id": "...", "caption": "..."}
    - video:    {"type": "video",    "file_id": "...", "caption": "..."}
    - document: {"type": "document", "file_id": "...", "file_name": "...", "caption": "..."}
    - animation:{"type": "animation","file_id": "...", "caption": "..."}

    ВАЖНО: сначала проверяем медиа по `content_type`, затем текст.
    Иначе подпись (html_text) у медиа приведёт к неверному определению типа как text.
    """
    ct = getattr(message, 'content_type', None)
    caption = _safe_caption(message)

    # MEDIA FIRST — корректная идентификация типа
    if ct == 'photo' and getattr(message, 'photo', None):
        file_id = message.photo[-1].file_id  # берём самое большое фото
        return json.dumps({
            "type": "photo",
            "file_id": file_id,
            "caption": caption,
        }, ensure_ascii=False)

    if ct == 'video' and getattr(message, 'video', None):
        return json.dumps({
            "type": "video",
            "file_id": message.video.file_id,
            "caption": caption,
        }, ensure_ascii=False)

    if ct == 'document' and getattr(message, 'document', None):
        return json.dumps({
            "type": "document",
            "file_id": message.document.file_id,
            "file_name": (message.document.file_name or ''),
            "caption": caption,
        }, ensure_ascii=False)

    if ct == 'animation' and getattr(message, 'animation', None):
        return json.dumps({
            "type": "animation",
            "file_id": message.animation.file_id,
            "caption": caption,
        }, ensure_ascii=False)

    if ct == 'voice' and getattr(message, 'voice', None):
        return json.dumps({
            "type": "voice",
            "file_id": message.voice.file_id,
            "caption": caption,
        }, ensure_ascii=False)

    if ct == 'audio' and getattr(message, 'audio', None):
        return json.dumps({
            "type": "audio",
            "file_id": message.audio.file_id,
            "caption": caption,
        }, ensure_ascii=False)

    # TEXT LAST — только если нет медиа
    text_content = _safe_text(message)
    if text_content:
        return json.dumps({
            "type": "text",
            "text": text_content,
        }, ensure_ascii=False)

    # FALLBACK — неизвестный тип, кладём подпись/пусто
    return json.dumps({
        "type": "text",
        "text": caption,
    }, ensure_ascii=False)


def try_parse_json(text: str) -> Optional[Dict]:
    """Аккуратно парсит JSON-строку. Возвращает dict или None."""
    if not text:
        return None
    try:
        data = json.loads(text)
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def collect_album_items(messages: List) -> Tuple[List[Dict], str]:
    try:
        messages = sorted(messages, key=lambda m: (getattr(m, 'mg_index', None) or 0, getattr(m, 'id_pk', None) or 0))
    except Exception:
        pass

    items: List[Dict] = []
    caption_parts: List[str] = []

    for m in messages:
        data = try_parse_json(getattr(m, 'content', '') or '') or {}
        t = data.get('type')

        if t == 'photo':
            fid = data.get('file_id', '')
            if fid:
                items.append({"type": "photo", "file_id": fid, "caption": (data.get('caption') or '').strip()})
            cap = (data.get('caption') or '').strip()
            if cap:
                caption_parts.append(cap)

        elif t == 'video':
            fid = data.get('file_id', '')
            if fid:
                items.append({"type": "video", "file_id": fid, "caption": (data.get('caption') or '').strip()})
            cap = (data.get('caption') or '').strip()
            if cap:
                caption_parts.append(cap)

        elif t == 'text':
            txt = (data.get('text') or '').strip()
            if txt:
                caption_parts.append(txt)

        elif t in ('document', 'animation'):
            cap = (data.get('caption') or '').strip()
            if cap:
                caption_parts.append(cap)

    caption = "\n".join([p for p in caption_parts if p]).strip()

    return items, caption


async def send_packed_content(bot: Bot, chat_id: int, packed: str,
                              reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | None = None) -> bool:
    """
    Отправляет пользователю контент, упакованный функцией pack_message_content.
    Если строка — обычный текст (или неправильный JSON), отправляет как text.

    Пример использования:
        payload = pack_message_content(message)
        await send_packed_content(message.bot, message.chat.id, payload)
    """
    data = try_parse_json(packed)
    if not data or 'type' not in data:
        # Обычный текст — просто отправляем
        await bot.send_message(chat_id, packed or '', reply_markup=reply_markup)
        return True

    t = data.get('type')
    if t == 'text':
        await bot.send_message(chat_id, data.get('text', '') or '', reply_markup=reply_markup)
        return True

    if t == 'photo':
        await bot.send_photo(chat_id, data.get('file_id', ''), caption=data.get('caption') or None,
                             reply_markup=reply_markup)
        return True

    if t == "video":
        await bot.send_video(chat_id, data.get('file_id', ''), caption=data.get('caption') or None,
                             reply_markup=reply_markup)
        return True

    if t == 'document':
        await bot.send_document(chat_id, data.get('file_id', ''), caption=data.get('caption') or None,
                                reply_markup=reply_markup)
        return True

    if t == 'animation':
        await bot.send_animation(chat_id, data.get('file_id', ''), caption=data.get('caption') or None,
                                 reply_markup=reply_markup)
        return True

    if t == 'voice':
        await bot.send_voice(chat_id, data.get('file_id', ''), caption=data.get('caption') or None,
                             reply_markup=reply_markup)
        return True

    if t == 'audio':
        await bot.send_audio(chat_id, data.get('file_id', ''), caption=data.get('caption') or None,
                             reply_markup=reply_markup)
        return True

    # На всякий случай: неизвестный тип — отправляем как текст
    await bot.send_message(chat_id, data.get('text', '') or '', reply_markup=reply_markup)

    return True


def _to_input_media(items: List[Dict], caption: str) -> List:
    media = []
    for i, it in enumerate(items):
        if it.get('type') == 'photo':
            media.append(InputMediaPhoto(media=it.get('file_id'), caption=caption if i == 0 and caption else None))
        elif it.get('type') == 'video':
            media.append(InputMediaVideo(media=it.get('file_id'), caption=caption if i == 0 and caption else None))
    return media


async def send_media_group_records(bot: Bot, chat_id: int, messages: List) -> bool:
    items, caption = collect_album_items(messages)
    media = _to_input_media(items, caption)
    if media:
        await bot.send_media_group(chat_id, media)
        return True
    return False


async def send_records_grouped(bot: Bot, chat_id: int, records: List,
                               reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | None = None) -> bool:
    groups: Dict[Optional[str], List] = {}
    for r in records or []:
        gid = getattr(r, 'media_group_id', None)
        groups.setdefault(gid, []).append(r)
    ok = True
    for gid, msgs in groups.items():
        if gid:
            sent = await send_media_group_records(bot, chat_id, msgs)
            ok = ok and sent
        else:
            for r in msgs:
                packed = getattr(r, 'content', '') or ''
                await send_packed_content(bot, chat_id, packed, reply_markup=reply_markup)
    return ok
