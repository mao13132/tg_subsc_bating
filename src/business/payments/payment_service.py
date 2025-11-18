from typing import Optional, Dict

from settings import SHOPKEY, SECKEY
from src.utils.logger._logger import logger_msg
from src.telegram.bot_core import BotDB
from src.business.payments_api.create_payment_ckassa import CKassaPayment


async def create_ckassa_payment(uid: str, amount_rub: int,
                                service_code: str = '1000-13864-2',
                                name_shop: str = 'Основной Магазин') -> Dict[str, str]:
    """
    Создаёт платёж в CKassa для пользователя.

    Возвращает словарь с ключами 'regPayNum' и 'payUrl'.
    """
    amount_kop = int(amount_rub) * 100
    payment_data = {
        "serviceCode": service_code,
        "amount": int(amount_kop),
        "comission": 0,
        "properties": [
            {"name": "ЛИЦЕВОЙ_СЧЕТ", "value": str(uid)}
        ]
    }

    try:
        res = await CKassaPayment(payment_data).create_payment(name_shop, SHOPKEY, SECKEY)
        return {"regPayNum": res["regPayNum"], "payUrl": res["payUrl"]}
    except Exception as e:
        logger_msg(f"CKassa: ошибка создания платежа для {uid}: {e}")
        raise


async def record_payment(uid: str, amount_rub: int, reg_pay_num: str, link: str, status: str) -> Optional[int]:
    """
    Записывает платёж в БД.

    Возвращает id_pk созданной записи или None.
    """
    try:
        return await BotDB.payments.create({
            'id_user': str(uid),
            'amount': int(amount_rub),
            'reg_pay_num': reg_pay_num,
            'status': status,
            'link': link
        })
    except Exception as e:
        logger_msg(f"SQL: ошибка записи платежа для {uid}: {e}")
        return None


BAD_STATUSES = (
    'expired', 'error', 'created_error', 'rejected', 'refunded', 'unknown'
)


def is_payment_bad(payment) -> bool:
    status = getattr(payment, 'status', '')
    link = getattr(payment, 'link', '') or ''
    return (status in BAD_STATUSES) or (link == 'bad')


async def ensure_payment_link(uid: str) -> Dict[str, Optional[str]]:
    latest = await BotDB.payments.read_latest_by_user(str(uid))
    if not latest:
        return {'link': None, 'amount': None, 'recreated': False, 'status': None}

    link = getattr(latest, 'link', '') or ''
    amount = int(getattr(latest, 'amount', 0) or 0)

    if is_payment_bad(latest):
        created = await create_ckassa_payment(str(uid), amount)
        await record_payment(str(uid), amount, created['regPayNum'], created['payUrl'], 'created')
        return {'link': created['payUrl'], 'amount': amount, 'recreated': True, 'status': 'created'}

    return {'link': link, 'amount': amount, 'recreated': False, 'status': getattr(latest, 'status', None)}
