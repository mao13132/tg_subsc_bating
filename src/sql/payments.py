# ---------------------------------------------
# Program by @developer_telegrams
# Payments Management (CKassa)
#
# Version   Date        Info
# ---------------------------------------------
from datetime import datetime
from typing import Dict, Any, Optional, List

from sqlalchemy import Column, Integer, String, DateTime, select, insert, update, delete
from settings import Base
from src.utils.logger._logger import logger_msg


class Payments(Base):
    __tablename__ = 'payments'

    id_pk = Column(Integer, primary_key=True, nullable=False)
    id_user = Column(String, nullable=False, index=True)
    amount = Column(Integer, nullable=False)
    reg_pay_num = Column(String, nullable=True, index=True)
    link = Column(String, nullable=False, default='created')
    status = Column(String, nullable=False, default='created')
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class PaymentsCRUD:
    def __init__(self, session_maker):
        self.session_maker = session_maker

    async def create(self, data: Dict[str, Any]) -> Optional[int]:
        try:
            async with self.session_maker() as session:
                q = insert(Payments).values(**data)
                res = await session.execute(q)
                await session.commit()
                return res.inserted_primary_key[0]
        except Exception as e:
            logger_msg(f"PaymentsCRUD create error: {e}")
            return None

    async def read_by_filter(self, filters: Dict[str, Any]) -> List[Payments]:
        try:
            async with self.session_maker() as session:
                q = select(Payments).filter_by(**filters)
                res = await session.execute(q)
                return res.scalars().all()
        except Exception as e:
            logger_msg(f"PaymentsCRUD read_by_filter error: {e}")
            return []

    async def update_by_id(self, payment_id: int, data: Dict[str, Any]) -> bool:
        try:
            async with self.session_maker() as session:
                q = update(Payments).where(Payments.id_pk == payment_id).values(**data)
                res = await session.execute(q)
                await session.commit()
                return res.rowcount > 0
        except Exception as e:
            logger_msg(f"PaymentsCRUD update_by_id error: {e}")
            return False

    async def delete_by_filter(self, filters: Dict[str, Any]) -> int:
        try:
            async with self.session_maker() as session:
                q = delete(Payments).filter_by(**filters)
                res = await session.execute(q)
                await session.commit()
                return res.rowcount
        except Exception as e:
            logger_msg(f"PaymentsCRUD delete_by_filter error: {e}")
            return 0