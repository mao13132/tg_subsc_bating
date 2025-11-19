# ---------------------------------------------
# Утилита парсинга даты/времени от пользователя
# Поддержка разных форматов и относительных выражений
# ---------------------------------------------
from __future__ import annotations

import re
from datetime import datetime, timedelta
from typing import Optional, Dict, Any


def _norm_dt_str(dt: datetime) -> str:
    return dt.strftime('%d.%m.%Y %H:%M')


def parse_user_datetime(text: str, now: Optional[datetime] = None) -> Dict[str, Any]:
    """
    Парсит дату/время из пользовательского ввода.

    Поддерживаемые варианты:
    - "DD.MM.YYYY HH:MM"
    - "DD.MM.YY HH:MM" (год интерпретируется как 2000+YY)
    - "DD.MM HH:MM" (год берётся текущий)
    - "YYYY-MM-DD HH:MM" или "YYYY/MM/DD HH:MM"
    - "HH:MM DD.MM.YYYY"
    - "сегодня HH:MM", "завтра HH:MM"
    - "через N мин", "через N минуты", "через N час/часа/часов"

    Возвращает словарь:
    {
      'ok': bool,
      'dt': datetime | None,
      'dt_str': str | None,  # нормализованная строка dd.mm.yyyy HH:MM
      'error': str | None,
      'code': str | None     # 'invalid_format' | 'past_time'
    }
    """
    now = now or datetime.now()
    s = (text or '').strip().lower()

    def _past_check(dt_: datetime) -> Dict[str, Any]:
        if dt_ <= now:
            return {
                'ok': False,
                'dt': None,
                'dt_str': None,
                'error': '❌ Дата/время уже в прошлом. Введите будущую дату.',
                'code': 'past_time'
            }
        return {
            'ok': True,
            'dt': dt_,
            'dt_str': _norm_dt_str(dt_),
            'error': None,
            'code': None
        }

    # через N минут/часов
    m_rel = re.fullmatch(r"через\s+(\d{1,4})\s*(минут(?:ы)?|мин|час(?:а|ов)?|ч)", s)
    if m_rel:
        n = int(m_rel.group(1))
        unit = m_rel.group(2)
        if 'мин' in unit:
            dt = now + timedelta(minutes=n)
        else:
            dt = now + timedelta(hours=n)
        return _past_check(dt)

    # сегодня/завтра HH:MM
    m_day = re.fullmatch(r"(сегодня|завтра)(?:\s*в)?\s*(\d{1,2}):(\d{2})", s)
    if m_day:
        word = m_day.group(1)
        hh = int(m_day.group(2))
        mm = int(m_day.group(3))
        base = now.date()
        if word == 'завтра':
            base = (now + timedelta(days=1)).date()
        dt = datetime(base.year, base.month, base.day, hh, mm)
        return _past_check(dt)

    # DD.MM.YYYY HH:MM  | DD/MM/YYYY HH:MM | DD-MM-YYYY HH:MM
    m1 = re.fullmatch(r"(\d{1,2})[\.\-/](\d{1,2})[\.\-/](\d{2,4})\s+(\d{1,2}):(\d{2})", s)
    if m1:
        dd, mm_, yy, hh, mn = map(int, m1.groups())
        if yy < 100:
            yy = 2000 + yy
        try:
            dt = datetime(yy, mm_, dd, hh, mn)
            return _past_check(dt)
        except ValueError:
            pass

    # YYYY-MM-DD HH:MM | YYYY/MM/DD HH:MM | YYYY.MM.DD HH:MM
    m2 = re.fullmatch(r"(\d{4})[\.\-/](\d{1,2})[\.\-/](\d{1,2})\s+(\d{1,2}):(\d{2})", s)
    if m2:
        yy, mm_, dd, hh, mn = map(int, m2.groups())
        try:
            dt = datetime(yy, mm_, dd, hh, mn)
            return _past_check(dt)
        except ValueError:
            pass

    # DD.MM HH:MM (год текущий)
    m3 = re.fullmatch(r"(\d{1,2})[\.\-/](\d{1,2})\s+(\d{1,2}):(\d{2})", s)
    if m3:
        dd, mm_, hh, mn = map(int, m3.groups())
        try:
            dt = datetime(now.year, mm_, dd, hh, mn)
            return _past_check(dt)
        except ValueError:
            pass

    # HH:MM DD.MM.YYYY
    m4 = re.fullmatch(r"(\d{1,2}):(\d{2})\s+(\d{1,2})[\.\-/](\d{1,2})[\.\-/](\d{2,4})", s)
    if m4:
        hh, mn, dd, mm_, yy = map(int, m4.groups())
        if yy < 100:
            yy = 2000 + yy
        try:
            dt = datetime(yy, mm_, dd, hh, mn)
            return _past_check(dt)
        except ValueError:
            pass

    return {
        'ok': False,
        'dt': None,
        'dt_str': None,
        'error': '❌ Не удалось распознать дату/время. Примеры: 25.12.2025 14:30, завтра 09:00, через 2 часа',
        'code': 'invalid_format'
    }
