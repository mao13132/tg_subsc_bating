from datetime import datetime
from typing import Dict, Any, Optional, List

from sqlalchemy import Column, Integer, String, DateTime, select, insert, update, delete

from settings import Base
from src.utils.logger._logger import logger_msg


class Offer(Base):
    __tablename__ = 'offers'

    id_pk = Column(Integer, primary_key=True, nullable=False)

    id_user = Column(String, nullable=False, index=True)

    summa = Column(Integer, nullable=False)

    message_json = Column(String, nullable=False)

    id_users = Column(String, nullable=True)

    paid_users = Column(String, nullable=True)

    expire_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class Motivation(Base):
    __tablename__ = 'motivations'

    id_pk = Column(Integer, primary_key=True, nullable=False)

    summa = Column(Integer, nullable=False)

    id_users = Column(String, nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class OffersCRUD:
    def __init__(self, session_maker):
        self.session_maker = session_maker

    async def create(self, data: Dict[str, Any]) -> Optional[int]:
        try:
            async with self.session_maker() as session:
                q = insert(Offer).values(**data)
                res = await session.execute(q)
                await session.commit()
                return res.inserted_primary_key[0]
        except Exception as e:
            logger_msg(f"OffersCRUD create error: {e}")
            return None

    async def read_by_id(self, offer_id: int) -> Optional[Offer]:
        try:
            async with self.session_maker() as session:
                q = select(Offer).where(Offer.id_pk == offer_id)
                res = await session.execute(q)
                return res.scalar_one_or_none()
        except Exception as e:
            logger_msg(f"OffersCRUD read_by_id error: {e}")
            return None

    async def read_by_filter(self, filters: Dict[str, Any]) -> List[Offer]:
        try:
            async with self.session_maker() as session:
                q = select(Offer).filter_by(**filters)
                res = await session.execute(q)
                return res.scalars().all()
        except Exception as e:
            logger_msg(f"OffersCRUD read_by_filter error: {e}")
            return []

    async def update_by_id(self, offer_id: int, data: Dict[str, Any]) -> bool:
        try:
            async with self.session_maker() as session:
                q = update(Offer).where(Offer.id_pk == offer_id).values(**data)
                res = await session.execute(q)
                await session.commit()
                return res.rowcount > 0
        except Exception as e:
            logger_msg(f"OffersCRUD update_by_id error: {e}")
            return False

    async def delete_by_id(self, offer_id: int) -> bool:
        try:
            async with self.session_maker() as session:
                q = delete(Offer).where(Offer.id_pk == offer_id)
                res = await session.execute(q)
                await session.commit()
                return res.rowcount > 0
        except Exception as e:
            logger_msg(f"OffersCRUD delete_by_id error: {e}")
            return False

    async def delete_expired(self, before: datetime) -> int:
        try:
            async with self.session_maker() as session:
                q = delete(Offer).where(
                    Offer.expire_at.isnot(None),
                    Offer.expire_at <= before
                )
                res = await session.execute(q)
                await session.commit()
                return res.rowcount
        except Exception as e:
            logger_msg(f"OffersCRUD delete_expired error: {e}")
            return 0

    async def delete_by_filter(self, filters: Dict[str, Any]) -> int:
        try:
            async with self.session_maker() as session:
                q = delete(Offer).filter_by(**filters)
                res = await session.execute(q)
                await session.commit()
                return res.rowcount
        except Exception as e:
            logger_msg(f"OffersCRUD delete_by_filter error: {e}")
            return 0

    async def delete_all(self) -> int:
        try:
            async with self.session_maker() as session:
                q = delete(Offer)
                res = await session.execute(q)
                await session.commit()
                return res.rowcount
        except Exception as e:
            logger_msg(f"OffersCRUD delete_all error: {e}")
            return 0


class MotivationsCRUD:
    def __init__(self, session_maker):
        self.session_maker = session_maker

    async def create(self, data: Dict[str, Any]) -> Optional[int]:
        try:
            async with self.session_maker() as session:
                q = insert(Motivation).values(**data)
                res = await session.execute(q)
                await session.commit()
                return res.inserted_primary_key[0]
        except Exception as e:
            logger_msg(f"MotivationsCRUD create error: {e}")
            return None

    async def read_by_id(self, motivation_id: int) -> Optional[Motivation]:
        try:
            async with self.session_maker() as session:
                q = select(Motivation).where(Motivation.id_pk == motivation_id)
                res = await session.execute(q)
                return res.scalar_one_or_none()
        except Exception as e:
            logger_msg(f"MotivationsCRUD read_by_id error: {e}")
            return None

    async def read_by_filter(self, filters: Dict[str, Any]) -> List[Motivation]:
        try:
            async with self.session_maker() as session:
                q = select(Motivation).filter_by(**filters)
                res = await session.execute(q)
                return res.scalars().all()
        except Exception as e:
            logger_msg(f"MotivationsCRUD read_by_filter error: {e}")
            return []

    async def update_by_id(self, motivation_id: int, data: Dict[str, Any]) -> bool:
        try:
            async with self.session_maker() as session:
                q = update(Motivation).where(Motivation.id_pk == motivation_id).values(**data)
                res = await session.execute(q)
                await session.commit()
                return res.rowcount > 0
        except Exception as e:
            logger_msg(f"MotivationsCRUD update_by_id error: {e}")
            return False

    async def delete_by_id(self, motivation_id: int) -> bool:
        try:
            async with self.session_maker() as session:
                q = delete(Motivation).where(Motivation.id_pk == motivation_id)
                res = await session.execute(q)
                await session.commit()
                return res.rowcount > 0
        except Exception as e:
            logger_msg(f"MotivationsCRUD delete_by_id error: {e}")
            return False

    async def delete_all(self) -> int:
        try:
            async with self.session_maker() as session:
                q = delete(Motivation)
                res = await session.execute(q)
                await session.commit()
                return res.rowcount
        except Exception as e:
            logger_msg(f"MotivationsCRUD delete_all error: {e}")
            return 0
            