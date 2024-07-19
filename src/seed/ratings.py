from faker import Faker
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.database.db import get_db
from src.models.models import Photo, User, Rating
from src.conf.constants import COMMENT_MIN_LENGTH, COMMENT_MAX_LENGTH

import random

fake_data: Faker = Faker(["uk_UA", "en_US"])


async def seed_ratings(db: AsyncSession = Depends(get_db)):
    """
    генерація кількох фейкових comments (за замовченням: count: int = 100)
    """
    print("ratings")
    result = await db.execute(select(User))
    users = result.scalars().all()
    users_id = []
    for user in users:
        users_id.append(user.id)
    users_id = list(set(users_id))
    # print(f"{users_id = }")
    # print(f"{len(users_id) = }")

    result = await db.execute(select(Photo))
    photos = result.scalars().all()
    photos_id = []
    for photo in photos:
        photos_id.append(photo.id)
    photos_id = list(set(photos_id))
    # print(f"{photos_id = }")
    # print(f"{len(photos_id) = }")

    count = len(users_id) * len(photos_id) // 2
    # print(f"+++++++++++ {count = }")
    for _ in range(count):
        new_rating = Rating(
            rating=random.randint(1, 5),
            user_id=users_id[random.randint(0, len(users_id) - 1)],
            photo_id=photos_id[random.randint(0, len(photos_id) - 1)],
        )

        db.add(new_rating)
        await db.commit()
        await db.refresh(new_rating)
