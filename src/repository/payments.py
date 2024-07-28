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
from sqlalchemy import update
from src.conf.constants import DAYS_IN_MONTH


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

async def check_payment_exist(session_id: int, db: AsyncSession) -> bool:
    """
    Check if a parking session has a payment.

    :param session_id: int: ID of the parking session
    :param db: AsyncSession: Database session object
    :return: bool - True if a payment exists, False otherwise
    """

    payment_stmt = select(Payment).filter_by(session_id=session_id)
    payment_result = await db.execute(payment_stmt)
    
    # Check if any payment is found
    payment = payment_result.scalar_one_or_none()

    return payment is not None


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


async def get_vehicle_id_from_session(session_id: int, db: AsyncSession) -> int:
    """
    Get the vehicle ID from a parking session.
    :param session_id: int
    :param db: AsyncSession
    :return: int
    """

    query = select(Parking_session.vehicle_id).where(
        Parking_session.id == session_id)
    result = await db.execute(query)
    vehicle_id = result.scalar_one()
    return vehicle_id

async def get_start_end_date_from_session(session_id: int, db: AsyncSession) -> tuple:
    """
    Get the start and end dates from a parking session.
    :param session_id: int
    :param db: AsyncSession
    :return: tuple
    """
    
    # session_id = int(session_id)
    stmt = select(Parking_session).where(Parking_session.id == session_id)
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()

    if session is None:
        #raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found.")
        return None, None

    start_date = session.created_at
    end_date = session.updated_at # or start_date
    return start_date, end_date


async def create_payment(
        user_id: int,
        vehicle_id: int,
        amount: int,
        session_id: Optional[int | None],
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


async def record_payment(session_id: int, amount: int, user_id: int, db: AsyncSession):
    """
    Record a new payment for a vehicle.
    :param license_plate: str
    :param amount: int
    :param user_id: int - id of the parking worker
    :param db: AsyncSession
    :return: dict with payment status and payment ID
    """
    # Find vehicle ID by license plate
    # vehicle_id = await find_vehicle_id_by_plate(license_plate, db)
    # print(vehicle_id)

    # user_id = await find_user_id_by_plate(license_plate, db)
    # print(user_id)

    # Get the most recent parking session for the vehicle
    # session_stmt = (
    #     select(Parking_session.id)
    #     .filter_by(vehicle_id=vehicle_id)
    #     # Order by created_at descending to get the latest session
    #     .order_by(desc(Parking_session.created_at))
    # )
    # session_result = await db.execute(session_stmt)
    # # Get the first result, which is the latest
    # session = session_result.scalars().first()

    # if not session:
    #     raise HTTPException(
    #         status_code=status.HTTP_404_NOT_FOUND,
    #         detail=messages.NO_SESSION_FOUND
    #     )

    session_stmt = select(Parking_session).filter_by(id=session_id)
    session_result = await db.execute(session_stmt)
    session = session_result.scalar_one_or_none()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=messages.NO_SESSION_FOUND
        )
    
    # Record the payment
    new_payment = await create_payment(
        user_id=user_id,
        vehicle_id=session.vehicle_id,
        amount=amount,
        session_id=session.id,
        db=db
    )

    return {"status": "success", "payment_id": new_payment.id, "amount": amount}

async def get_end_date_payment_abonement(vehicle_id: int, db: AsyncSession):
    """
    Get the end date of the abonement payment for a vehicle.
    :param vehicle_id: int
    :param db: AsyncSession
    :return: datetime
    """

    stmt = select(Vehicle.ended_at).filter_by(id=vehicle_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def update_end_date_payment_abonement(vehicle_id: int, new_end_date: datetime, db: AsyncSession):
    """
    Update the end date of the abonement payment for a vehicle.
    :param vehicle_id: int
    :param new_end_date: datetime
    :param db: AsyncSession
    :return: None
    """

    try:
        stmt = (
            update(Vehicle)
            .where(Vehicle.id == vehicle_id)
            .values(ended_at=new_end_date)
            .execution_options(synchronize_session="fetch")
        )

        await db.execute(stmt)
        await db.commit()

    except Exception as e:
        await db.rollback()
        print(f"An error occurred while updating the vehicle's end date: {e}")


async def record_monthly_payment(license_plate: str, amount: int, user_id: int, number_of_months: int, db: AsyncSession):
    """
    Record a new monthly payment for a vehicle.
    :param license_plate: str
    :param amount: int
    :param user_id: int - id of the parking worker
    :last_day: datetime - last day of the payment
    :param db: AsyncSession
    :return: dict with payment status and payment ID
    """

    vehicle_id = await find_vehicle_id_by_plate(license_plate, db)

    existing_end_date = await get_end_date_payment_abonement(vehicle_id, db)

    if existing_end_date:
        last_day = existing_end_date + timedelta(days=DAYS_IN_MONTH*number_of_months)     
    else:
        last_day = datetime.now() + timedelta(days=DAYS_IN_MONTH*number_of_months)

    await update_end_date_payment_abonement(vehicle_id, last_day, db)

    new_payment = await create_payment(
        user_id=user_id,
        vehicle_id=vehicle_id,
        amount=amount,
        session_id=None,
        db=db,
    )

    if new_payment:
        return {"status": "success", "payment_id": new_payment.id, "amount": amount, "payment_till": last_day}
    else:
        return {"status": "failed"}


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


async def get_rate_by_name(name: str, db: AsyncSession):
    """
    Get the rate by name.
    :param name: str
    :db: AsyncSession
    :return: int
    """

    stmt = select(Rate).where(Rate.rate_name == name.lower())
    try:
        result = await db.execute(stmt)
        rate = result.scalar_one()
        return rate.price
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=messages.RATE_NOT_FOUND + ": " + name
        )


async def calculate_parking_fee(start_time: datetime, end_time: datetime, db: AsyncSession):
    """
    Calculate the parking fee based on the start and end times.
    :param start_time: datetime
    :param end_time: datetime
    :param db: AsyncSession
    :return: int
    """

    # Get rates
    hourly_rate = await get_rate_by_name("hourly", db)
    daily_rate = await get_rate_by_name("daily", db)
    monthly_rate = await get_rate_by_name("monthly", db)

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
        months = ceil(days / DAYS_IN_MONTH)
        fee = months * monthly_rate

    return fee


async def calculate_monthly_fee(months_number: int, db: AsyncSession):
    """
    Calculate the monthly fee based on the number of months.
    :param months_number: int
    :param db: AsyncSession
    :return: int
    """

    monthly_rate = await get_rate_by_name("monthly", db)
    fee = months_number * monthly_rate
    return fee

