import pickle

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
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.models.models import User, Role
from src.schemas.vehicles import (
    BlacklistSchema,
    BlacklistResposeSchema,
    BLResposeSchema,
    BlacklistedVehicleResponse,
    Reminder,
    VehicleSchema,
    VehicleUpdateSchema,
    VehicleResponse,
)
from src.services.auth import auth_service
from src.conf import messages
from src.conf.config import config
from src.services.roles import RoleAccess
from src.repository import vehicles as repositories_vehicles
from src.services.email import send_email_by_license_plate

router = APIRouter(prefix="/vehicles", tags=["vehicles"])

access_to_route_all = RoleAccess([Role.admin])


@router.get(
    "/blacklist",
    response_model=list[BLResposeSchema],
    dependencies=[Depends(access_to_route_all)],
)
async def get_all_black_list(
    limit: int = Query(10, ge=10, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):

    if user.role != Role.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=messages.USER_NOT_HAVE_PERMISSIONS,
        )

    black_list = await repositories_vehicles.get_all_black_list(limit, offset, db)
    # black_list = await repositories_vehicles.get_blacklisted_vehicles(limit, offset, db)

    return black_list

@router.get(
    "/all_abonement",
    response_model=list[VehicleResponse],
    dependencies=[Depends(access_to_route_all)],
)
async def get_all_vehicles_on_abonement(
    limit: int = Query(10, ge=10, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    # if user.role != Role.admin:
    #     print(user.role)
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail=messages.USER_NOT_HAVE_PERMISSIONS,
    #     )
    vehicles = await repositories_vehicles.get_vehicles_abonement(limit, offset, db)
    return vehicles

@router.get(
    "/reminder",
    response_model=list[VehicleResponse],
    dependencies=[Depends(access_to_route_all)],
)
async def get_all_vehicles_reminder(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):

    vehicles = await repositories_vehicles.get_all_vehicles_reminder(db)
    return vehicles

@router.get(
    "/blacklist/owners",
    response_model=list[BlacklistedVehicleResponse],
    dependencies=[Depends(access_to_route_all)],
)
async def get_black_list_only_owners(
    limit: int = Query(10, ge=10, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):

    if user.role != Role.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=messages.USER_NOT_HAVE_PERMISSIONS,
        )

    # black_list = await repositories_vehicles.get_all_black_list(limit, offset, db)
    black_list = await repositories_vehicles.get_blacklisted_vehicles(limit, offset, db)

    return black_list


@router.post(
    "/blacklist",
    # response_model=BlacklistResposeSchema,
    status_code=status.HTTP_201_CREATED,
)
async def add_to_black_list(
    body: BlacklistSchema,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    """
    The add_to_black_list function creates a new vehicle in the black_list.
    It takes a UserSchema object as input, and returns the newly created user.
    If an account with that email already exists, it raises an HTTPException.

    :param body: BlacklistSchema: Validate the request body
    :param request: Request: Get the base url of the request
    :param db: AsyncSession: Pass the database session to the function
    :return: message '{license_plate} move to black list'
    :doc-author: Trelent
    """
    if user.role != Role.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=messages.USER_NOT_HAVE_PERMISSIONS,
        )
    exist_vehicle_in_black_list = await repositories_vehicles.get_vehicle_in_black_list(
        body.license_plate, db
    )
    if exist_vehicle_in_black_list:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=messages.VEHICLE_ALREADY_BLACK_LIST,
        )
    exist_vehicle = await repositories_vehicles.get_vehicle_by_plate(
        body.license_plate, db
    )
    if not exist_vehicle:
        return f"{body.license_plate} не зареєтрована в системі!"
        # exist_vehicle = await repositories_vehicles.add_to_black_list_new_vehicle(body, user, db)

    vehicle_bl = await repositories_vehicles.add_to_black_list(
        body, exist_vehicle, user, db
    )
    return vehicle_bl


@router.patch(
    "/{license_plate}/blacklist",
    response_model=BlacklistResposeSchema,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def update_black_list(
    body: BlacklistSchema,
    license_plate: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):

    if user.role != Role.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=messages.USER_NOT_HAVE_PERMISSIONS,
        )
    try:
        vehicle = await repositories_vehicles.update_vehicle_in_blacklist(
            body, license_plate, db, user
        )
        if vehicle is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=messages.VEHICLE_NOT_FOUND
            )
    except:
        raise HTTPException(status_code=409, detail=messages.LICENSE_PLATE_NOT_UNIQUE)
    return vehicle


@router.get("/{license_plate}/blacklist", response_model=BlacklistedVehicleResponse)
async def get_license_plate_blacklist_info(
    license_plate: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):

    if user.role != Role.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=messages.USER_NOT_HAVE_PERMISSIONS,
        )
    exist_vehicle_in_black_list = await repositories_vehicles.get_vehicle_in_blacklist(
        license_plate, db
    )
    if exist_vehicle_in_black_list is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.VEHICLE_NOT_FOUND
        )
    return exist_vehicle_in_black_list


@router.post("/{license_plate}/email")
async def email_license_plate(
    license_plate: str,
    body: Reminder,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    if user.role != Role.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=messages.USER_NOT_HAVE_PERMISSIONS,
        )
    vehicle = await repositories_vehicles.get_vehicle_by_plate(license_plate, db)
    if vehicle is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.VEHICLE_NOT_FOUND
        )
    user_vehicle = await repositories_vehicles.get_user_by_license_plate(
        license_plate, db
    )
    if user_vehicle is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=messages.VEHICLE_USER_NOT_FOUND,
        )
    try:
        background_tasks.add_task(
            send_email_by_license_plate,
            user_vehicle.email,
            user_vehicle.name,
            license_plate,
            body.days,
        )
        return f"E-mail was sent to owner vehicle {license_plate} - {user_vehicle.name}"
    except Exception as e:
        raise HTTPException(detail=f"Failed to send email: {e}")


# A little changes
@router.post(
    "/{username}",
    status_code=status.HTTP_201_CREATED,
)
async def add_vehicle_to_database(
    username: str,
    body: VehicleSchema,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    if user.role != Role.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=messages.USER_NOT_HAVE_PERMISSIONS,
        )

    user_id = await repositories_vehicles.find_user_id_by_username(username, db)

    exist_vehicle = await repositories_vehicles.get_vehicle_by_plate(
        body.license_plate, db
    )
    if exist_vehicle:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=messages.LICENSE_PLATE_NOT_UNIQUE,
        )

    vehicle_new = await repositories_vehicles.add_to_DB(
        body.license_plate, body.rate_id, user_id, db
    )
    return vehicle_new


@router.get("/{license_plate}", response_model=VehicleSchema)
async def get_license_plate_info(
    license_plate: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):

    if user.role != Role.admin or user.role != Role.user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=messages.USER_NOT_HAVE_PERMISSIONS,
        )
    exist_vehicle = await repositories_vehicles.get_vehicle_by_plate(license_plate, db)
    if exist_vehicle is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.VEHICLE_NOT_FOUND
        )
    return exist_vehicle


@router.patch(
    "/{license_plate}",
    response_model=VehicleSchema,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def update_car_info(
    license_plate: str,
    body: VehicleUpdateSchema,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    if user.role != Role.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=messages.USER_NOT_HAVE_PERMISSIONS,
        )
    try:

        vehicle = await repositories_vehicles.update_vehicle(
            license_plate, body, db, user
        )
        if vehicle is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=messages.VEHICLE_NOT_FOUND
            )
    except Exception as e:
        raise HTTPException(status_code=409, detail=messages.LICENSE_PLATE_NOT_UNIQUE)
    return vehicle

@router.get(
    "/",
    response_model=list[VehicleResponse],
    dependencies=[Depends(access_to_route_all)],
)
async def get_all_vehicles(
    limit: int = Query(10, ge=10, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):

    vehicles = await repositories_vehicles.get_all_vehicles(limit, offset, db)
    return vehicles