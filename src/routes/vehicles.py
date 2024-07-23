import pickle

from fastapi import APIRouter, HTTPException, Depends, Query, status, UploadFile, File, Path, BackgroundTasks, Request
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.models.models import User, Role
from src.schemas.user import UserChangeRoleResponse, UserChangeRole, UserResponse, AboutUser, UserUpdateSchema
from src.schemas.vehicles import BlacklistResposeSchema, BlacklistSchema, BLResposeSchema
from src.services.auth import auth_service
from src.conf import messages
from src.conf.config import config
from src.services.roles import RoleAccess
from src.repository import vehicles as repositories_vehicles
from src.services.email import send_email

router = APIRouter(prefix="/vehicles", tags=["vehicles"])

access_to_route_all = RoleAccess([Role.admin])


@router.get(
    "/blacklist", response_model=list[BlacklistResposeSchema], dependencies=[Depends(access_to_route_all)]
)
async def get_all_black_list(
    limit: int = Query(10, ge=10, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
   
    """
    The get_all_users function returns a list of all users in the database.
        The limit and offset parameters are used to paginate the results.
    
    :param limit: int: Limit the number of users returned
    :param ge: Set a minimum value for the limit parameter
    :param le: Set the maximum value of the limit parameter
    :param offset: int: Specify the number of records to skip
    :param db: AsyncSession: Pass the database connection to the function
    :param user: User: Get the current user
    :return: A list of users
    :doc-author: Trelent
    """
    if  user.role != Role.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=messages.USER_NOT_HAVE_PERMISSIONS)
    
    black_list = await repositories_vehicles.get_all_black_list(limit, offset, db)
    return black_list

@router.post(
    "/blacklist", 
    # response_model=BlacklistResposeSchema, 
    status_code=status.HTTP_201_CREATED
)
async def add_to_black_list(
    body: BlacklistSchema,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user)
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
    if  user.role != Role.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=messages.USER_NOT_HAVE_PERMISSIONS)
    exist_vehicle_in_black_list = await repositories_vehicles.get_vehicle_in_black_list(body.license_plate, db)
    if exist_vehicle_in_black_list:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=messages.VEHICLE_ALREADY_BLACK_LIST
        )
    exist_vehicle = await repositories_vehicles.get_vehicle_by_plate(body.license_plate, db)
    if not exist_vehicle:
        return f'{body.license_plate} не зареєтрована в системі!'
        # exist_vehicle = await repositories_vehicles.add_to_black_list_new_vehicle(body, user, db)
    
    vehicle_bl = await repositories_vehicles.add_to_black_list(body, exist_vehicle, user, db)
    return vehicle_bl


# router.post('/{license_plate})
    # background_tasks.add_task(  
    #     send_email, new_user.email, new_user.username, str(request.base_url)
    # )

@router.patch("/{license_plate}/blacklist", response_model=BlacklistResposeSchema,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def update_black_list(body: BlacklistSchema, license_plate: str, db: AsyncSession = Depends(get_db),
                    user: User = Depends(auth_service.get_current_user)):
    """
    The update_user function updates a user in the database.
        Args:
            body (UserUpdateSchema): The updated user object.
            db (AsyncSession): An async session for interacting with the database.
        Returns:
            User: A User object representing an updated version of the original 
    
    
    :param body: UserUpdateSchema: Validate the request body
    :param db: AsyncSession: Get the database connection,
    :param user: User: Get the current user from the cache
    :return: The user object
    :doc-author: Trelent
    """
    if  user.role != Role.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=messages.USER_NOT_HAVE_PERMISSIONS)
    # try:
    vehicle = await repositories_vehicles.update_vehicle_in_blacklist(body, license_plate, db, user)
    if vehicle is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.VEHICLE_NOT_FOUND)
    # except:
        # raise HTTPException(status_code=409, detail=messages.LICENSE_PLATE_NOT_UNIQUE)
    return vehicle


@router.get("/{license_plate}/blacklist", response_model=BLResposeSchema)
async def get_license_plate_blacklist_info(
    license_plate: str,
    db: AsyncSession = Depends(get_db),
    # user: User = Depends(auth_service.get_current_user),
):

    """
    The get_username_info function returns the user's information and number of photos.
        Args:
            username (str): The username of the user whose info is being requested.
            db (AsyncSession): An async session for interacting with a database. Defaults to Depends(get_db).
            user (User): A User object representing the current logged in user, defaults to Depends(auth_service.get_current_user)
    
    :param username: str: Get the username from the url path
    :param db: AsyncSession: Pass the database session to the repository function
    :param user: User: Get the current user
    :return: A user object
    :doc-author: Trelent
    """

    exist_vehicle_in_black_list = await repositories_vehicles.get_vehicle_in_black_list(license_plate, db)
    if exist_vehicle_in_black_list is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.VEHICLE_NOT_FOUND)
    exist_vehicle_in_black_list.license_plate = license_plate
    return exist_vehicle_in_black_list
