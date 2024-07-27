from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from src.database.db import get_db
from src.models.models import User
from src.repository import users as repositories_users
from src.schemas.user import UserSchema
from src.services.auth import auth_service


async def seed_users(db: AsyncSession = Depends(get_db)):
    """
    генерація фейкових юзерів:
    "admin" - 2 шт, "user" - 7 шт, "guest" - 1 шт
    які мають відповідні імена "admin", "user", "guest"
    та відповідні ролі "admin", "user", "guest"
    "guest" відрізняється від "user" тим, що має confirmed=False
    email'и - {"ім'я"}@gmail.com
    user'и мають імена виду user_N, де N - ціле число від 1 до 7,
    поле email має вигляд user_N@gmail.com
    пароль для всіх однаковий: "123456"
    поле confirmed має значення True
    решта полів - за замовченням
    в разі, якщо вже є юзери в бд, їх буде видалено
    """

    print("users")
    result = await db.execute(select(User))
    number_user = len(result.scalars().all())
    if number_user > 0:
        delete_stmt = delete(User)
        await db.execute(delete_stmt)
        await db.commit()

    name_ = "admin"
    # print(f"{name_ = }")
    new_user = UserSchema(
        name=name_,
        username=name_,
        email=name_ + "@gmail.com",
        password="123456",
    )
    new_user.password = auth_service.get_password_hash(new_user.password)
    await repositories_users.create_user(new_user, db)
    await repositories_users.confirmed_email(new_user.email, db)
    user = await repositories_users.get_user_by_email(new_user.email, db)
    user.role = "admin"
    await db.commit()

    name_ = "admin_1"
    # print(f"{name_ = }")
    new_user = UserSchema(
        name=name_,
        username=name_,
        email=name_ + "@gmail.com",
        password="123456",
    )
    new_user.password = auth_service.get_password_hash(new_user.password)
    await repositories_users.create_user(new_user, db)
    await repositories_users.confirmed_email(new_user.email, db)
    user = await repositories_users.get_user_by_email(new_user.email, db)
    user.role = "admin"
    await db.commit()

    for num in range(1, 8):
        name_ = f"user_{str(num)}"
        new_user = UserSchema(
            name=name_,
            username=name_,
            email=name_ + "@gmail.com",
            password="123456",
            role="user",
        )
        new_user.password = auth_service.get_password_hash(new_user.password)
        await repositories_users.create_user(new_user, db)
        await repositories_users.confirmed_email(new_user.email, db)

    name_ = "guest"
    # print(f"{name_ = }")
    new_user = UserSchema(
        name=name_,
        username=name_,
        email=name_ + "@gmail.com",
        password="123456",
    )
    new_user.password = auth_service.get_password_hash(new_user.password)
    await repositories_users.create_user(new_user, db)
    user = await repositories_users.get_user_by_email(new_user.email, db)
    user.role = "guest"
    await db.commit()
