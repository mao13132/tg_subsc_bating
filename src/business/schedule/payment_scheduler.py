# ---------------------------------------------
# Планировщик фоновой проверки платежей CKassa
# ---------------------------------------------
# - Отдельный модуль, не засоряет main.py
# - Запускает асинхронный цикл, который периодически проверяет статусы платежей
# - Проверка выполняется через CKassaPaymentChecker
# - Обновляет статус записи в таблице payments
# - Снимает флаг need_paid у пользователя при успешной оплате
# ---------------------------------------------
import asyncio
from datetime import datetime, timedelta
from typing import Optional, List

from settings import SHOPKEY, SECKEY, CHECK_PAYMENT_EVERY, MOKE_SCHEDULE_PAYMENTS_TASK
from src.telegram.keyboard.keyboards import Admin_keyb
from src.utils.logger._logger import logger_msg
from src.telegram.bot_core import BotDB, bot
from src.business.payments_api.check_payment_ckassa import CKassaPaymentChecker
from src.business.text_manager.text_manager import text_manager
from src.telegram.sendler.sendler import Sendler_msg
from src.business.offers.send_offer_content import send_offer_content_to_user
from src.business.offers.offers_json import add_id_user
from src.business.schedule.payment_admin_notify import send_admin_payment_info
from src.business.offers.send_latest_offer_to_waiting_users import send_latest_offer_to_waiting_users


async def check_payments_once() -> int:
    """
    Одноразовая проверка статусов платежей.
    - Берём платежи со статусами 'sent' и 'created'
    - По каждому вызываем CKassaPaymentChecker
    - Успех: пишем фактический статус (payed/processed/holded), снимаем need_paid у пользователя
    - Негатив/ошибки: обновляем статус если удалось распарсить, иначе оставляем как есть

    Returns:
        Кол-во успешно обработанных (оплаченных) платежей
    """
    if not SHOPKEY or not SECKEY:
        logger_msg("CKassa: SHOPKEY/SECKEY не заданы, проверка пропущена")
        return 0

    processed_ok = 0
    checker = CKassaPaymentChecker()

    payments_to_check: List = []
    for st in ('sent', 'created'):
        try:
            payments_to_check.extend(await BotDB.payments.read_by_filter({'status': st}) or [])
        except Exception as e:
            logger_msg(f"SQL: ошибка выборки платежей со статусом '{st}': {e}")

    ttl_seconds = 86400
    for p in payments_to_check:
        reg = getattr(p, 'reg_pay_num', None)
        pid = getattr(p, 'id_pk', None)
        uid = getattr(p, 'id_user', None)
        created_at = getattr(p, 'created_at', None)

        if not reg or not pid:
            continue

        try:
            result = await checker.check_payment(SHOPKEY, SECKEY, reg)

            if isinstance(result, dict):
                kind = result.get('kind')
                norm = result.get('norm')
                raw = result.get('raw')

                if norm is None and isinstance(raw, dict):
                    state = raw.get('state') or raw.get('status') or raw.get('paymentStatus')
                    norm = str(state).lower() if state is not None else None

                if kind == 'success' and norm in ("payed", "processed", "holded"):
                    await BotDB.payments.update_by_id(pid, {'status': norm})

                    await BotDB.edit_user('need_paid', False, uid)
                    await BotDB.edit_user('received_forecast', False, uid)
                    await BotDB.edit_user('send_payments', False, uid)

                    msg = await text_manager.get_message('payment_success')

                    get_forecast_btn = await text_manager.get_button_text('get_forecast')

                    admin_link = await text_manager.get_button_text('admin_link')

                    admin_text = await text_manager.get_button_text('admin_text')

                    keyboard = Admin_keyb().good_payments(get_forecast_btn, admin_text, admin_link)

                    try:
                        await bot.send_message(int(uid), msg, reply_markup=keyboard, disable_notification=True,
                                               protect_content=True)
                    except Exception as e:
                        logger_msg(f"Ошибка отправки сообщения об оплате пользователю {uid}: {e}")

                    offer_id = getattr(p, 'offer_id', None)
                    if offer_id:
                        await send_offer_content_to_user(bot, int(uid), int(offer_id))
                        try:
                            offer = await BotDB.offers.read_by_id(int(offer_id))
                            current = getattr(offer, 'paid_users', None)
                            paid_json = add_id_user(current, uid)
                            await BotDB.offers.update_by_id(int(offer_id), {"paid_users": paid_json})
                        except Exception as e:
                            logger_msg(f"Ошибка записи оплатившего в Offer {offer_id}: {e}")

                    processed_ok += 1
                    try:
                        await send_admin_payment_info(bot, p, norm)
                    except Exception as e:
                        logger_msg(f"Ошибка уведомления админов об оплате {pid}: {e}")
                    continue

                if kind == 'negative' and norm in ("rejected", "refunded", "error", "created_error"):
                    await BotDB.payments.update_by_id(pid, {'status': norm})
                    continue

                if kind == 'error':
                    await BotDB.payments.update_by_id(pid, {'status': 'error'})
                    continue

                if kind == 'pending' and norm == 'created':
                    if created_at and (datetime.utcnow() - created_at).total_seconds() > ttl_seconds:
                        await BotDB.payments.update_by_id(pid, {'status': 'expired'})
                    continue

                if kind == 'unknown':
                    await BotDB.payments.update_by_id(pid, {'status': norm or 'unknown'})
                    continue

            await asyncio.sleep(0)

        except Exception as e:
            logger_msg(f"Проверка платежа {reg} упала: {e}")
            await asyncio.sleep(0)

    return processed_ok


async def check_expired_messages_once() -> int:
    try:
        before = datetime.utcnow() + timedelta(hours=3)
        deleted_msgs = await BotDB.user_messages.delete_expired(before)
        deleted_offers = 0
        try:
            deleted_offers = await BotDB.offers.delete_expired(before)
        except Exception as es:
            logger_msg(f"Delete expired offers error: {es}")

        if (deleted_msgs or 0) > 0 or (deleted_offers or 0) > 0:
            try:
                text = (
                    f"🗑 Автоудаление:\n"
                    f"• прогнозов: {int(deleted_offers or 0)}"
                )
                await Sendler_msg.sendler_to_admin_mute_bot(bot, text, None)
            except Exception as es:
                logger_msg(f"Notify admin about expired deletion error: {es}")

        return int((deleted_msgs or 0) + (deleted_offers or 0))
    except Exception as e:
        logger_msg(f"Delete expired messages/offers error: {e}")
        return 0


class PaymentScheduler:
    """Планировщик для автоматической проверки платежей CKassa"""

    def __init__(self):
        self.is_running = False
        self.task: Optional[asyncio.Task] = None

    async def start(self):
        if self.is_running:
            print("⚠️ Планировщик уже запущен")
            return

        try:
            print("🚀 Запуск планировщика автоматической проверки платежей...")
            self.is_running = True
            self.task = asyncio.create_task(self._run_payment_checker())
            print("✅ Планировщик успешно запущен")
        except Exception as e:
            logger_msg(f"❌ Ошибка запуска планировщика: {e}")
            self.is_running = False

    async def stop(self):
        if not self.is_running:
            logger_msg("⚠️ Планировщик не запущен")
            return

        try:
            logger_msg("🛑 Остановка планировщика...")
            self.is_running = False

            if self.task and not self.task.done():
                self.task.cancel()
                try:
                    await self.task
                except asyncio.CancelledError:
                    pass

            print("✅ Планировщик остановлен")
        except Exception as e:
            logger_msg(f"❌ Ошибка остановки планировщика: {e}")

    async def _run_payment_checker(self):
        """Основной цикл проверки платежей"""
        try:
            print("🔄 Запуск цикла автоматической проверки платежей")
            while self.is_running:
                try:
                    tasks = []
                    idx_pay = None
                    if not MOKE_SCHEDULE_PAYMENTS_TASK:
                        idx_pay = len(tasks)
                        tasks.append(check_payments_once())
                    idx_exp = len(tasks)
                    tasks.append(check_expired_messages_once())
                    idx_offer = len(tasks)
                    tasks.append(send_latest_offer_to_waiting_users())

                    results = await asyncio.gather(*tasks, return_exceptions=True)

                    count_pay = 0 if idx_pay is None else results[idx_pay]
                    count_exp = results[idx_exp]
                    sent_offer = results[idx_offer]

                    if isinstance(count_pay, Exception):
                        logger_msg(f"❌ Ошибка одноразовой проверки платежей: {count_pay}")
                    elif (count_pay or 0) > 0:
                        print(f"✅ Обработано оплаченных платежей: {int(count_pay)}")

                    if isinstance(count_exp, Exception):
                        logger_msg(f"❌ Ошибка одноразовой очистки просроченных: {count_exp}")
                    elif (count_exp or 0) > 0:
                        print(f"🧹 Удалено просроченных сообщений: {int(count_exp)}")

                    if isinstance(sent_offer, Exception):
                        logger_msg(f"❌ Ошибка рассылки свежего оффера: {sent_offer}")
                    elif sent_offer:
                        print("📨 Свежий оффер отправлен ожидающим пользователям")
                    await asyncio.sleep(CHECK_PAYMENT_EVERY)
                except asyncio.CancelledError:
                    logger_msg("🛑 Цикл проверки платежей отменен")
                    break
                except Exception as e:
                    logger_msg(f"❌ Ошибка в цикле проверки платежей: {e}")
                    await asyncio.sleep(60)
        except Exception as e:
            logger_msg(f"❌ Критическая ошибка в _run_payment_checker: {e}")
        finally:
            self.is_running = False

    def get_status(self) -> dict:
        """Статус планировщика"""
        return {
            'is_running': self.is_running,
            'task_done': self.task.done() if self.task else None,
            'current_time': datetime.now().isoformat()
        }


payment_scheduler = PaymentScheduler()


async def start_payment_scheduler():
    """Запуск планировщика при старте приложения"""
    await payment_scheduler.start()


async def stop_payment_scheduler():
    """Остановка планировщика при остановке приложения"""
    await payment_scheduler.stop()


async def manual_payment_check() -> dict:
    """
    Ручной запуск одноразовой проверки платежей (например, для админки)
    """
    try:
        logger_msg("🔍 Ручной запуск проверки платежей...")
        processed_count = await check_payments_once()
        result = {
            'success': True,
            'processed_count': processed_count,
            'timestamp': datetime.now().isoformat()
        }
        logger_msg(f"✅ Ручная проверка завершена. Обработано: {processed_count}")
        return result
    except Exception as e:
        logger_msg(f"❌ Ошибка ручной проверки платежей: {e}")
        return {'success': False, 'error': str(e), 'timestamp': datetime.now().isoformat()}
