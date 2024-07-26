from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Session as DbSession
from src.models.models import Vehicle as DbSessionModel
from src.schemas.session import SessionCreate, SessionClose
import uuid
from datetime import datetime
from fastapi import HTTPException

async def create_session(session_data: SessionCreate, db: AsyncSession) -> DbSessionModel:
    session = DbSessionModel(   
        license_plate=session_data.number,
        rate_id = 1,
        created_at=datetime.now()
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


async def close_session(session_data: SessionClose, db: AsyncSession) -> DbSessionModel:
    query = select(DbSessionModel).where(DbSessionModel.license_plate == session_data.number, DbSessionModel.updated_at.is_(None))
    result = await db.execute(query)
    session = result.scalars().first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or already closed")
    
    session.updated_at = datetime.now()
    await db.commit()
    await db.refresh(session)
    return session


def verify_image(image: bytes) -> bool:
    # Тут буде логіка перевірки зображення
    # Повертає True, якщо зображення пройшло перевірку, інакше False
    return True
