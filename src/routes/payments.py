import pickle

from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from src.database.db import get_db
from src.models.models import User, Role
from src.services.auth import auth_service
from src.conf import messages
from src.repository import payments as repositories_payments
from typing import Optional, List

router = APIRouter(prefix="/payments", tags=["payments"])

@router.post("/monthly_abonement")
async def abonement_payment(
    license_plate: str,
    number_of_months:  int = Query(1, ge=1, le=12),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user)
):
    """
    Abonement payment

    :param license_plate: str: Specify the license plate of the vehicle
    :param number_of_months: int: Specify the number of months for the abonement
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Get the current user
    :return: A payment object
    """
    
    if user.role != Role.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=messages.USER_NOT_HAVE_PERMISSIONS)
    
    amount = await repositories_payments.calculate_monthly_fee(number_of_months, db)

    payment_info = await repositories_payments.record_monthly_payment(license_plate, amount, user.id, number_of_months, db)

    return payment_info


@router.post("/{session_id}")
async def post_payment(
    session_id: int,
    # amount: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user)
):
    """
    Create a payment for a session

    :param session_id: int: Specify the session id
    :param amount: Optional[int]: Specify the amount to be paid
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Get the current user
    :return: A payment object
    """

    if user.role != Role.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=messages.USER_NOT_HAVE_PERMISSIONS)
    
    start_date, end_date = await repositories_payments.get_start_end_date_from_session(session_id, db)

    
    if not start_date:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=messages.SESSION_NOT_FOUND)
    
    if not end_date:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=messages.SESSION_NOT_CLOSED)
    
    vehicle_id = await repositories_payments.get_vehicle_id_from_session(session_id, db)
    
    end_abonement_date = await repositories_payments.get_end_date_payment_abonement(vehicle_id, db)

    #license_plate = await repositories_payments.get_vehicle_id_from_session(vehicle_id, db)
    
    # Convert end_abonement_date and start_date to date objects (remove time)
    # end_abonement_date is date
    start_date_date = start_date.date()
    end_date_date = end_date.date()

    session_payed = await repositories_payments.check_payment_exist(session_id, db)

    if session_payed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=messages.PAYMENT_FOR_SESSION_EXISTS)

    amount = await repositories_payments.calculate_parking_fee(start_date, end_date, db)

    # abonement
    if end_abonement_date is not None:
        #
        if end_abonement_date >= end_date_date:
            amount = 0
        elif start_date_date < end_abonement_date < end_date:
            amount = await repositories_payments.calculate_parking_fee(end_abonement_date, end_date, db)
        
    if amount == 0:
        payment_info =  {"message": "No need to pay", "abonement_active_till": end_abonement_date}
    else:
        payment_info = await repositories_payments.record_payment(session_id, amount, user.id, db)

    return payment_info


@router.get("/{license_plate}")
async def get_last_10_payments(
    license_plate: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user)
):
    """
    Get list of last 10 payments for a vehicle

    :param license_plate: str: Specify the license plate of the vehicle
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Get the current user
    :return: A list of payments
    """

    if user.role != Role.admin and user.role != Role.user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=messages.USER_NOT_HAVE_PERMISSIONS)

    payments = await repositories_payments.get_last_payments(license_plate, db)

    return payments


@router.get("/calculate")
async def calculate_payment(
    start_time: datetime,
    end_time: datetime,
    icense_plate: Optional[str] = Query(
        None, description="License plate of the vehicle"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user)
):
    """
    Calculate the parking fee for a given time range

    :param start_time: datetime: Specify the start time of the parking session
    :param end_time: datetime: Specify the end time of the parking session
    :param icense_plate: Optional[str]: Specify the license plate of the vehicle
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Get the current user
    :return: The calculated parking fee
    """
    
    if user.role != Role.admin and user.role != Role.user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=messages.USER_NOT_HAVE_PERMISSIONS)

    amount = await repositories_payments.calculate_parking_fee(start_time, end_time, db)

    return {"amount": amount}
