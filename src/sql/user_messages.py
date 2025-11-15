# python
# c:\Users\user\PycharmProjects\tg_display_foto\src\sql\user_messages.py
# ---------------------------------------------
# Program by @developer_telegrams
# Универсальное хранилище пользовательских сообщений (упакованный контент)
#
# Version   Date        Info
# 1.0       2025        Initial Version
# ---------------------------------------------
from datetime import datetime
from typing import Dict, Any, Optional, List

from sqlalchemy import Column, Integer, String, DateTime, select, insert, update, delete

from settings import Base
from src.utils.logger._logger import logger_msg


class UserMessage(Base):
    """
    Таблица для хранения сообщений пользователя в едином формате:
    - id_user: Telegram ID пользователя
    - content: JSON-строка из pack_message_content(message)
    - batch_key: ключ партии/сессии для групповой отправки
    - media_group_id: идентификатор медиа-группы Telegram (если сообщение часть альбома)
    - mg_index: порядок сообщения внутри медиа-группы (1..N)
    - created_at/updated_at: аудит
    """
    __tablename__ = 'user_messages'

    id_pk = Column(Integer, primary_key=True, nullable=False)

    id_user = Column(String, nullable=False, index=True, comment="ID пользователя-отправителя")

    content = Column(String, nullable=False, comment="Упакованный JSON контент (text/photo/video/document/animation)")

    batch_key = Column(String, nullable=True, index=True, comment="Ключ партии/контекста для группировки")

    media_group_id = Column(String, nullable=True, index=True, comment="ID медиа-группы Telegram")

    mg_index = Column(Integer, nullable=True, comment="Порядковый номер сообщения в медиа-группе")

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, comment="Дата создания")

    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow,
                        comment="Дата обновления")


class UserMessageCRUD:
    """Универсальные CRUD операции для таблицы user_messages"""

    def __init__(self, session_maker):
        self.session_maker = session_maker

    async def create(self, data: Dict[str, Any]) -> Optional[int]:
        """
        Создать запись.
        Обязательные поля: id_user, content
        Необязательные: batch_key
        """
        try:
            async with self.session_maker() as session:
                query = insert(UserMessage).values(**data)
                result = await session.execute(query)
                await session.commit()
                return result.inserted_primary_key[0]
        except Exception as e:
            logger_msg(f"UserMessageCRUD create error: {e}")
            return None

    async def read_by_id(self, msg_id: int) -> Optional[UserMessage]:
        """Получить запись по ID"""
        try:
            async with self.session_maker() as session:
                query = select(UserMessage).where(UserMessage.id_pk == msg_id)
                result = await session.execute(query)
                return result.scalar_one_or_none()
        except Exception as e:
            logger_msg(f"UserMessageCRUD read_by_id error: {e}")
            return None

    async def read_by_filter(self, filters: Dict[str, Any]) -> List[UserMessage]:
        """Получить список записей по фильтрам (например: {'id_user': '123', 'batch_key': 'op_...'})."""
        try:
            async with self.session_maker() as session:
                query = select(UserMessage).filter_by(**filters)
                result = await session.execute(query)
                return result.scalars().all()
        except Exception as e:
            logger_msg(f"UserMessageCRUD read_by_filter error: {e}")
            return []

    async def read_media_group(self, id_user: str, media_group_id: str) -> List[UserMessage]:
        """Получить все сообщения медиа-группы в правильном порядке."""
        try:
            async with self.session_maker() as session:
                query = (
                    select(UserMessage)
                    .where(
                        UserMessage.id_user == str(id_user),
                        UserMessage.media_group_id == str(media_group_id)
                    )
                    .order_by(UserMessage.mg_index.asc(), UserMessage.id_pk.asc())
                )
                result = await session.execute(query)
                return result.scalars().all()
        except Exception as e:
            logger_msg(f"UserMessageCRUD read_media_group error: {e}")
            return []

    async def update_by_id(self, msg_id: int, data: Dict[str, Any]) -> bool:
        """Обновить запись по ID"""
        try:
            async with self.session_maker() as session:
                query = update(UserMessage).where(UserMessage.id_pk == msg_id).values(**data)
                result = await session.execute(query)
                await session.commit()
                return result.rowcount > 0
        except Exception as e:
            logger_msg(f"UserMessageCRUD update_by_id error: {e}")
            return False

    async def delete_by_filter(self, filters: Dict[str, Any]) -> int:
        """Удалить записи по фильтрам. Возвращает количество удалённых строк."""
        try:
            async with self.session_maker() as session:
                query = delete(UserMessage).filter_by(**filters)
                result = await session.execute(query)
                await session.commit()
                return result.rowcount
        except Exception as e:
            logger_msg(f"UserMessageCRUD delete_by_filter error: {e}")
            return 0

    async def delete_not_batch_key(self, id_user, batch_key):
        try:
            async with self.session_maker() as session:
                stmt = delete(UserMessage).where(
                    UserMessage.id_user == str(id_user),
                    UserMessage.batch_key != str(batch_key)
                )
                await session.execute(stmt)
                await session.commit()
        except Exception as e:
            logger_msg(f"finish_get_posts_call delete old messages error: {e}")

            return False

        return True
