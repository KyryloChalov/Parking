from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from src.database.db import get_db
from src.models.models import Rate


async def seed_rates(base: int = 10, db: AsyncSession = Depends(get_db)):
    """
    генерація ((del and create_new) if exist) rates (4 штуки)
    базова ціна (base) множимо на (10**i), i - індекс в rate_names[]
    """
    print("rates")
    result = await db.execute(select(Rate))
    number_rates = len(result.scalars().all())
    # print(number_rates)

    if number_rates > 0:
        delete_stmt = delete(Rate)
        await db.execute(delete_stmt)
        await db.commit()

    rate_names = ["hourly", "daily", "monthly", "custom"]
    count = len(rate_names)

    for i in range(count):
        name = rate_names[i]
        price = base * (10**i)

        new_rate = Rate(rate_name=name, price=price)

        db.add(new_rate)
        await db.commit()
        await db.refresh(new_rate)
