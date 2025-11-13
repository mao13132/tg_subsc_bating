# ---------------------------------------------
# Program by @developer_telegrams
#
#
# Version   Date        Info
# 1.0       2023    Initial Version
#
# ---------------------------------------------
from datetime import datetime

from sqlalchemy import Column, Integer, String, select, insert, update, delete, Boolean, DateTime
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from settings import SQL_URL, Base
from src.sql.texts import TextsCRUD
from src.utils.logger._logger import logger_msg
from src.utils.telegram_debug import SendlerOneCreate


class Users(Base):
    __tablename__ = f'users'

    id_pk = Column(Integer, primary_key=True, nullable=False)

    id_user = Column(String)

    login = Column(String, nullable=True)

    first_name = Column(String, nullable=True)

    last_name = Column(String, nullable=True)

    premium = Column(String, nullable=True)

    join_date = Column(DateTime, nullable=True, default=datetime.utcnow)

    last_time = Column(DateTime, nullable=True)

    other = Column(String, nullable=True)


class Settings(Base):
    __tablename__ = 'settings'

    id_pk = Column(Integer, primary_key=True, nullable=False)

    key = Column(String, nullable=False)

    value = Column(String, nullable=False)

    types = Column(String, nullable=True)


class BotDB:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    def __init__(self):
        try:
            self.engine = create_async_engine(SQL_URL)

            # Создаём сессию
            self.async_session_maker = sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)

            # Инициализируем CRUD для текстов
            self.texts = TextsCRUD(self.async_session_maker)
        except Exception as es:
            error_ = f'SQL не могу создать подключение "{es}"'

            logger_msg(error_)

    async def check_or_add_user(self, id_user, data_user):
        async with self.async_session_maker() as session:
            query = select(Users).filter_by(id_user=str(id_user))

            response = await session.execute(query)

            status_new_user = response.scalar_one_or_none()

            if not status_new_user:
                now_date = datetime.now()

                query = insert(Users).values(**data_user, join_date=now_date, id_user=str(id_user))

                response = await session.execute(query)

                await session.commit()

            return status_new_user

    async def edit_user(self, key_, value, id_user):

        try:
            async with self.async_session_maker() as session:
                query = update(Users).where(Users.id_user == str(id_user)).values({key_: value})

                response = await session.execute(query)

                result = await session.commit()

                return True
        except Exception as es:
            error_ = f'SQL edit_user: "{es}"'

            logger_msg(error_)

            return False

    async def get_setting(self, key):

        try:
            async with self.async_session_maker() as session:
                query = select(Settings).where(Settings.key == str(key))

                response = await session.execute(query)

                result = response.scalars().first()

                return result.value
        except Exception as es:
            error_ = f'SQL get_setting: "{es}"'

            logger_msg(error_)

            return False

    async def update_settings(self, key, value):

        try:
            async with self.async_session_maker() as session:
                query = update(Settings).where(Settings.key == str(key)).values(value=value)

                response = await session.execute(query)

                result = await session.commit()

                return True
        except Exception as es:
            error_ = f'SQL update_settings: "{es}"'

            logger_msg(error_)

            return False

    async def start_settings(self, **filters):
        try:

            async with self.async_session_maker() as session:
                query = select(Settings).filter_by(key=filters['key'])

                response = await session.execute(query)

                exists = response.scalar_one_or_none()

                if not exists:
                    query = insert(Settings).values(**filters)

                    response = await session.execute(query)

                    await session.commit()

                return exists
        except Exception as es:
            error_ = f'Ошибка SQL start_settings: "{es}"'

            logger_msg(error_)

            return False

    async def init_bases(self):
        try:
            async with self.engine.begin() as conn:
                # await conn.run_sync(Base.metadata.drop_all)
                await conn.run_sync(Base.metadata.create_all)

                return True
        except Exception as es:
            error_ = f'SQL Postgres: Ошибка не могу подключиться к базе данных "{es}"\n' \
                     f'"{SQL_URL}"'

            logger_msg(error_)

            await SendlerOneCreate().send_message(error_)

            return False
