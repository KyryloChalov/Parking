import contextlib

from os import environ
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from src.conf.config import config

TESTING = environ.get("TESTING")

# from sqlalchemy.orm import DeclarativeBase # переставив до models.models.py
# class Base(DeclarativeBase): ...


class DatabaseSessionManager:
    def __init__(self, url: str):
        self._engine: AsyncEngine | None = create_async_engine(url)
        self._session_maker: async_sessionmaker = async_sessionmaker(
            autocommit=False, autoflush=False, bind=self._engine
        )

    @contextlib.asynccontextmanager
    async def session(self):
        if self._session_maker is None:
            raise Exception("Session is not initialized!")
        session = self._session_maker()
        try:
            yield session
        except Exception as e:
            print(e)
            await session.rollback()
        finally:
            await session.close()


if TESTING:
    sessionmanager = DatabaseSessionManager(config.TEST_DB_URL)
else:
    sessionmanager = DatabaseSessionManager(config.DB_URL)


# Dependency
async def get_db():
    async with sessionmanager.session() as session:
        yield session
