# ---------------------------------------------
# CKassa Payment Status Check (Shop API)
# ---------------------------------------------
# Задача файла: минималистично и надёжно проверить статус платежа по regPayNum.
# Комментарии и документация — компактные, но информативные.

import asyncio
import os
import httpx
import backoff

from settings import DOMAIN_PAYMENT
from src.utils.logger._logger import logger_msg


class CKassaPaymentChecker:
    """
    Проверка статуса платежа в CKassa (Shop API).

    Стиль и поведение полностью повторяют create_payment_ckassa.py:
      - внутренний метод с backoff-ретраями;
      - внешний метод с циклом попыток, задержками и единообразным логированием;
      - единый парсинг ошибок и возврат значений.
    """

    @backoff.on_exception(
        backoff.expo,
        (httpx.RequestError, httpx.TimeoutException),
        max_tries=5,
        jitter=None
    )
    async def _check_payment(self, shop_token: str, sec_key: str, regPayNum: str):
        """
        Делает запрос на проверку статуса платежа CKassa.

        Returns:
            dict | '-1'
        """
        url = f"https://{DOMAIN_PAYMENT}/api-shop/rs/shop/check/payment/state"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        payload = {"regPayNum": regPayNum}

        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
            try:
                response = await client.post(
                    url,
                    headers=headers,
                    json=payload,
                    auth=httpx.BasicAuth(shop_token, sec_key)
                )

                try:
                    data = response.json()
                except Exception:
                    data = {}

                if response.status_code in (200, 201) and not data:
                    logger_msg("CKassa Check: Сервер вернул пустой JSON")

                return data

            except Exception as e:
                logger_msg(f"CKassa: Ошибка запроса проверки платежа: {e}")
                return '-1'

    async def check_error(self, data: dict, regPayNum: str):
        """
        Проверка ответа API.
        """
        if not isinstance(data, dict):
            logger_msg(f"CKassa Check Error: Некорректный формат ответа для regPayNum={regPayNum}")
            return True

        err_fields = ('error', 'errors', 'message', 'status', 'code', 'detail', 'errorCode')
        messages = []

        for k in err_fields:
            v = data.get(k)
            if v:
                messages.append(str(v))

        result_obj = data.get("result")
        if isinstance(result_obj, dict):
            rmsg = result_obj.get("message")
            if rmsg:
                messages.append(str(rmsg))

        if messages:
            msg = " | ".join(messages)
            logger_msg(f"CKassa Check Error: {msg}")

            low = msg.lower()
            if "limit" in low or "too many" in low or "unknown error" in low:
                return '-1'

            return True

        return False

    async def check_payment(self, shop_token: str, sec_key: str, regPayNum: str):
        for attempt in range(5):
            data = await self._check_payment(shop_token, sec_key, regPayNum)

            if data == '-1':
                logger_msg(f"Попытка {attempt + 1}/5: Ошибка соединения, ждем 15 сек")
                await asyncio.sleep(15)
                continue

            if not data:
                logger_msg(f"Попытка {attempt + 1}/5: Пустой ответ, ждем 1 сек")
                await asyncio.sleep(1)
                continue

            is_err = await self.check_error(data, regPayNum)
            if is_err == '-1':
                logger_msg(f"Попытка {attempt + 1}/5: Лимит/таймаут, ждем 15 сек")
                await asyncio.sleep(15)
                continue
            if is_err:
                return {"kind": "error", "raw": data}

            try:
                state = data.get("state") or data.get("status") or data.get("paymentStatus")
                norm = str(state).lower() if state is not None else None
                amount = data.get("amount")
                created_date = data.get("createdDate") or data.get("created_date")

                if norm in ("payed", "processed", "holded"):
                    return {"kind": "success", "norm": norm, "amount": amount, "created_date": created_date,
                            "raw": data}
                if norm in ("created",):
                    return {"kind": "pending", "norm": norm, "created_date": created_date, "raw": data}
                if norm in ("rejected", "refunded", "error", "created_error"):
                    return {"kind": "negative", "norm": norm, "raw": data}
                return {"kind": "unknown", "norm": norm, "raw": data}

            except Exception as e:
                logger_msg(f"CKassa: Ошибка структуры ответа проверки: {e}")
                await asyncio.sleep(1)
                continue

        return {"kind": "retry", "raw": None}


if __name__ == "__main__":
    async def _run_test():
        shop_token = "1a4c0d33-010c-4365-9c65-4c7f9bb415d5"
        sec_key = "6a7abaad-2147-4646-b91a-435b5d97527b"

        regPayNum = '536354'

        checker = CKassaPaymentChecker()
        result = await checker.check_payment(
            shop_token=shop_token,
            sec_key=sec_key,
            regPayNum=regPayNum
        )
        print("Результат проверки:", result)


    asyncio.run(_run_test())
