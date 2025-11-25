# ---------------------------------------------
# CKassa Payment Create (Shop API)
# ---------------------------------------------

import asyncio
import httpx
import backoff

from settings import DOMAIN_PAYMENT, SERVCODE
from src.utils.logger._logger import logger_msg


class CKassaPayment:
    """
    Создание платежа в CKassa (Shop API)
    """

    def __init__(self, payment_data: dict):
        self.payment_data = payment_data

    @backoff.on_exception(
        backoff.expo,
        (httpx.RequestError, httpx.TimeoutException),
        max_tries=5,
        jitter=None
    )
    async def _create_payment(self, shop_token: str, sec_key: str):
        """
        Делает запрос на создание платежа CKassa.

        Returns:
            dict | '-1'
        """
        url = f"https://{DOMAIN_PAYMENT}/api-shop/do/payment/anonymous"

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        async with httpx.AsyncClient(timeout=httpx.Timeout(180.0)) as client:
            try:
                response = await client.post(
                    url,
                    headers=headers,
                    json=self.payment_data,
                    auth=httpx.BasicAuth(shop_token, sec_key)
                )

                try:
                    data = response.json()
                except Exception:
                    data = {}

                if response.status_code in (200, 201) and not data:
                    logger_msg("CKassa: Сервер вернул пустой JSON")

                return data

            except Exception as e:
                logger_msg(f"CKassa: Ошибка при создании платежа: {e}")
                return '-1'

    async def check_error(self, data: dict, name_shop: str):
        """
        Проверка ответа API.
        """
        if not isinstance(data, dict):
            logger_msg(f"CKassa Error: Некорректный формат ответа {name_shop}")
            return True

        err_fields = ('error', 'errors', 'message', 'status', 'code', 'detail')
        messages = []

        for k in err_fields:
            if k in data and data[k]:
                messages.append(str(data[k]))

        if messages:
            msg = " | ".join(messages)
            logger_msg(f"CKassa Error: {msg}")

            low = msg.lower()
            if "limit" in low or "too many" in low or "unknown error" in low:
                return '-1'

            return True

        return False

    async def create_payment(self, name_shop: str, shop_token: str, sec_key: str):
        """
        Основной метод создания платежа.
        """
        for attempt in range(5):

            data = await self._create_payment(shop_token, sec_key)

            if data == '-1':
                logger_msg(f"Попытка {attempt + 1}/5: Ошибка соединения, ждем 15 сек")
                await asyncio.sleep(15)
                continue

            if not data:
                logger_msg(f"Попытка {attempt + 1}/5: Пустой ответ, ждем 1 сек")
                await asyncio.sleep(1)
                continue

            is_err = await self.check_error(data, name_shop)

            if is_err == '-1':
                logger_msg(f"Попытка {attempt + 1}/5: Лимит/таймаут, ждем 15 сек")
                await asyncio.sleep(15)
                continue

            if is_err:
                logger_msg(f"CKassa: Ошибка платежа для {name_shop}")
                return False

            # --- УСПЕХ ---
            try:
                if "regPayNum" in data:
                    pid = data["regPayNum"]
                    print(f'Платёж создан для "{name_shop}": {pid}')
                    return data

                print(f'Платёж создан (нет regPayNum) для "{name_shop}": {data}')
                return data

            except Exception as e:
                logger_msg(f"CKassa: Ошибка структуры ответа: {e}")
                logger_msg(f"Ответ: {data}")
                await asyncio.sleep(1)
                continue

        logger_msg(f"CKassa: Не удалось создать платёж для {name_shop}")
        return False


if __name__ == "__main__":
    async def _run_test():
        payment_data = {
            "serviceCode": SERVCODE,
            "amount": 5000,
            "comission": 0,
            "properties": [
                {"name": "ID", "value": "141"},  # Идентификатор
                # {"name": "PHONE", "value": "79170000000"},  # Телефон
                {"name": "telegramID", "value": "1234567"}  # Telegram ID
            ]
            # "properties": [
            #     "14",  # ID (Идентификатор клиента)
            #     "79170000000",  # PHONE (Телефон)
            #     "1422194909"  # telegramID (Telegram User ID)
            # ]
        }

        from settings import SHOPKEY
        shop_token = SHOPKEY
        from settings import SECKEY
        sec_key = SECKEY

        client = CKassaPayment(payment_data)
        result = await client.create_payment(
            name_shop="Боевой Магазин",
            shop_token=shop_token,
            sec_key=sec_key
        )
        print("Результат:", result)


    asyncio.run(_run_test())
