from datetime import datetime

from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status

from src.repository.vehicles import get_vehicle_in_black_list, get_vehicle_by_plate, add_vehicle_to_db_auto
from src.models.models import Parking_session
from src.conf import messages
from src.schemas.session import SessionCreate, SessionClose


async def create_session(license_plate, db: AsyncSession):
    vehicle = await get_vehicle_in_black_list(license_plate, db)
    if vehicle:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Entrance closed. Auto in black list')
    vehicle = await get_vehicle_by_plate(license_plate, db)
    if not vehicle:
        vehicle = await add_vehicle_to_db_auto(license_plate, db)
    stmt = Parking_session(   
        vehicle_id=vehicle.id,
    )
    db.add(stmt)
    await db.commit()
    await db.refresh(stmt)
    return stmt


async def close_session(license_plate: str, db: AsyncSession):
    vehicle = await get_vehicle_in_black_list(license_plate, db)
    if vehicle:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Exit closed. Auto in black list')
    vehicle = await get_vehicle_by_plate(license_plate, db)
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.VEHICLE_NOT_FOUND)
    stmt = select(Parking_session).where(and_(Parking_session.vehicle_id == vehicle.id, Parking_session.updated_at == None))
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found or already closed")
    
    session.updated_at = datetime.now()
    await db.commit()
    await db.refresh(session)
    return session


def verify_image(image: bytes) -> bool:
    # Тут буде логіка перевірки зображення
    # Повертає True, якщо зображення пройшло перевірку, інакше False
    return True
