from fastapi import Depends, HTTPException, status
from sqlalchemy import select, func, desc
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from math import ceil
from typing import Optional
from datetime import timedelta, datetime

from src.conf import messages
from src.database.db import get_db
from src.models.models import Vehicle, Payment, Parking_session, Rate


async def find_vehicle_id_by_plate(license_plate: str, db: AsyncSession):
    """
    Find the vehicle ID by license plate.
    Raises an HTTPException if the vehicle is not found.
    :param license_plate: str
    :param db: AsyncSession
    :return: int
    """
    vehicle_stmt = select(Vehicle).filter_by(license_plate=license_plate)
    vehicle_result = await db.execute(vehicle_stmt)
    vehicle = vehicle_result.scalar_one_or_none()

    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.VEHICLE_NOT_FOUND
        )

    return vehicle.id


async def find_user_id_by_plate(license_plate: str, db: AsyncSession) -> int:
    """
    Find the user ID by license plate.
    Raises an HTTPException if the vehicle is not found.
    :param license_plate: str
    :param db: AsyncSession
    :return: int
    """
    query = select(Vehicle.owner_id).where(
        Vehicle.license_plate == license_plate)
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
    """
    Create a new payment.
    :param user_id: int
    :param vehicle_id: int
    :param amount: int
    :param session_id: Optional[int]
    :param db: AsyncSession
    :return: Payment
    """
    new_payment = Payment(user_id=user_id, vehicle_id=vehicle_id,
                          amount=amount, session_id=session_id)
    db.add(new_payment)
    await db.commit()
    await db.refresh(new_payment)
    return new_payment


async def record_payment(license_plate: str, amount: int, user_id: int, db: AsyncSession):
    """
    Record a new payment for a vehicle.
    :param license_plate: str
    :param amount: int
    :param user_id: int - id of the parking worker
    :param db: AsyncSession
    :return: dict with payment status and payment ID
    """
    # Find vehicle ID by license plate
    vehicle_id = await find_vehicle_id_by_plate(license_plate, db)
    # print(vehicle_id)

    # user_id = await find_user_id_by_plate(license_plate, db)
    # print(user_id)

    # Get the most recent parking session for the vehicle
    session_stmt = (
        select(Parking_session.id)
        .filter_by(vehicle_id=vehicle_id)
        # Order by created_at descending to get the latest session
        .order_by(desc(Parking_session.created_at))
    )
    session_result = await db.execute(session_stmt)
    # Get the first result, which is the latest
    session = session_result.scalars().first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=messages.NO_SESSION_FOUND
        )

    # Record the payment
    new_payment = await create_payment(
        user_id=user_id,
        vehicle_id=vehicle_id,
        amount=amount,
        session_id=session,
        db=db,
    )

    return {"status": "success", "payment_id": new_payment.id}


async def get_last_payments(license_plate: str, db: AsyncSession):
    """
    Get the last payments for a vehicle.
    :param license_plate: str
    :param db: AsyncSession
    :return: list of Payment
    """
    vehicle_stmt = select(Vehicle).filter_by(license_plate=license_plate)
    vehicle_result = await db.execute(vehicle_stmt)
    vehicle = vehicle_result.scalar_one_or_none()

    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.VEHICLE_NOT_FOUND
        )

    payment_stmt = (
        select(Payment).filter_by(vehicle_id=vehicle.id).order_by(
            Payment.created_at.desc()).limit(10)
    )
    payments_result = await db.execute(payment_stmt)
    return payments_result.scalars().all()


async def calculate_parking_fee(start_time: datetime, end_time: datetime, db: AsyncSession):
    """
    Calculate the parking fee based on the start and end times.
    :param start_time: datetime
    :param end_time: datetime
    :param db: AsyncSession
    :return: int
    """
    # function to get the rate by name
    async def get_rate_by_name(name: str):
        """
        Get the rate by name.
        :param name: str
        :return: int
        """
        stmt = select(Rate).where(Rate.rate_name == name.lower())
        try:
            result = await db.execute(stmt)
            rate = result.scalar_one()
            return rate.price
        except NoResultFound:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=messages.RATE_NOT_FOUND + ": " + name
            )

    # Get rates from the database
    hourly_rate = await get_rate_by_name("hourly")
    daily_rate = await get_rate_by_name("daily")
    monthly_rate = await get_rate_by_name("monthly")

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
