import pickle

from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from src.database.db import get_db
from src.models.models import User, Role
from src.services.auth import auth_service
from src.conf import messages
from src.repository import payments as repositories_payments
from typing import Optional

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/{license_plate}")
async def post_payment(
    license_plate: str,
    amount: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user)
):
    if user.role != Role.admin and user.role != Role.user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=messages.USER_NOT_HAVE_PERMISSIONS)

    if not amount:
        # TODO: get start_time and end_time from the sessions db
        start_time = datetime.now()-timedelta(hours=2)
        end_time = datetime.now()
        amount = await repositories_payments.calculate_parking_fee(start_time, end_time, db)

    payment_info = await repositories_payments.record_payment(license_plate, amount, user.id, db)
    return payment_info


@router.get("/{license_plate}")
async def get_last_10_payments(
    license_plate: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user)
):
    if user.role != Role.admin and user.role != Role.user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=messages.USER_NOT_HAVE_PERMISSIONS)

    payments = await repositories_payments.get_last_payments(license_plate, db)
    return payments


@router.get("/calculate")
async def calculate_payment(
    start_time: datetime,
    end_time: datetime,
    # icense_plate: Optional[str] = Query(
    #     None, description="License plate of the vehicle"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user)
):
    if user.role != Role.admin and user.role != Role.user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=messages.USER_NOT_HAVE_PERMISSIONS)

    amount = await repositories_payments.calculate_parking_fee(start_time, end_time, db)
    return {"calculated_amount": amount}
