import re
from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, APIRouter, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.repository import session
from src.schemas.session import SessionCreate, SessionClose
from src.services.roles import RoleAccess
from src.models.models import Role, User
from src.database.db import get_db
from src.services.use_model import processing

from src.repository import vehicles as repositories_vehicles
from src.services.auth import auth_service

router = APIRouter(prefix="/session", tags=["session"])
access_to_route_all = RoleAccess([Role.admin, Role.operator])

LICENSE_PLATE_REGEX = re.compile(r"^[A-Za-zА-Яа-я]{2}\d{4}[A-Za-zА-Яа-я]{2}$")


@router.post("/in", dependencies=[Depends(access_to_route_all)])
async def in_session(image: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    image_bytes = await image.read()

    number, recognize = processing(image_bytes, echo=False, log_on=False)
    if not recognize:
        raise HTTPException(
            status_code=406, detail=f"Image verification failed - {number}"
        )

    result = await session.create_session(number, db)
    return {"session_id": result.id, "plate_number": number}


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

    blacklist_entry = await session.find_vehicle_in_blacklist(license_plate, db)
    if blacklist_entry:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vehicle is in the blacklist.",
        )

    vehicle = await session.find_vehicle_by_license_plate(license_plate, db)
    if not vehicle:
        hourly_rate = await session.find_hourly_rate_id(db)
        if not hourly_rate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hourly rate not found.",
            )

        vehicle = await repositories_vehicles.add_to_DB(
            license_plate=license_plate, rate_id=hourly_rate, user_id=None, db=db
        )

    open_session = await session.find_open_session_by_vehicle_id(vehicle.id, db)
    if open_session:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Open parking session already exists for this vehicle.",
        )

    new_session = await session.create_parking_session(vehicle.id, db)

    return {"session_id": new_session.id}


@router.post("/out", dependencies=[Depends(access_to_route_all)])
async def out_session(
    image: UploadFile = File(...), db: AsyncSession = Depends(get_db)
):
    image_bytes = await image.read()
    number, recognize = processing(image_bytes, echo=False, log_on=False)
    if not recognize:
        raise HTTPException(
            status_code=406, detail=f"Image verification failed - {number}"
        )

    result = await session.close_session(number, db)
    return {"session_id": result.id, "plate_number": number}


@router.post("/manual_out")
async def manual_out(
    license_plate: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    if not LICENSE_PLATE_REGEX.match(license_plate):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid license plate format. Must be 2 letters, 4 digits, 2 letters.",
        )

    blacklist_entry = await session.find_vehicle_in_blacklist(license_plate, db)
    if blacklist_entry:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vehicle is in the blacklist.",
        )

    vehicle = await session.find_vehicle_by_license_plate(license_plate, db)
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found.",
        )

    open_session = await session.find_open_session_by_vehicle_id(vehicle.id, db)
    if not open_session:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No open parking session found for this vehicle.",
        )

    closed_session = await session.close_parking_session(open_session.id, db)

    return {"session_id": closed_session.id}
