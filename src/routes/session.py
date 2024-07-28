from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from src.repository import session
from src.schemas.session import SessionCreate, SessionClose
from src.services.roles import RoleAccess
from src.models.models import Role
from src.database.db import get_db
from src.services.use_model import processing

router = APIRouter(prefix="/session", tags=["session"])
access_to_route_all = RoleAccess([Role.admin, Role.operator])


@router.post("/in", dependencies=[Depends(access_to_route_all)])
async def in_session(image: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    image_bytes = await image.read()

    number, recognize = processing(image_bytes, echo=False, log_on=False)
    if not recognize:
        raise HTTPException(status_code=406, detail="Image verification failed")

    result = await session.create_session(number, db)
    return {"session_id": result.id, "plate_number": number}

@router.post("/manual_in", dependencies=[Depends(access_to_route_all)])
async def manual_in_session(number: str, db: AsyncSession = Depends(get_db)):
    session = await session.create_session(SessionCreate(number=number), db)
    return {"session_id": session.id}


@router.post("/out", dependencies=[Depends(access_to_route_all)])
async def out_session(image: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    image_bytes = await image.read()
    number, recognize = processing(image_bytes, echo=False, log_on=False)
    if not recognize:
        raise HTTPException(status_code=406, detail="Image verification failed")
    
    result = await session.close_session(number, db)
    return {"session_id": result.id, "plate_number": number}


@router.post("/manual_out", dependencies=[Depends(access_to_route_all)])
async def manual_out_session(number: str, db: AsyncSession = Depends(get_db)):
    result = await session.close_session(SessionClose(number=number), db)
    return {"session_id": result.id}
