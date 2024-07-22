# import uuid

from fastapi import Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar

from src.conf import messages
from src.database.db import get_db
from src.models.models import Role, User, Vehicle, Blacklist
from src.schemas.vehicles import BlacklistSchema
from src.schemas.user import UserSchema, UserUpdateSchema


async def get_vehicle_by_plate(license_plate: str, db: AsyncSession = Depends(get_db)):
    """
    The get_user_by_email function takes an email address and returns the user object associated with that email.
    If no such user exists, it returns None.

    :param email: str: Specify the email of the user we want to retrieve
    :param db: AsyncSession: Pass the database session to the function
    :return: A user object
    :doc-author: Trelent
    """

    stmt = select(Vehicle).filter_by(license_plate=license_plate)
    vehicle = await db.execute(stmt)
    vehicle = vehicle.scalar_one_or_none()
    if vehicle:
        return vehicle
    else:
        return None

async def get_vehicle_in_black_list(license_plate: str, db: AsyncSession):
    vehicle = await get_vehicle_by_plate(license_plate, db)
    if vehicle:
        stmt = select(Blacklist).filter_by(vehicle_id=vehicle.id)
        vehicle_bl = await db.execute(stmt)
        vehicle_bl = vehicle_bl.scalar_one_or_none()
        return vehicle_bl
    else:
        return None

async def add_to_black_list(body: BlacklistSchema, vehicle: Vehicle, user: User,
                            db: AsyncSession = Depends(get_db)):
    """
    The create_user function creates a new user in the database.

    :param body: UserSchema: Validate the request body
    :param db: AsyncSession: Get the database session
    :return: A user object, which is a sqlalchemy model
    :doc-author: Trelent
    """
    license_plate = Blacklist(user_id = user.id, vehicle_id = vehicle.id, reason = body.reason)
    db.add(license_plate)
    await db.commit()
    await db.refresh(license_plate)
    return f'{body.license_plate} move to black list'

async def add_to_black_list_new_vehicle(body: BlacklistSchema, user: User, db: AsyncSession = Depends(get_db)):
    """
    The create_user function creates a new user in the database.

    :param body: UserSchema: Validate the request body
    :param db: AsyncSession: Get the database session
    :return: A user object, which is a sqlalchemy model
    :doc-author: Trelent
    """
    
    license_plate = Vehicle(
        license_plate = body.license_plate,
        rate_id = 1
        )
   
    db.add(license_plate)
    await db.commit()
    await db.refresh(license_plate)
    stmt = select(Vehicle).filter_by(license_plate=body.license_plate)
    vehicle = await db.execute(stmt)
    vehicle = vehicle.scalar_one_or_none()

    return vehicle


async def get_all_black_list(limit: int, offset: int, db: AsyncSession):
    """
    The get_all_black_list function returns a list of all vehicles in the black_list.

    :param limit: int: Limit the number of contacts returned
    :param offset: int: Specify the offset of the first row to return
    :param db: AsyncSession: Pass in the database session to use
    :return: A list of vehicles in black list
    """
    stmt = select(Blacklist).offset(offset).limit(limit)
    # stmt = select(Blacklist).select_from(Vehicle).filter_by(id=Blacklist.vehicle_id).offset(offset).limit(limit)
    black_list = await db.execute(stmt)
    return black_list.scalars().all()


async def update_vehicle_in_blacklist(body: BlacklistSchema, license_plate: str, db: AsyncSession, current_user: User):
    vehicle = await get_vehicle_by_plate(license_plate, db)
    vehicle_new = None
    if body.license_plate != license_plate:
        vehicle_new = await get_vehicle_by_plate(body.license_plate, db)
        if not vehicle_new:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.UPDATED_LICENSE_PLACE_NOT_FOUND)
    if vehicle:
        stmt = select(Blacklist).filter_by(vehicle_id=vehicle.id)
        vehicle_bl = await db.execute(stmt)
        vehicle_bl = vehicle_bl.scalar_one_or_none()
        print(vehicle_bl.reason)
        vehicle_bl.user_id = current_user.id
        if vehicle_new:
            vehicle_bl.vehicle_id = vehicle_new.id
         
        vehicle_bl.reason = body.reason
        vehicle_bl.updated_at = func.now()
        print(vehicle_bl.reason)
        await db.commit()
        print(vehicle_bl.user_id)  
        await db.refresh(vehicle_bl)
        return vehicle_bl