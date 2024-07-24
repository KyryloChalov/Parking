from fastapi import HTTPException, status
from sqlalchemy import select, update, delete, func, extract, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from src.models.models import Rate
from src.schemas.rates import RateSchema, RateUpdateSchema
from src.conf import messages


async def get_all_rates(db: AsyncSession):
    """
    Get all rates from the database.
    :param db: AsyncSession
    :return: List[Rate]
    """
    stmt = select(Rate).order_by(Rate.id)
    result = await db.execute(stmt)
    return result.scalars().all()

async def create_rate(rate: RateSchema, db: AsyncSession):
    """
    Create a new rate in the database.
    :param rate: RateSchema
    :param db: AsyncSession
    :return: Rate
    """
    existing_rate_stmt = select(Rate).filter_by(rate_name=rate.rate_name)
    existing_rate_result = await db.execute(existing_rate_stmt)
    existing_rate = existing_rate_result.scalar_one_or_none()

    if existing_rate:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=messages.RATE_ALREADY_EXISTS + ": " + rate.rate_name
        )
    new_rate = Rate(rate_name=rate.rate_name, price=rate.price)
    db.add(new_rate)
    await db.commit()
    await db.refresh(new_rate)
    return new_rate

async def update_rate(rate_id: int, rate_update: RateUpdateSchema, db: AsyncSession):
    """
    Update an existing rate in the database.
    :param rate_id: int
    :param rate_update: RateUpdateSchema
    :param db: AsyncSession
    :return: Rate
    """
    stmt = select(Rate).filter_by(id=rate_id)
    result = await db.execute(stmt)
    existing_rate = result.scalar_one_or_none()

    if existing_rate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.RATE_NOT_FOUND)

    update_stmt = (
        update(Rate)
        .where(Rate.id == rate_id)
        .values(price=rate_update.price, updated_at=func.now())
        .execution_options(synchronize_session="fetch")
    )
    await db.execute(update_stmt)
    await db.commit()

    result = await db.execute(select(Rate).filter_by(id=rate_id))
    return result.scalar_one()

async def delete_rate(rate_id: int, db: AsyncSession):
    """
    Delete a rate by its ID.
    :param rate_id: int
    :param db: AsyncSession
    :return: None
    """
    stmt = select(Rate).filter_by(id=rate_id)
    result = await db.execute(stmt)
    existing_rate = result.scalar_one_or_none()

    if existing_rate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.RATE_NOT_FOUND)

    delete_stmt = delete(Rate).where(Rate.id == rate_id)
    await db.execute(delete_stmt)
    await db.commit()

