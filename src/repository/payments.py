from fastapi import Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from math import ceil
from typing import Optional
from datetime import timedelta, datetime

from src.conf import messages
from src.database.db import get_db
from src.models.models import Vehicle, Payment, Parking_session, Rate

async def find_vehicle_id_by_plate(license_plate: str, db: AsyncSession):
    vehicle_stmt = select(Vehicle).filter_by(license_plate=license_plate)
    vehicle_result = await db.execute(vehicle_stmt)
    vehicle = vehicle_result.scalar_one_or_none()

    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.VEHICLE_NOT_FOUND
        )

    return vehicle.id

async def find_user_id_by_plate(license_plate: str, db: AsyncSession) -> int:
    query = select(Vehicle.owner_id).where(Vehicle.license_plate == license_plate)
    result = await db.execute(query)
    user_id = result.scalar_one()
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.VEHICLE_NOT_FOUND
        )
    return user_id

async def create_payment(
        user_id: int,
        vehicle_id: int, 
        amount: int, 
        session_id: Optional[int], 
        db: AsyncSession
):
    new_payment = Payment(vehicle_id=vehicle_id, amount=amount, session_id=session_id)
    db.add(new_payment)
    await db.commit()
    await db.refresh(new_payment)
    return new_payment


async def record_payment(license_plate: str, amount: int, db: AsyncSession):
    # Find vehicle ID by license plate
    vehicle_id = await find_vehicle_id_by_plate(license_plate, db)
    print(vehicle_id)

    user_id = await find_user_id_by_plate(license_plate, db)
    print(user_id)

    # Get the current parking session for the vehicle
    session_stmt = select(Parking_session).filter_by(vehicle_id=vehicle_id)
    session_result = await db.execute(session_stmt)
    session = session_result.scalar_one_or_none()

    # Record the payment
    new_payment = await create_payment(
        user_id=user_id,
        vehicle_id=vehicle_id,        
        amount=amount,
        session_id=session.id if session else None,
        db=db,
    )

    return {"status": "success", "payment_id": new_payment.id}

async def get_last_payments(license_plate: str, db: AsyncSession):
    vehicle_stmt = select(Vehicle).filter_by(license_plate=license_plate)
    vehicle_result = await db.execute(vehicle_stmt)
    vehicle = vehicle_result.scalar_one_or_none()

    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.VEHICLE_NOT_FOUND
        )

    payment_stmt = (
        select(Payment).filter_by(vehicle_id=vehicle.id).order_by(Payment.created_at.desc()).limit(10)
    )
    payments_result = await db.execute(payment_stmt)
    return payments_result.scalars().all()


async def calculate_parking_fee(start_time: datetime, end_time: datetime, db: AsyncSession):
    # Get the rates from the database
    # 1: hourly, 2: daily, 3: monthly
    rate_stmt = select(Rate).order_by(Rate.id)  
    rates_result = await db.execute(rate_stmt)
    rates = rates_result.scalars().all()

    if len(rates) < 3:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Rates not configured properly."
        )

    hourly_rate = rates[0].price
    daily_rate = rates[1].price
    monthly_rate = rates[2].price

    # Calculate parking duration
    duration = end_time - start_time
    hours = ceil(duration.total_seconds() / 3600)
    days = ceil(duration.total_seconds() / (3600 * 24))

    # Determine fee
    if hours < 10:
        fee = hours * hourly_rate
    elif 10 <= hours < 240:  # Less than 10 days
        fee = days * daily_rate
    else:  # 10 days or more
        months = ceil(days / 30)
        fee = months * monthly_rate

    return fee

