import sys
import traceback
from typing import Optional, Dict
from datetime import datetime

from settings import SHOPKEY, SECKEY, SERVCODE, PAYMENT_TIMEOUT_MINUTES
from src.utils.logger._logger import logger_msg
from src.telegram.bot_core import BotDB
from src.business.payments_api.create_payment_ckassa import CKassaPayment
from src.business.payments_api.order_best_before import order_best_before


async def create_ckassa_payment(uid: str, amount_rub: int,
                                service_code: str = SERVCODE,
                                name_shop: str = 'Основной Магазин') -> Dict[str, str]:
    """
    Создаёт платёж в CKassa для пользователя.

    Логика:
    1) Конвертируем сумму в копейки (CKassa ожидает amount в копейках).
    2) Собираем payload: serviceCode, amount, payType, properties с идентификатором пользователя.
    3) Делаем запрос через CKassaPayment.create_payment с shop/secret ключами.
    4) Валидируем ответ: извлекаем regPayNum и payUrl, иначе логируем ошибку.
    5) Возвращаем словарь с ключами 'regPayNum' и 'payUrl'.
    """
    # 1) Сумма в копейках
    amount_kop = int(amount_rub) * 100
    payment_data = {
        "serviceCode": service_code,
        "amount": int(amount_kop),
        "comission": 0,
        "payType": 'sbp',
        # "orderBestBefore": order_best_before(),
        # 2) Доп. свойства для сопоставления платежей в CKassa
        "properties": [
            {"name": "ID", "value": str(uid)},
            {"name": "telegramID", "value": str(uid)},
        ]
    }

    try:
        # 3) Запрос на создание платежа
        res = await CKassaPayment(payment_data).create_payment(name_shop, SHOPKEY, SECKEY)

        try:
            # 4) Приведение ответа к ожидаемому виду
            response = {"regPayNum": res["regPayNum"], "payUrl": res["payUrl"]}
        except Exception as es:
            error_ = f'Ошибка при проверки платежа "{es}"'

            logger_msg(error_)

            return False

        return response
    except Exception as e:
        logger_msg(f"CKassa: ошибка создания платежа для {uid}: {e}\n"
                   f"{''.join(traceback.format_exception(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2]))}")
        raise


async def record_payment(uid: str,
                         amount_rub: int,
                         reg_pay_num: str,
                         link: str,
                         status: str,
                         offer_id: Optional[int] = None) -> Optional[int]:
    """
    Записывает платёж в БД.

    Логика:
    1) Формируем словарь данных записи платежа.
    2) Опционально добавляем offer_id для привязки к офферу.
    3) Выполняем INSERT через CRUD-слой и возвращаем первичный ключ.
    4) В случае ошибки логируем и возвращаем None.
    """
    data = {
        'id_user': str(uid),
        'amount': int(amount_rub),
        'reg_pay_num': reg_pay_num,
        'status': status,
        'link': link,
    }
    if offer_id is not None:
        data['offer_id'] = int(offer_id)

    try:
        return await BotDB.payments.create(data)
    except Exception as e:
        logger_msg(f"SQL: ошибка записи платежа для {uid}: {e}")
        return None


BAD_STATUSES = (
    'expired', 'error', 'created_error', 'rejected', 'refunded', 'unknown'
)


def is_payment_bad(payment) -> bool:
    """
    Проверяет, что платеж «плохой» и ссылку надо заменять.

    Логика:
    1) Берём статус и ссылку из объекта платежа.
    2) Возвращаем True если статус в BAD_STATUSES или link == 'bad'.
    """
    status = getattr(payment, 'status', '')
    link = getattr(payment, 'link', '') or ''
    return (status in BAD_STATUSES) or (link == 'bad')


async def ensure_payment_link(uid: str, preferred_amount_rub: Optional[int] = None) -> Dict[str, Optional[str]]:
    """
    Гарантирует актуальную ссылку на оплату для пользователя.

    Логика:
    1) Читаем последний платеж пользователя.
    2) Если платежа нет — возвращаем пустую структуру.
    3) Извлекаем link и последнюю сумму amount_latest.
    4) Вычисляем amount_effective: берём preferred_amount_rub если она валидна (>0), иначе последнюю сумму.
    5) Если платеж «плохой» — создаём новый платёж по amount_effective, записываем его в БД и возвращаем новую ссылку.
    6) Если платеж «хороший» — возвращаем текущую ссылку и сумму без пересоздания.
    """
    latest = await BotDB.payments.read_latest_by_user(str(uid))
    if not latest:
        return {'link': None, 'amount': None, 'recreated': False, 'status': None}

    link = getattr(latest, 'link', '') or ''
    amount_latest = int(getattr(latest, 'amount', 0) or 0)
    created_at = getattr(latest, 'created_at', None)
    try:
        ttl_seconds = int(PAYMENT_TIMEOUT_MINUTES) * 60
    except Exception:
        ttl_seconds = 60
    # 4) Сумма для пересоздания, если потребуется
    amount_effective = (
        int(preferred_amount_rub)
        if (preferred_amount_rub is not None and str(preferred_amount_rub).isdigit() and int(preferred_amount_rub) > 0)
        else amount_latest
    )

    # Принудительно истекает по TTL: пересоздаём счёт по эффективной сумме
    if created_at and (datetime.utcnow() - created_at).total_seconds() > ttl_seconds:
        try:
            await BotDB.payments.update_by_id(getattr(latest, 'id_pk', 0), {'status': 'expired'})
        except Exception:
            pass
        created = await create_ckassa_payment(str(uid), amount_effective)
        await record_payment(str(uid), amount_effective, created['regPayNum'], created['payUrl'], 'created')
        return {'link': created['payUrl'], 'amount': amount_effective, 'recreated': True, 'status': 'created'}

    if is_payment_bad(latest):
        # 5) Пересоздаём платёж по эффективной сумме
        created = await create_ckassa_payment(str(uid), amount_effective)
        await record_payment(str(uid), amount_effective, created['regPayNum'], created['payUrl'], 'created')
        return {'link': created['payUrl'], 'amount': amount_effective, 'recreated': True, 'status': 'created'}

    # 6) Возвращаем текущую рабочую ссылку
    return {'link': link, 'amount': amount_latest, 'recreated': False, 'status': getattr(latest, 'status', None)}

# async def ensure_offer_payment(uid: str,
#                                offer_id: int,
#                                amount_rub: int,
#                                service_code: str = '1000-13864-2',
#                                name_shop: str = 'Основной Магазин') -> Dict[str, Optional[str]]:
#     payments = await BotDB.payments.read_by_filter({
#         'id_user': str(uid),
#         'amount': int(amount_rub),
#         'offer_id': int(offer_id)
#     })
#
#     latest = None
#     if payments:
#         try:
#             latest = sorted(payments, key=lambda p: getattr(p, 'created_at', None) or 0, reverse=True)[0]
#         except Exception:
#             latest = payments[-1]
#
#     if latest:
#         link = getattr(latest, 'link', '') or ''
#         status = getattr(latest, 'status', '') or ''
#         invalid_link = link in ('', 'created')
#         if not is_payment_bad(latest) and not invalid_link:
#             return {
#                 'link': link,
#                 'amount': int(amount_rub),
#                 'recreated': False,
#                 'status': status,
#                 'regPayNum': getattr(latest, 'reg_pay_num', None)
#             }
#
#     created = await create_ckassa_payment(str(uid), int(amount_rub), service_code=service_code, name_shop=name_shop)
#     await record_payment(str(uid), int(amount_rub), created['regPayNum'], created['payUrl'], 'created',
#                          offer_id=int(offer_id))
#     return {
#         'link': created['payUrl'],
#         'amount': int(amount_rub),
#         'recreated': bool(latest),
#         'status': 'created',
#         'regPayNum': created['regPayNum']
#     }
