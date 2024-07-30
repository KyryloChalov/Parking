import os
from datetime import datetime
from starlette.responses import FileResponse
from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    Query,
    status,
    UploadFile,
    File,
    Path,
    BackgroundTasks,
    Request,
)
from sqlalchemy.ext.asyncio import AsyncSession
import pandas as pd


from sqlalchemy import select
from src.models.models import Parking_session, Payment, Vehicle, User

from src.database.db import get_db
from src.models.models import User, Role

from src.repository.utilities import get_parking_data

from src.schemas.vehicles import Reminder, VehicleResponse, Info

from src.services.auth import auth_service
from src.conf import messages
from src.conf.config import config
from src.services.roles import RoleAccess
from src.repository import vehicles as repositories_vehicles

from src.services.email import send_email_by_license_plate, send_email_info


router = APIRouter(prefix="/utilities", tags=["utilities"])

access_to_route_all = RoleAccess([Role.admin])


@router.post("/email_reminder")  # , response_model=list[VehicleResponse])
async def email_reminder(
    # body: Reminder,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    if user.role != Role.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=messages.USER_NOT_HAVE_PERMISSIONS,
        )
    vehicles = await repositories_vehicles.get_all_vehicles_reminder(db)
    if vehicles is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.VEHICLE_NOT_FOUND
        )

    try:
        for v in vehicles:
            days_reminder = v.ended_at - datetime.now().date()
            user_vehicle = await repositories_vehicles.get_user_by_license_plate(
                v.license_plate, db
            )
            background_tasks.add_task(
                send_email_by_license_plate,
                user_vehicle.email,
                user_vehicle.name,
                v.license_plate,
                days_reminder.days,
            )
        return f"E-mails was sent to owner of vehicles"
    except Exception as e:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Failed to send email: {e}"
        )


@router.post("/email_info")
async def email_info(
    body: Info,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    if user.role != Role.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=messages.USER_NOT_HAVE_PERMISSIONS,
        )
    vehicles = await repositories_vehicles.get_vehicles_not_in_black_list(db)
    if vehicles is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.VEHICLE_NOT_FOUND
        )

    try:
        for v in vehicles:
            user_vehicle = await repositories_vehicles.get_user_by_license_plate(
                v.license_plate, db
            )
            # print(user_vehicle)
            background_tasks.add_task(
                send_email_info,
                user_vehicle.email,
                user_vehicle.name,
                body.subject,
                body.info,
            )
        return f"E-mails was sent to owner of vehicles"
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Failed to send email: {e}"
        )


@router.post("/parking_place_abonement")
async def parking_place_abonement(
    db: AsyncSession = Depends(get_db),
):
    num_vehicles_abonement_ = await repositories_vehicles.get_num_vehicles_with_abonement(db)
    return f"{num_vehicles_abonement_}"


@router.post("/free_parking_places")
async def free_parking_places(
    db: AsyncSession = Depends(get_db),
):
    num_free = await repositories_vehicles.free_parking_space(db)
    return f"Кількість вільних паркомісць {num_free}"


# @router.get("/export", response_class=FileResponse)
# async def export_parking_data(
#     start_date: datetime = Query(
#         ..., description="Start date for the export (YYYY-MM-DD)"
#     ),
#     end_date: datetime = Query(..., description="End date for the export (YYYY-MM-DD)"),
#     db: AsyncSession = Depends(get_db),
# ):
#     data = await get_parking_data(start_date, end_date, db)
#     print(f"{data = }")

#     df = pd.DataFrame(data)
#     print(f"1. {df = }")
#     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#     export_dir = "exports"

#     # Проверка наличия папки и создание её, если она не существует
#     if not os.path.exists(export_dir):
#         os.makedirs(export_dir)

#     csv_file = os.path.join(export_dir, f"parking_data_{timestamp}.csv")
#     df.to_csv(csv_file, index=False)
#     print(f"2. {df = }")

#     return FileResponse(path=csv_file, filename=csv_file, media_type="text/csv")


@router.get("/export", response_class=FileResponse)
async def export_parking_data(
    start_date: datetime = Query(
        ..., description="Start date for the export (YYYY-MM-DD)"
    ),
    end_date: datetime = Query(..., description="End date for the export (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    if user.role != Role.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=messages.USER_NOT_HAVE_PERMISSIONS,
        )
    query = (
        select(
            Parking_session.id,
            Vehicle.license_plate,
            # User.username,
            Parking_session.created_at,
            Parking_session.updated_at,
            Payment.amount,
            Payment.created_at,
        )
        .join(Vehicle, Parking_session.vehicle_id == Vehicle.id)
        # .join(User, Vehicle.owner_id == User.id)
        .join(Payment, Payment.session_id == Parking_session.id)
        # .where(Payment.created_at >= start_date)
        # .where(Payment.created_at <= end_date)
    )
    result = await db.execute(query)
    data = result.all()
    # data = await get_parking_data(start_date, end_date, db)
    df = pd.DataFrame(data)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    export_dir = "exports"
    # Проверка наличия папки и создание её, если она не существует
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)
    csv_file = os.path.join(export_dir, f"parking_data_{timestamp}.csv")
    df.to_csv(csv_file, index=False)
    return FileResponse(path=csv_file, filename=csv_file, media_type="text/csv")


# @router.get("/export", response_class=FileResponse)
# async def get_parking_data(start_date: datetime, end_date: datetime, db: AsyncSession):
#     print(start_date)
#     query = (
#         select(
#             Parking_session.id,
#             Vehicle.license_plate,
#             # User.username,
#             Parking_session.created_at,
#             Parking_session.updated_at,
#             Payment.amount,
#             Payment.created_at,
#         ).join(Vehicle, Parking_session.vehicle_id == Vehicle.id)
#         # .join(User, Vehicle.owner_id == User.id)
#         .join(Payment, Payment.session_id == Parking_session.id)
#         # .where(Payment.created_at >= start_date)
#         # .where(Payment.created_at <= end_date)
#     )
#     result = await db.execute(query)
#     records = result.all()
#     return records
