from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from src.database.db import get_db
from src.models.models import Setting


async def seed_settings(db: AsyncSession = Depends(get_db)):
    """
    генерація рядка settings
    """
    print("settings")
    result = await db.execute(select(Setting))
    number_settings = len(result.scalars().all())
    # print(number_settings)

    if number_settings > 0:
        delete_stmt = delete(Setting)
        await db.execute(delete_stmt)
        await db.commit()

    new_settings = Setting(capacity=30, num_days_reminder=3, num_days_benefit=2)

    db.add(new_settings)
    await db.commit()
    await db.refresh(new_settings)
