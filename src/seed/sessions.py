from faker import Faker
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from src.database.db import get_db
from src.models.models import Vehicle, User, Rate, Parking_session

import random
# import datetime

fake_data: Faker = Faker(["uk_UA", "en_US"])


async def seed_sessions(num_sessions: int = 100, db: AsyncSession = Depends(get_db)):
    """
    генерація кількох фейкових sessions зі списку
    """
    print("sessions")
    result = await db.execute(select(Parking_session))
    number_vehicle = len(result.scalars().all())
    print(f"{number_vehicle = }")
    # if number_vehicle > 0:
    #     delete_stmt = delete(Parking_session)
    #     await db.execute(delete_stmt)
    #     await db.commit()

    result = await db.execute(select(Vehicle))
    vehicles = result.scalars().all()
    vehicles_id = []
    for vehicle in vehicles:
        vehicles_id.append(vehicle.id)
    vehicles_id = list(set(vehicles_id))
    # print(f"{vehicles = }")
    print(f"{vehicles_id = }")
    print(f"{len(vehicles_id) = }")

    # result = await db.execute(select(Rate))
    # rates = result.scalars().all()
    # rates_id = []
    # for rate in rates:
    #     rates_id.append(rate.id)
    # rates_id = list(set(rates_id))
    # # print(f"{rates = }")
    # # print(f"{rates_id = }")
    # # print(f"{len(rates_id) = }")

    # print(f"{license_plates = }")

    # i = 0
    # for user_id in users_id:
    #     i += 1
    #     # print(f"{i = }")
    #     # owner_id = user_id
    #     # license_plate = license_plates[i]
    #     # print(f"{owner_id = } <--> {license_plate = }")
    #     new_vehicle = Vehicle(
    #         license_plate=license_plates[i],
    #         owner_id=user_id,
    #         rate_id=rates_id[random.randint(0, len(rates_id)-1)],
    #         # created_at="2024-07-26T23:03:29.641Z",
    #         # updated_at="2024-07-26T23:03:29.641Z",
    #         # created_at=datetime.datetime.now(),
    #     )
    #     db.add(new_vehicle)
    #     await db.commit()
    #     await db.refresh(new_vehicle)

    # # print(f"{len(license_plates) = }")
    # # print(f"{len(users_id) = }")
    # if len(license_plates) > len(users_id):
    #     num_additional_vehicles = len(license_plates) - len(users_id)-3 # 3 шт
    #     for num in range(1, num_additional_vehicles):
    #         # print(license_plates[num+len(users_id)])
    #         # print(users_id[random.randint(0, len(users_id)-1)])
    #         new_vehicle = Vehicle(
    #             license_plate=license_plates[num+len(users_id)],
    #             owner_id=users_id[random.randint(0, len(users_id)-1)],
    #             rate_id=rates_id[random.randint(0, len(rates_id)-1)],
    #             # created_at="2024-07-26T23:03:29.641Z",
    #             # updated_at="2024-07-26T23:03:29.641Z",
    #             # created_at=datetime.datetime.now(),
    #         )
    #         db.add(new_vehicle)
    #         await db.commit()
    #         await db.refresh(new_vehicle)
