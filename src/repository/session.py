from datetime import datetime

from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status

from src.repository.vehicles import get_vehicle_in_black_list, get_vehicle_by_plate, add_vehicle_to_db_auto
from src.models.models import Parking_session
from src.conf import messages
from src.schemas.session import SessionCreate, SessionClose
# <<<<<<< oleksandr


async def create_session(license_plate, db: AsyncSession):
    vehicle = await get_vehicle_in_black_list(license_plate, db)
    if vehicle:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Entrance closed. Auto in black list')
    vehicle = await get_vehicle_by_plate(license_plate, db)
    if not vehicle:
        vehicle = await add_vehicle_to_db_auto(license_plate, db)
    stmt = Parking_session(   
        vehicle_id=vehicle.id,
# =======
# import uuid
# from datetime import datetime
# from fastapi import HTTPException
# from sqlalchemy.ext.asyncio import AsyncSession
# from src.models.models import Vehicle, Parking_session, Blacklist, Rate


# async def create_session(
#     session_data: SessionCreate, db: AsyncSession
# ) -> DbSessionModel:
#     session = DbSessionModel(
#         license_plate=session_data.number, rate_id=1, created_at=datetime.now()
# >>>>>>> dev
    )
    db.add(stmt)
    await db.commit()
    await db.refresh(stmt)
    return stmt


# <<<<<<< oleksandr
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
    
# =======
# async def close_session(session_data: SessionClose, db: AsyncSession) -> DbSessionModel:
#     query = select(DbSessionModel).where(
#         DbSessionModel.license_plate == session_data.number,
#         DbSessionModel.updated_at.is_(None),
#     )
#     result = await db.execute(query)
#     session = result.scalars().first()

#     if not session:
#         raise HTTPException(
#             status_code=404, detail="Session not found or already closed"
#         )

# >>>>>>> dev
    session.updated_at = datetime.now()
    await db.commit()
    await db.refresh(session)
    return session


def verify_image(image: bytes) -> bool:
    # Тут буде логіка перевірки зображення
    # Повертає True, якщо зображення пройшло перевірку, інакше False
    return True


# |Function for manual_in
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
