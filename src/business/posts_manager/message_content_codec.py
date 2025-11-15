# ---------------------------------------------
# Program by @developer_telegrams
#
# Универсальная упаковка/распаковка контента Telegram-сообщений
# для компактного хранения в БД и последующей отправки.
# ---------------------------------------------
import json
from typing import Optional, Dict, List, Tuple

from aiogram import Bot
from aiogram.types import Message, InlineKeyboardMarkup, ReplyKeyboardMarkup


def _safe_caption(message: Message) -> str:
    """
    Возвращает подпись/текст из сообщения, если есть.
    Предпочитаем html_text для сохранения форматирования.
    """
    try:
        exists_text = (getattr(message, 'html_text', None) or getattr(message, 'caption', None) or '').strip()
    except:
        return ''

    return exists_text


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

    # TEXT LAST — только если нет медиа
    text_content = (getattr(message, 'html_text', None) or getattr(message, 'text', None) or '').strip()
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
        messages = sorted(messages, key=lambda m: getattr(m, 'created_at', None) or 0)
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

    # На всякий случай: неизвестный тип — отправляем как текст
    await bot.send_message(chat_id, data.get('text', '') or '', reply_markup=reply_markup)

    return True
