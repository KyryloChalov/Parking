import random
from datetime import datetime, timedelta

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from src.database.db import get_db
from src.models.models import Vehicle, Parking_session


def random_date_in():

    # Поточна дата та час
    date_ = datetime.now()

    # Випадкове число днів від 1 до 30 (або 31)
    random_days = timedelta(days=random.randint(1, 31))

    # Випадковий проміжок часу (години, хвилини, секунди)
    random_hours = timedelta(hours=random.randint(0, 23))
    random_minutes = timedelta(minutes=random.randint(0, 59))
    random_seconds = timedelta(seconds=random.randint(0, 59))

    # Віднімаємо цей проміжок часу від поточної дати та часу
    new_datetime = date_ - random_days - random_hours - random_minutes - random_seconds

    # print("Нова дата та час:", new_datetime)
    return new_datetime


def random_date_out(date_in_):
    # Випадковий проміжок часу від 15 хвилин до 2 днів
    random_time = timedelta(minutes=random.randint(15, 60 * 24 * 2))

    # Додамо цей випадковий проміжок часу до попередньо обчисленої нової дати та часу
    new_datetime_with_random_time = date_in_ + random_time

    # Перевірка, щоб нова дата була не більше ніж поточний час
    current_datetime = datetime.now()
    if new_datetime_with_random_time > current_datetime:
        new_datetime_with_random_time = current_datetime

    # Ось ваш об'єкт datetime.datetime:
    # print("Нова дата та час:", new_datetime_with_random_time)
    return new_datetime_with_random_time


async def seed_sessions(num_sessions: int = 20, left_in: int = 3, db: AsyncSession = Depends(get_db)):
    """
    генерація кількох фейкових sessions 
    """
    print("sessions")
    # видаляти дані з таблиці? поки що ні
    # result = await db.execute(select(Parking_session))
    # number_vehicle = len(result.scalars().all())
    # print(f"{number_vehicle = }")
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
    # print(f"{vehicles_id = }")
    # print(f"{len(vehicles_id) = }")
    # print(f"{min(vehicles_id) = }")
    # print(f"{max(vehicles_id) = }")

    for i in range(num_sessions):
        rnd_ = random.randint(1, len(vehicles_id)) - 1
        vehicle_id = vehicles_id[rnd_]

        date_in = random_date_in()
        date_out = random_date_out(date_in)

        new_session = Parking_session(
            vehicle_id=vehicle_id,
            created_at=date_in,
            # останні left_in ще не виїхали з парковки
            updated_at=date_out if i < (num_sessions - left_in) else None,
        )

        db.add(new_session)
        await db.commit()
        await db.refresh(new_session)
