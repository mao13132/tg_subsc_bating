from datetime import datetime
from typing import Dict, Any, Optional, List

from sqlalchemy import Column, Integer, String, DateTime, select, insert, update

from settings import Base
from src.utils.logger._logger import logger_msg


class PaymentMessages(Base):
    __tablename__ = 'payment_messages'

    id_pk = Column(Integer, primary_key=True, nullable=False)
    chat_id = Column(String, nullable=False, index=True)
    message_id = Column(Integer, nullable=False)
    amount = Column(Integer, nullable=False, default=0)
    status = Column(String, nullable=False, default='active')
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class PaymentMessagesCRUD:
    def __init__(self, session_maker):
        self.session_maker = session_maker

    async def create(self, data: Dict[str, Any]) -> Optional[int]:
        try:
            async with self.session_maker() as session:
                q = insert(PaymentMessages).values(**data)
                res = await session.execute(q)
                await session.commit()
                return res.inserted_primary_key[0]
        except Exception as e:
            logger_msg(f"PaymentMessagesCRUD create error: {e}")
            return None

    async def read_active_older_than(self, before_dt: datetime) -> List[PaymentMessages]:
        try:
            async with self.session_maker() as session:
                q = select(PaymentMessages).where(
                    PaymentMessages.status == 'active',
                    PaymentMessages.created_at <= before_dt
                )
                res = await session.execute(q)
                return res.scalars().all()
        except Exception as e:
            logger_msg(f"PaymentMessagesCRUD read_active_older_than error: {e}")
            return []

    async def mark_reverted_by_id(self, pm_id: int) -> bool:
        try:
            async with self.session_maker() as session:
                q = update(PaymentMessages).where(PaymentMessages.id_pk == pm_id).values(status='reverted')
                res = await session.execute(q)
                await session.commit()
                return (res.rowcount or 0) > 0
        except Exception as e:
            logger_msg(f"PaymentMessagesCRUD mark_reverted_by_id error: {e}")
            return False

    async def mark_error_by_id(self, pm_id: int) -> bool:
        try:
            async with self.session_maker() as session:
                q = update(PaymentMessages).where(PaymentMessages.id_pk == pm_id).values(status='error')
                res = await session.execute(q)
                await session.commit()
                return (res.rowcount or 0) > 0
        except Exception as e:
            logger_msg(f"PaymentMessagesCRUD mark_error_by_id error: {e}")
            return False

    async def ensure_active(self, chat_id: str, message_id: int, amount: int) -> bool:
        try:
            async with self.session_maker() as session:
                sel = select(PaymentMessages).where(
                    PaymentMessages.chat_id == str(chat_id),
                    PaymentMessages.message_id == int(message_id)
                )
                res = await session.execute(sel)
                row = res.scalars().first()
                if row:
                    upd = update(PaymentMessages).where(PaymentMessages.id_pk == row.id_pk).values(
                        status='active', amount=int(amount), created_at=datetime.utcnow()
                    )
                    await session.execute(upd)
                else:
                    ins = insert(PaymentMessages).values(
                        chat_id=str(chat_id), message_id=int(message_id), amount=int(amount), status='active',
                        created_at=datetime.utcnow()
                    )
                    await session.execute(ins)
                await session.commit()
                return True
        except Exception as e:
            logger_msg(f"PaymentMessagesCRUD ensure_active error: {e}")
            return False
            