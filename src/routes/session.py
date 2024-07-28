import re
from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, APIRouter, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.repository import session as session_repo
from src.repository import vehicles as repositories_vehicles
from src.schemas.session import SessionCreate, SessionClose
from src.services.roles import RoleAccess
from src.models.models import Role, User
from src.services.auth import auth_service
from src.database.db import get_db

# from DS.main.use_model import processing
router = APIRouter(prefix="/session", tags=["session"])
access_to_route_all = RoleAccess([Role.admin])

LICENSE_PLATE_REGEX = re.compile(r"^[A-Za-zА-Яа-я]{2}\d{4}[A-Za-zА-Яа-я]{2}$")


@router.post("/in", dependencies=[Depends(access_to_route_all)])
async def in_session(image: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    image_bytes = await image.read()
    if not session_repo.verify_image(image_bytes):
        raise HTTPException(status_code=400, detail="Image verification failed")

    # Розпізнавання номера
    # number = processing(image_bytes)   Функція розпізнавання, у мене не працює TensorFlow, не можу перевірити
    number = "FH1234HN"

    session = await session_repo.create_session(SessionCreate(number=number), db)
    return {"session_id": session.id}


# @router.post("/manual_in", dependencies=[Depends(access_to_route_all)])
# async def manual_in_session(number: str, db: AsyncSession = Depends(get_db)):
#     session = await session_repo.create_session(SessionCreate(number=number), db)
#     return {"session_id": session.id}


#  Manual_in
@router.post("/manual_in")
async def manual_in(
    license_plate: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    if not LICENSE_PLATE_REGEX.match(license_plate):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid license plate format. Must be 2 letters, 4 digits, 2 letters.",
        )

    blacklist_entry = await session_repo.find_vehicle_in_blacklist(license_plate, db)
    if blacklist_entry:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vehicle is in the blacklist.",
        )

    vehicle = await session_repo.find_vehicle_by_license_plate(license_plate, db)
    if not vehicle:
        hourly_rate = await session_repo.find_hourly_rate_id(db)
        if not hourly_rate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hourly rate not found.",
            )

        vehicle = await repositories_vehicles.add_to_DB(
            license_plate=license_plate, rate_id=hourly_rate, user_id=None, db=db
        )

    open_session = await session_repo.find_open_session_by_vehicle_id(vehicle.id, db)
    if open_session:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Open parking session already exists for this vehicle.",
        )

    new_session = await session_repo.create_parking_session(vehicle.id, db)

    return {"session_id": new_session.id}


@router.post("/out", dependencies=[Depends(access_to_route_all)])
async def out_session(
    image: UploadFile = File(...), db: AsyncSession = Depends(get_db)
):
    image_bytes = await image.read()
    if not session_repo.verify_image(image_bytes):
        raise HTTPException(status_code=400, detail="Image verification failed")

    # Розпізнавання номера
    # number = processing(image_bytes) , Функція розпізнавання, у мене не працює TensorFlow, не можу перевірити
    number = "FH1234HN"

    session = await session_repo.close_session(SessionClose(number=number), db)
    return {"session_id": session.id}


@router.post("/manual_out", dependencies=[Depends(access_to_route_all)])
async def manual_out_session(number: str, db: AsyncSession = Depends(get_db)):
    session = await session_repo.close_session(SessionClose(number=number), db)
    return {"session_id": session.id}
