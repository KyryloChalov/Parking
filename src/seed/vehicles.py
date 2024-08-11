# from faker import Faker
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from src.database.db import get_db
from src.models.models import Vehicle, User, Rate

import random

# import datetime

# fake_data: Faker = Faker(["uk_UA", "en_US"])


async def seed_vehicles(db: AsyncSession = Depends(get_db)):
    """
    генерація кількох фейкових vehicles зі списку license_plates
    """
    print("vehicles")
    result = await db.execute(select(Vehicle))
    number_vehicle = len(result.scalars().all())
    # print(f"{number_vehicle = }")
    if number_vehicle > 0:
        delete_stmt = delete(Vehicle)
        await db.execute(delete_stmt)
        await db.commit()

    result = await db.execute(select(User))
    users = result.scalars().all()
    users_id = []
    for user in users:
        users_id.append(user.id)
    users_id = list(set(users_id))
    # print(f"{users = }")
    # print(f"{users_id = }")
    # print(f"{len(users_id) = }")

    result = await db.execute(select(Rate))
    rates = result.scalars().all()
    rates_id = []
    for rate in rates:
        rates_id.append(rate.id)
    rates_id = list(set(rates_id))
    # print(f"{rates = }")
    # print(f"{rates_id = }")
    # print(f"{len(rates_id) = }")

    license_plates = [
        "AE1455KH",  # 0 - вільний
        "BM8780EC",  # 1
        "BA5486HE",  # 2
        "BE0394EE",  # 3
        "AX0787CO",  # 4
        "BM7462BI",  # 5
        "BA9635HA",  # 6
        "BK9358HH",  # 7
        "BM0485CM",  # 8
        "AB6924KK",  # 9
        "KA7777AC",  # 10
        "KA3792KK",  # 11
        "AA3003OB",  # 12
        "AM3808CO",  # 13 - край
        "AE6638KK",  # 14 - guest
        "KA8781IO",  # 15 - guest
        "AA6418XA",  # 16 - guest
        "БУБОЧКА",  # 17 - guest
    ]
    # print(f"{license_plates = }")

    i = 0
    for user_id in users_id:
        i += 1
        # print(f"{i = }")
        # owner_id = user_id
        # license_plate = license_plates[i]
        # print(f"{owner_id = } <--> {license_plate = }")
        new_vehicle = Vehicle(
            license_plate=license_plates[i],
            owner_id=user_id,
            # rate_id=rates_id[random.randint(0, len(rates_id) - 1)],
            # останній з rates виключаємо з рандому
            rate_id=rates_id[random.randint(0, len(rates_id) - 2)],
            # created_at="2024-07-26T23:03:29.641Z",
            # updated_at="2024-07-26T23:03:29.641Z",
            # created_at=datetime.datetime.now(),
        )
        db.add(new_vehicle)
        await db.commit()
        await db.refresh(new_vehicle)

    # print(f"{len(license_plates) = }")
    # print(f"{len(users_id) = }")
    if len(license_plates) > len(users_id):
        num_additional_vehicles = len(license_plates) - len(users_id) - 4  # 3 шт
        for num in range(1, num_additional_vehicles):
            # print(license_plates[num+len(users_id)])
            # print(users_id[random.randint(0, len(users_id)-1)])
            new_vehicle = Vehicle(
                license_plate=license_plates[num + len(users_id)],
                owner_id=users_id[random.randint(0, len(users_id) - 1)],
                rate_id=rates_id[random.randint(0, len(rates_id) - 1)],
                # created_at="2024-07-26T23:03:29.641Z",
                # updated_at="2024-07-26T23:03:29.641Z",
                # created_at=datetime.datetime.now(),
            )
            db.add(new_vehicle)
            await db.commit()
            await db.refresh(new_vehicle)
