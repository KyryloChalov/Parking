from fastapi import HTTPException, status
from sqlalchemy import select, update, delete, func, extract, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from src.models.models import Rate
from src.schemas.rates import RateSchema, RateUpdateSchema


async def get_all_rates(db: AsyncSession):
    stmt = select(Rate).order_by(Rate.id)
    result = await db.execute(stmt)
    return result.scalars().all()

async def create_rate(rate: RateSchema, db: AsyncSession):
    existing_rate_stmt = select(Rate).filter_by(rate_name=rate.rate_name)
    existing_rate_result = await db.execute(existing_rate_stmt)
    existing_rate = existing_rate_result.scalar_one_or_none()

    if existing_rate:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Rate with name '{rate.rate_name}' already exists."
        )
    new_rate = Rate(rate_name=rate.rate_name, price=rate.price)
    db.add(new_rate)
    await db.commit()
    await db.refresh(new_rate)
    return new_rate

async def update_rate(rate_id: int, rate_update: RateUpdateSchema, db: AsyncSession):
    stmt = select(Rate).filter_by(id=rate_id)
    result = await db.execute(stmt)
    existing_rate = result.scalar_one_or_none()

    if existing_rate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rate not found")

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
    stmt = select(Rate).filter_by(id=rate_id)
    result = await db.execute(stmt)
    existing_rate = result.scalar_one_or_none()

    if existing_rate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rate not found")

    delete_stmt = delete(Rate).where(Rate.id == rate_id)
    await db.execute(delete_stmt)
    await db.commit()

