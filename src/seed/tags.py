from faker import Faker
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.models.models import Tag
from src.conf.constants import TAG_MIN_LENGTH, TAG_MAX_LENGTH

import random

fake_data: Faker = Faker(["uk_UA", "en_US"])


async def seed_tags(count: int = 10, db: AsyncSession = Depends(get_db)):
    """
    генерація кількох фейкових tags (за замовченням: count: int = 10)
    """
    print("tags")
    for _ in range(count):
        name_tag = ""
        name_tag = fake_data.text(random.randint(TAG_MIN_LENGTH, TAG_MAX_LENGTH))
        # print(f"{name_tag = }")

        new_tag = Tag(name=name_tag[:-1])

        db.add(new_tag)
        await db.commit()
        await db.refresh(new_tag)
