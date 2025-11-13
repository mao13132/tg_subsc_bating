from src.sql.bd import BotDB
from src.utils.logger._logger import logger_msg


class TextManager:
    """Менеджер текстов с поддержкой базы данных"""
    
    def __init__(self):
        self._db = BotDB()
    
    async def get_button_text(self, key: str) -> str:
        """Получает текст кнопки по ключу"""
        return await self._db.texts.get_text_by_key('buttons', key)
    
    async def get_message(self, key: str) -> str:
        """Получает текст сообщения по ключу"""
        return await self._db.texts.get_text_by_key('messages', key)
    
    async def set_button_text(self, key: str, value: str) -> bool:
        """Устанавливает текст кнопки по ключу"""
        return await self._db.texts.set_text_by_key('buttons', key, value)
    
    async def set_message_text(self, key: str, value: str) -> bool:
        """Устанавливает текст сообщения по ключу"""
        return await self._db.texts.set_text_by_key('messages', key, value)
    
    async def get_all_button_texts(self) -> dict:
        """Получает все тексты кнопок"""
        return await self._db.texts.get_button_texts()
    
    async def get_all_message_texts(self) -> dict:
        """Получает все тексты сообщений"""
        return await self._db.texts.get_message_texts()
    
    async def get_text_by_type_and_key(self, text_type: str, key: str) -> str:
        """Получает текст по типу и ключу"""
        return await self._db.texts.get_text_by_key(text_type, key)


# Создаем глобальный экземпляр
try:
    text_manager = TextManager()
except Exception as es:
    error_ = f'Ошибка создания TextManager: "{es}"'
    logger_msg(error_)
    text_manager = None
