from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Session as DbSession
from src.models.models import Vehicle as DbSessionModel
from src.schemas.session import SessionCreate, SessionClose
import uuid
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.models import Vehicle, Parking_session, Blacklist, Rate


async def create_session(
    session_data: SessionCreate, db: AsyncSession
) -> DbSessionModel:
    session = DbSessionModel(
        license_plate=session_data.number, rate_id=1, created_at=datetime.now()
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


async def close_session(session_data: SessionClose, db: AsyncSession) -> DbSessionModel:
    query = select(DbSessionModel).where(
        DbSessionModel.license_plate == session_data.number,
        DbSessionModel.updated_at.is_(None),
    )
    result = await db.execute(query)
    session = result.scalars().first()

    if not session:
        raise HTTPException(
            status_code=404, detail="Session not found or already closed"
        )

    session.updated_at = datetime.now()
    await db.commit()
    await db.refresh(session)
    return session


def verify_image(image: bytes) -> bool:
    # Тут буде логіка перевірки зображення
    # Повертає True, якщо зображення пройшло перевірку, інакше False
    return True


async def find_vehicle_in_blacklist(license_plate: str, db: AsyncSession):
    query = (
        select(Blacklist).join(Vehicle).filter(Vehicle.license_plate == license_plate)
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def find_vehicle_by_license_plate(license_plate: str, db: AsyncSession):
    query = select(Vehicle).filter_by(license_plate=license_plate)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def find_hourly_rate_id(db: AsyncSession):
    query = select(Rate.id).filter_by(rate_name="hourly")
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def find_open_session_by_vehicle_id(vehicle_id: int, db: AsyncSession):
    query = select(Parking_session).filter_by(vehicle_id=vehicle_id, updated_at=None)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def create_parking_session(vehicle_id: int, db: AsyncSession):
    new_session = Parking_session(vehicle_id=vehicle_id)
    db.add(new_session)
    await db.commit()
    await db.refresh(new_session)
    return new_session
