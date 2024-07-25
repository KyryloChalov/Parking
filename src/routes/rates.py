from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.schemas.rates import RateSchema, RateResponseSchema, RateUpdateSchema
from src.repository import rates as repository_rates
from src.services.auth import auth_service
from src.models.models import User, Role
from src.conf import messages

router = APIRouter(prefix="/rates", tags=["rates"])

@router.post("/", response_model=RateResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_rate(
    rate: RateSchema,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user)
):
    """
    Create a new rate. If a rate with the same name already exists, raises an error.
    Only accessible to admins.

    :param rate: RateSchema: Validate the request body
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Get the current user
    :return: A rate object
    """
    if user.role != Role.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=messages.USER_NOT_HAVE_PERMISSIONS)

    return await repository_rates.create_rate(rate, db)

@router.get("/", response_model=list[RateResponseSchema])
async def get_rates(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user)
):
    """
    Retrieve all existing rates.
    Only accessible to admins and users.

    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Get the current user
    :return: A list of rates
    """
    if user.role != Role.admin and user.role != Role.user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=messages.USER_NOT_HAVE_PERMISSIONS)

    return await repository_rates.get_all_rates(db)

@router.patch("/{rate_id}", response_model=RateResponseSchema)
async def update_rate(
    rate_id: int,
    rate_update: RateUpdateSchema,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user)
):
    """
    Update the price of a rate by its ID.
    Only accessible to admins.

    :param rate_id: int: Specify the rate to be updated
    :param rate_update: RateUpdateSchema: Validate the request body
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Get the current user
    :return: The updated rate object
    """
    if user.role != Role.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=messages.USER_NOT_HAVE_PERMISSIONS)

    return await repository_rates.update_rate(rate_id, rate_update, db)

@router.delete("/{rate_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rate(
    rate_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user)
):
    """
    Delete a rate by its ID.
    Only accessible to admins.

    :param rate_id: int: Specify the rate to be deleted
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Get the current user
    :return: None
    """
    if user.role != Role.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=messages.USER_NOT_HAVE_PERMISSIONS)

    await repository_rates.delete_rate(rate_id, db)
    return None

