import os
import asyncio

import pytest
import pytest_asyncio

os.environ["TESTING"] = "True"

from alembic import command
from alembic.config import Config

from fastapi import Depends
from fastapi.testclient import TestClient
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from main import app
from src.models.models import Base, User
from src.database.db import get_db, DatabaseSessionManager
from src.services.auth import auth_service
from src.conf.config import config

TEST_SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"
# TEST_SQLALCHEMY_DATABASE_URL = config.TEST_DB_URL

engine = create_async_engine(TEST_SQLALCHEMY_DATABASE_URL, poolclass=NullPool)

TestingSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, expire_on_commit=False, bind=engine
)

test_user = {
    "name": "Bill",
    "username": "Bill",
    "email": "gates@microsoft.com",
    "password": "33344455",
}
user_data = {
    "name": "Stevev",
    "username": "Steve",
    "email": "jobs@gmail.com",
    "password": "66677788",
}


@pytest.fixture(scope="module", autouse=True)
def init_models_wrap():
    async def init_models():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        async with TestingSessionLocal() as session:
            hash_password = auth_service.get_password_hash(test_user["password"])
            current_user = User(
                username=test_user["username"],
                email=test_user["email"],
                password=hash_password,
                confirmed=True,
                role="admin",
            )
            session.add(current_user)
            await session.commit()

    asyncio.run(init_models())


@pytest.fixture(scope="module")
def client():
    app.testing_db_session = TestingSessionLocal()

    # Dependency override
    async def override_get_db():
        try:
            yield app.testing_db_session
        except Exception as err:
            print(err)
            await app.testing_db_session.rollback()
        finally:
            await app.testing_db_session.close()

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)

    del app.testing_db_session

@pytest.fixture(scope="module")
def db_session(client):
    return client.app.testing_db_session

@pytest_asyncio.fixture()
async def get_token():
    token = await auth_service.create_access_token(data={"sub": test_user["email"]})
    return token


@pytest_asyncio.fixture()
async def get_email_token():
    token = auth_service.create_email_token(data={"sub": user_data["email"]})
    return token
