from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.models.models import Parking_session as DbSessionModel
from src.schemas.session import SessionCreate, SessionClose
import uuid
from datetime import datetime
from fastapi import HTTPException
from src.models.models import Vehicle

async def create_session(session_data: SessionCreate, db: AsyncSession) -> DbSessionModel:
    vehicle_query = select(Vehicle).where(Vehicle.license_plate == session_data.number)
    vehicle_result = await db.execute(vehicle_query)
    vehicle = vehicle_result.scalars().first()
    
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    total_cost = 0  
    empty_place = 0  

    session = DbSessionModel(
        vehicle_id=vehicle.id,
        total_cost=total_cost,
        empty_place=empty_place,
        created_at=datetime.now()
    )
    
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


async def close_session(session_data: SessionClose, db: AsyncSession) -> DbSessionModel:
    query = select(DbSessionModel).where(Vehicle.license_plate == session_data.number, DbSessionModel.updated_at.is_(None))
    result = await db.execute(query)
    session = result.scalars().first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or already closed")
    
    session.updated_at = datetime.now()
    await db.commit()
    await db.refresh(session)
    return session