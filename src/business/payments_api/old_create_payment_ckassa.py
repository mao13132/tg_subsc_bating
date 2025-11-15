# ---------------------------------------------
# Program by @developer_telegrams
#
# Version   Date        Info
# 1.0       2025        Initial Version (CKassa Anonymous Payment)
# ---------------------------------------------

import asyncio
import httpx
import backoff

from src.utils.logger._logger import logger_msg


class CKassaAnonymousPayment:
    def __init__(self, payment_data):
        self.payment_data = payment_data

    @backoff.on_exception(
        backoff.expo,
        (httpx.RequestError, httpx.TimeoutException),
        max_tries=5,
        jitter=None
    )
    async def _create_payment(self, username, password):
        """
        Отправляет запрос на создание анонимного платежа в CKassa (демо).

        Args:
            username (str): Логин для Basic Auth
            password (str): Пароль для Basic Auth

        Returns:
            dict|str: JSON-ответ API (dict) или '-1' в случае ошибки соединения/таймаута
        """
        url = 'https://demo-api2.ckassa.ru/api-shop/do/payment/anonymous'

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        async with httpx.AsyncClient(timeout=httpx.Timeout(180.0)) as client:
            try:
                response = await client.post(
                    url,
                    headers=headers,
                    json=self.payment_data,
                    auth=httpx.BasicAuth(username, password)
                )

                # Пытаемся разобрать JSON, если нет — вернём пустой dict
                try:
                    data_response = response.json()
                except Exception:
                    data_response = {}

                if response.status_code in (200, 201) and not data_response:
                    logger_msg('CKassa: Нулевой ответ от серверов')

                return data_response

            except Exception as e:
                logger_msg(f'CKassa: Ошибка при создании анонимного платежа: "{e}"')
                return '-1'

    async def check_error(self, data_response, name_shop):
        """
        Проверяет ответ API на наличие ошибок.

        Args:
            data_response (dict): Ответ от API
            name_shop (str): Название магазина/лист для логирования

        Returns:
            bool|str:
                False - нет ошибок
                True  - есть ошибка
                '-1'  - лимит/слишком много запросов/временные проблемы ("limit", "Unknown error, try later")
        """
        if not isinstance(data_response, dict):
            logger_msg(f'CKassa Error: Некорректный формат ответа для {name_shop}')
            return True

        # Частые поля ошибок: 'error', 'errors', 'message', 'status'
        message_parts = []
        for key in ('error', 'errors', 'message', 'status', 'code', 'detail'):
            val = data_response.get(key)
            if val:
                message_parts.append(str(val))

        error_msg = ' | '.join(message_parts) if message_parts else ''

        if error_msg:
            logger_msg(f'CKassa Error: {error_msg}')
            low = error_msg.lower()
            if 'limit' in low or 'too many' in low or 'unknown error, try later' in low:
                return '-1'
            return True

        return False

    async def loop_create_anonymous_payment(self, name_shop, username, password):
        """
        Основной метод: создаёт анонимный платёж с повторными попытками.

        Args:
            name_shop (str): Название магазина/лист
            username (str): Логин Basic Auth
            password (str): Пароль Basic Auth

        Returns:
            str|bool:
                - Возврат 'paymentId' при успехе, если он есть
                - Возврат 'result' при успехе, если он есть
                - True, если успех без явного идентификатора
                - False при неудаче
        """
        for attempt in range(5):
            data_response = await self._create_payment(username, password)

            if data_response == '-1':
                logger_msg(f'Попытка {attempt + 1}/5: Ошибка соединения, ждем 15 сек')
                await asyncio.sleep(15)
                continue

            if not data_response:
                logger_msg(f'Попытка {attempt + 1}/5: Пустой ответ от сервера')
                await asyncio.sleep(1)
                continue

            is_error = await self.check_error(data_response, name_shop)

            if is_error == '-1':
                logger_msg(f'Попытка {attempt + 1}/5: Превышен лимит/временная ошибка, ждем 15 сек')
                await asyncio.sleep(15)
                continue

            if is_error:
                logger_msg(f'Критическая ошибка при создании платежа для {name_shop}')
                return False

            try:
                if 'paymentId' in data_response:
                    pid = data_response['paymentId']
                    print(f'Создан анонимный платёж для "{name_shop}": {pid}')
                    return pid
                elif 'result' in data_response:
                    result = data_response['result']
                    print(f'Платёж создан для "{name_shop}": {result}')
                    return result
                else:
                    print(f'Платёж успешно создан для "{name_shop}"')
                    return True

            except (KeyError, TypeError) as e:
                logger_msg(f'Неожиданная структура ответа CKassa: {e}')
                logger_msg(f'Ответ: {data_response}')
                await asyncio.sleep(1)
                continue

        logger_msg(f'CKassa: Исчерпаны все попытки создать анонимный платёж для {name_shop}')
        return False
