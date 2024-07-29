from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from src.models.models import Parking_session, Payment, Vehicle, User


async def get_parking_data(start_date: datetime, end_date: datetime, db: AsyncSession):
    query = (
        select(
            Parking_session.id,
            Vehicle.license_plate,
            User.username,
            Parking_session.created_at,
            Parking_session.updated_at,
            Payment.amount,
            Payment.created_at,
        )
        .join(Vehicle, Parking_session.vehicle_id == Vehicle.id)
        .join(User, Vehicle.owner_id == User.id)
        .join(Payment, Payment.session_id == Parking_session.id)
        .where(Payment.created_at >= start_date)
        .where(Payment.created_at <= end_date)
    )
    # result = await db.execute(query)
    # return result.all()
    result = await db.execute(query)
    records = result.all()
    print(f"1. {records = }")

    return records
