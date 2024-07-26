from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from src.repository import session as session_repo
from src.schemas.session import SessionCreate, SessionClose
from src.services.roles import RoleAccess
from src.models.models import Role
from src.database.db import get_db  
#from DS.main.use_model import processing
router = APIRouter(prefix="/session", tags=["session"])
access_to_route_all = RoleAccess([Role.admin])


@router.post("/in", dependencies=[Depends(access_to_route_all)])
async def in_session(image: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    image_bytes = await image.read()
    if not session_repo.verify_image(image_bytes):
        raise HTTPException(status_code=400, detail="Image verification failed")
    
    # Розпізнавання номера
    #number = processing(image_bytes)   Функція розпізнавання, у мене не працює TensorFlow, не можу перевірити
    number = 'FH1234HN'

    session = await session_repo.create_session(SessionCreate(number=number), db)
    return {"session_id": session.id}


@router.post("/manual_in", dependencies=[Depends(access_to_route_all)])
async def manual_in_session(number: str, db: AsyncSession = Depends(get_db)):
    session = await session_repo.create_session(SessionCreate(number=number), db)
    return {"session_id": session.id}


@router.post("/out", dependencies=[Depends(access_to_route_all)])
async def out_session(image: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    image_bytes = await image.read()
    if not session_repo.verify_image(image_bytes):
        raise HTTPException(status_code=400, detail="Image verification failed")
    
    # Розпізнавання номера
    # number = processing(image_bytes) , Функція розпізнавання, у мене не працює TensorFlow, не можу перевірити
    number = 'FH1234HN'
    
    session = await session_repo.close_session(SessionClose(number=number), db)
    return {"session_id": session.id}


@router.post("/manual_out", dependencies=[Depends(access_to_route_all)])
async def manual_out_session(number: str, db: AsyncSession = Depends(get_db)):
    session = await session_repo.close_session(SessionClose(number=number), db)
    return {"session_id": session.id}
