from faker import Faker
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.database.db import get_db
from src.models.models import Photo, User
from src.conf.constants import (
    COMMENT_MIN_LENGTH,
    COMMENT_MAX_LENGTH,
    PHOTO_PATH_LENGTH,
    TRANSFORM_PATH_LENGTH,
    PHOTO_MIN_DESCRIPTION_LENGTH,
    PHOTO_MAX_DESCRIPTION_LENGTH,
)

import random

fake_data: Faker = Faker(["uk_UA", "en_US"])


async def seed_photos(count: int = 10, db: AsyncSession = Depends(get_db)):
    """
    генерація кількох фейкових photo (за замовченням: count: int = 10)
    """
    print("photos")
    result = await db.execute(select(User))
    users = result.scalars().all()
    users_id = []
    for user in users:
        users_id.append(user.id)
    users_id = list(set(users_id))

    for _ in range(count):

        # text = fake_data.paragraph(nb_sentences=1)

        new_photo = Photo(
            path=fake_data.image_url(),
            description=fake_data.text(
                random.randint(
                    PHOTO_MIN_DESCRIPTION_LENGTH, PHOTO_MAX_DESCRIPTION_LENGTH
                )
            )[:-1],
            path_transform=(
                fake_data.image_url() if bool(random.getrandbits(1)) else ""
            ),
            user_id=users_id[random.randint(0, len(users_id) - 1)],
            public_photo_id=fake_data.image_url(),
        )

        db.add(new_photo)
        await db.commit()
        await db.refresh(new_photo)
