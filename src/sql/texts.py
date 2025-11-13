# ---------------------------------------------
# Program by @developer_telegrams
# Texts Management
#
# Version   Date        Info
# 1.0       2024    Initial Version
#
# ---------------------------------------------
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple

from sqlalchemy import Column, Integer, String, UniqueConstraint, select, insert, update, delete

from settings import Base
from src.utils.logger._logger import logger_msg


class Texts(Base):
    """Модель для хранения текстов кнопок и сообщений"""
    __tablename__ = 'texts'

    id_pk = Column(Integer, primary_key=True, nullable=False)

    text_type = Column(String, nullable=False, index=True, comment="Тип текста: 'buttons' или 'messages'")

    key = Column(String, nullable=False, index=True, comment="Ключ текста")

    value = Column(String, nullable=False, comment="Значение текста")

    # Уникальное ограничение для комбинации text_type и key
    __table_args__ = (
        UniqueConstraint('text_type', 'key', name='uq_text_type_key'),
    )


class TextsCRUD:
    """Универсальные CRUD операции для таблицы текстов"""

    def __init__(self, session_maker):
        self.session_maker = session_maker

    async def create(self, data: Dict[str, Any]) -> Optional[int]:
        """
        Создание новой записи текста
        
        Args:
            data: Словарь с данными для создания записи
                  Обязательные поля: text_type, key, value
            
        Returns:
            ID созданной записи или None при ошибке
        """
        try:
            async with self.session_maker() as session:
                query = insert(Texts).values(**data)
                result = await session.execute(query)
                await session.commit()

                # Получаем ID созданной записи
                return result.inserted_primary_key[0]

        except Exception as e:
            error_msg = f"TextsCRUD create error: {e}"
            logger_msg(error_msg)
            return None

    async def read_by_id(self, text_id: int) -> Optional[Texts]:
        """
        Получение записи по ID
        
        Args:
            text_id: ID записи
            
        Returns:
            Объект Texts или None
        """
        try:
            async with self.session_maker() as session:
                query = select(Texts).where(Texts.id_pk == text_id)
                result = await session.execute(query)
                return result.scalar_one_or_none()

        except Exception as e:
            error_msg = f"TextsCRUD read_by_id error: {e}"
            logger_msg(error_msg)
            return None

    async def read_by_filter(self, filters: Dict[str, Any]) -> List[Texts]:
        """
        Получение записей по фильтрам
        
        Args:
            filters: Словарь с фильтрами для поиска
                    Возможные ключи: text_type, key, value
            
        Returns:
            Список объектов Texts
        """
        try:
            async with self.session_maker() as session:
                query = select(Texts).filter_by(**filters)
                result = await session.execute(query)
                return result.scalars().all()

        except Exception as e:
            error_msg = f"TextsCRUD read_by_filter error: {e}"
            logger_msg(error_msg)
            return []

    async def read_all(self) -> List[Texts]:
        """
        Получение всех записей
        
        Returns:
            Список всех объектов Texts
        """
        try:
            async with self.session_maker() as session:
                query = select(Texts)
                result = await session.execute(query)
                return result.scalars().all()

        except Exception as e:
            error_msg = f"TextsCRUD read_all error: {e}"
            logger_msg(error_msg)
            return []

    async def update_by_id(self, text_id: int, data: Dict[str, Any]) -> bool:
        """
        Обновление записи по ID
        
        Args:
            text_id: ID записи для обновления
            data: Словарь с новыми данными
            
        Returns:
            True при успехе, False при ошибке
        """
        try:
            async with self.session_maker() as session:
                query = update(Texts).where(Texts.id_pk == text_id).values(**data)
                result = await session.execute(query)
                await session.commit()

                return result.rowcount > 0

        except Exception as e:
            error_msg = f"TextsCRUD update_by_id error: {e}"
            logger_msg(error_msg)
            return False

    async def update_by_filter(self, filters: Dict[str, Any], data: Dict[str, Any]) -> int:
        """
        Обновление записей по фильтрам
        
        Args:
            filters: Словарь с фильтрами для поиска записей
            data: Словарь с новыми данными
            
        Returns:
            Количество обновленных записей
        """
        try:
            async with self.session_maker() as session:
                query = update(Texts).filter_by(**filters).values(**data)
                result = await session.execute(query)
                await session.commit()

                return result.rowcount

        except Exception as e:
            error_msg = f"TextsCRUD update_by_filter error: {e}"
            logger_msg(error_msg)
            return 0

    async def delete_by_id(self, text_id: int) -> bool:
        """
        Удаление записи по ID
        
        Args:
            text_id: ID записи для удаления
            
        Returns:
            True при успехе, False при ошибке
        """
        try:
            async with self.session_maker() as session:
                query = delete(Texts).where(Texts.id_pk == text_id)
                result = await session.execute(query)
                await session.commit()

                return result.rowcount > 0

        except Exception as e:
            error_msg = f"TextsCRUD delete_by_id error: {e}"
            logger_msg(error_msg)
            return False

    async def delete_by_filter(self, filters: Dict[str, Any]) -> int:
        """
        Удаление записей по фильтрам
        
        Args:
            filters: Словарь с фильтрами для поиска записей
            
        Returns:
            Количество удаленных записей
        """
        try:
            async with self.session_maker() as session:
                query = delete(Texts).filter_by(**filters)
                result = await session.execute(query)
                await session.commit()

                return result.rowcount

        except Exception as e:
            error_msg = f"TextsCRUD delete_by_filter error: {e}"
            logger_msg(error_msg)
            return 0

    # Специализированные методы для работы с текстами

    async def get_text_by_key(self, text_type: str, key: str) -> Optional[str]:
        """
        Получение значения текста по типу и ключу
        
        Args:
            text_type: Тип текста ('buttons' или 'messages')
            key: Ключ текста
            
        Returns:
            Значение текста или None если не найден
        """
        try:
            texts = await self.read_by_filter({'text_type': text_type, 'key': key})
            if texts:
                return texts[0].value
            return None

        except Exception as e:
            error_msg = f"TextsCRUD get_text_by_key error: {e}"
            logger_msg(error_msg)
            return None

    async def set_text_by_key(self, text_type: str, key: str, value: str) -> bool:
        """
        Установка значения текста по типу и ключу (создание или обновление)
        
        Args:
            text_type: Тип текста ('buttons' или 'messages')
            key: Ключ текста
            value: Новое значение текста
            
        Returns:
            True при успехе, False при ошибке
        """
        try:
            # Проверяем, существует ли запись
            existing_texts = await self.read_by_filter({'text_type': text_type, 'key': key})

            if existing_texts:
                # Обновляем существующую запись
                return await self.update_by_id(existing_texts[0].id_pk, {'value': value})
            else:
                # Создаем новую запись
                text_id = await self.create({
                    'text_type': text_type,
                    'key': key,
                    'value': value
                })
                return text_id is not None

        except Exception as e:
            error_msg = f"TextsCRUD set_text_by_key error: {e}"
            logger_msg(error_msg)
            return False

    async def get_texts_by_type(self, text_type: str) -> Dict[str, str]:
        """
        Получение всех текстов определенного типа в виде словаря
        
        Args:
            text_type: Тип текста ('buttons' или 'messages')
            
        Returns:
            Словарь {key: value} с текстами
        """
        try:
            texts = await self.read_by_filter({'text_type': text_type})
            return {text.key: text.value for text in texts}

        except Exception as e:
            error_msg = f"TextsCRUD get_texts_by_type error: {e}"
            logger_msg(error_msg)
            return {}

    async def get_all_texts(self, text_type: str) -> List[Tuple[str, str]]:
        """
        Получить все тексты выбранного типа в виде списка пар (key, value).

        Используется UI для генерации клавиатур редактирования.

        Args:
            text_type: Тип текста ('buttons' или 'messages').

        Returns:
            Список пар (key, value). Пустой список при ошибке/отсутствии данных.
        """
        try:
            async with self.session_maker() as session:
                query = select(Texts).where(Texts.text_type == text_type)
                result = await session.execute(query)
                texts = result.scalars().all()

                # Возвращаем минимально необходимую структуру для клавиатур
                return [(t.key, t.value) for t in texts]
        except Exception as e:
            error_msg = f"TextsCRUD get_all_texts error: {e}"
            logger_msg(error_msg)
            return []

    async def get_button_texts(self) -> Dict[str, str]:
        """
        Получение всех текстов кнопок
        
        Returns:
            Словарь {key: value} с текстами кнопок
        """
        return await self.get_texts_by_type('buttons')

    async def get_message_texts(self) -> Dict[str, str]:
        """
        Получение всех текстов сообщений
        
        Returns:
            Словарь {key: value} с текстами сообщений
        """
        return await self.get_texts_by_type('messages')

    async def bulk_create_texts(self, texts_data: List[Dict[str, str]]) -> int:
        """
        Массовое создание текстов
        
        Args:
            texts_data: Список словарей с данными текстов
                       Каждый словарь должен содержать: text_type, key, value
            
        Returns:
            Количество успешно созданных записей
        """
        created_count = 0

        for text_data in texts_data:
            try:
                text_id = await self.create(text_data)
                if text_id is not None:
                    created_count += 1
            except Exception as e:
                error_msg = f"TextsCRUD bulk_create_texts error for {text_data}: {e}"
                logger_msg(error_msg)
                continue

        return created_count

    async def delete_texts_by_type(self, text_type: str) -> int:
        """
        Удаление всех текстов определенного типа
        
        Args:
            text_type: Тип текста для удаления
            
        Returns:
            Количество удаленных записей
        """
        return await self.delete_by_filter({'text_type': text_type})
