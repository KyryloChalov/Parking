from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.database.db import get_db
from src.models.models import User
from src.repository import users as repositories_users
from src.schemas.user import UserSchema
from src.services.auth import auth_service


async def seed_basic_users(db: AsyncSession = Depends(get_db)):
    """
    генерація базових фейкових юзерів "admin", "moderator", "user", "guest"
    які мають відповідні імена "admin", "moderator", "user", "guest"
    та відповідні ролі "admin", "moderator", "user", "user"
    "guest" відрізняється від "user" тим, що має confirmed=False
    email'и - {"ім'я"}@gmail.com
    паролі у всіх однакові: "123456"
    в разі наявності в базі юзерів с такими іменами, до імен додається "_{N}"
    N - ціле число
    upd: 
    додав юзера "banned" - він як звичайний "user", тільки забанений
    """
    print("basic_users")
    roles = ["admin", "moderator", "user", "guest", "banned"]
    offset = 0

    for role in roles:

        while await repositories_users.get_user_by_email(
                f"{role + (str('_' + str(offset)) if offset > 0 else '')}@gmail.com", db
        ):
            offset += 1

        name_ = f"{role + (str('_' + str(offset)) if offset > 0 else '')}"

        body = UserSchema(
            name=name_,
            username=name_,
            email=name_ + "@gmail.com",
            password="123456",
        )

        body.password = auth_service.get_password_hash(body.password)

        await repositories_users.create_user(body, db)

        user = await repositories_users.get_user_by_email(body.email, db)

        if role == roles[4]:
            user.banned = True
        if role != roles[3]:
            user.confirmed = True
        if role in [roles[0], roles[1], roles[2]]:
            user.role = role

        await db.commit()


async def seed_users(count_users: int = 3, db: AsyncSession = Depends(get_db)):
    """
    генерація кількох фейкових юзерів (за замовченням: count_users: int = 3)
    вони мають імена виду user_N, де N - ціле число,
    яке залежить від кількості юзерів, що вже є в базі
    поле email иає вигляд user_N@gmail.com
    пароль для всіх однаковий: "123456"
    поле confirmed має значення True
    решта полів - за замовченням"""

    print("users")
    result = await db.execute(select(User))
    users = result.scalars().all()
    number_user = len(users) + 1
    offset = 0

    for num in range(number_user, (number_user + count_users)):

        while await repositories_users.get_user_by_email(
                f"user_{str(num + offset)}@gmail.com", db
        ):
            offset += 1

        name_ = f"user_{str(num + offset)}"

        body = UserSchema(
            name=name_,
            username=name_,
            email=name_ + "@gmail.com",
            password="123456",
        )

        body.password = auth_service.get_password_hash(body.password)

        await repositories_users.create_user(body, db)
        await repositories_users.confirmed_email(body.email, db)
