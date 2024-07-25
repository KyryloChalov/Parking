from fastapi import Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload, aliased
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf import messages
from src.database.db import get_db
from src.models.models import Role, User, Vehicle, Blacklist
from src.schemas.vehicles import BlacklistSchema, BLResposeSchema, BlacklistedVehicleResponse


async def get_vehicle_by_plate(license_plate: str, db: AsyncSession = Depends(get_db)):

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
    
async def get_vehicle_in_blacklist(license_plate: str, db: AsyncSession):

    Owner = aliased(User)

    stmt = (
        select(
            Blacklist.reason,
            Blacklist.created_at,
            Blacklist.updated_at,
            Vehicle.license_plate,
            User.username.label("user_username"),
            Owner.name.label("owner_name"),
            Owner.email.label("owner_email")
        )
        .join(Vehicle, Blacklist.vehicle_id == Vehicle.id)
        .join(User, Blacklist.user_id == User.id)
        .outerjoin(Owner, Vehicle.owner_id == Owner.id)
    ).where(Vehicle.license_plate == license_plate)
    
    result = await db.execute(stmt)
    bl_vehicle = result.one_or_none()

    if bl_vehicle is None:
        return None

    formatted_result = BlacklistedVehicleResponse(
            license_plate=bl_vehicle.license_plate,
            username=bl_vehicle.user_username,             # username того, хто вніс в blacklist
            owner_name=bl_vehicle.owner_name,              # name власника авто
            owner_email=bl_vehicle.owner_email,            # email власника авто
            created_at=bl_vehicle.created_at,
            updated_at = bl_vehicle.updated_at,
            reason=bl_vehicle.reason
        )

    return formatted_result

async def add_to_black_list(body: BlacklistSchema, vehicle: Vehicle, user: User,
                            db: AsyncSession = Depends(get_db)):
    
    license_plate = Blacklist(user_id = user.id, vehicle_id = vehicle.id, reason = body.reason)
    db.add(license_plate)
    await db.commit()
    await db.refresh(license_plate)
    return f'{body.license_plate} move to black list'

async def add_to_black_list_new_vehicle(body: BlacklistSchema, user: User, db: AsyncSession = Depends(get_db)):
    
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
    # stmt = select(Blacklist).offset(offset).limit(limit)
    stmt = (
        select(Blacklist)
        .options(
            joinedload(Blacklist.vehicle).load_only(Vehicle.license_plate),
            # joinedload(Blacklist.user).load_only(User.name, User.email)
        )
    ).order_by(Blacklist.created_at).offset(offset).limit(limit)
    result = await db.execute(stmt)
    black_list = result.scalars().all()
    # Форматування даних для повернення у відповідності до схеми
    formatted_result = [
        BLResposeSchema(
            license_plate=bl.vehicle.license_plate,
            created_at = bl.created_at,
            updated_at = bl.updated_at,
            reason = bl.reason
        )
        for bl in black_list
    ]
    return formatted_result

# Пояснення
# Використовується aliased(User) для створення окремого приєднання до таблиці User для власників авто.
# select вибирає необхідні поля, включаючи Blacklists.reason, Blacklists.created_at, Vehicle.license_plate, Owner.name, Owner.email та User.username.
# join виконує приєднання відповідних таблиць для отримання потрібних даних.
async def get_blacklisted_vehicles(limit: int, offset: int, db: AsyncSession):
    Owner = aliased(User)

    stmt = (
        select(
            Blacklist.reason,
            Blacklist.created_at,
            Blacklist.updated_at,
            Vehicle.license_plate,
            User.username.label("user_username"),
            Owner.name.label("owner_name"),
            Owner.email.label("owner_email")
        )
        .join(Vehicle, Blacklist.vehicle_id == Vehicle.id)
        .join(User, Blacklist.user_id == User.id)
        .join(Owner, Vehicle.owner_id == Owner.id)
        .order_by(Blacklist.created_at)
    ).offset(offset).limit(limit)
    
    result = await db.execute(stmt)
    blacklisted_vehicles = result.fetchall()

    formatted_result = [
        BlacklistedVehicleResponse(
            license_plate=row.license_plate,
            username=row.user_username,             # username того, хто вніс в blacklist
            owner_name=row.owner_name,              # name власника авто
            owner_email=row.owner_email,            # email власника авто
            created_at=row.created_at,
            updated_at = row.updated_at,
            reason=row.reason
        )
        for row in blacklisted_vehicles
    ]

    return formatted_result

async def update_vehicle_in_blacklist(body: BlacklistSchema, license_plate: str, db: AsyncSession, current_user: User):
    vehicle = await get_vehicle_by_plate(license_plate, db)
    vehicle_new = None
    if body.license_plate != license_plate:
        vehicle_new = await get_vehicle_by_plate(body.license_plate, db)
        if not vehicle_new:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.UPDATED_LICENSE_PLACE_NOT_FOUND)
    if vehicle:
        stmt = select(Blacklist).filter_by(vehicle_id=vehicle.id)
        result = await db.execute(stmt)
        vehicle_bl = result.scalar_one_or_none()
        print(vehicle_bl.reason)
        vehicle_bl.user_id = current_user.id
        if vehicle_new:
            vehicle_bl.vehicle_id = vehicle_new.id
         
        vehicle_bl.reason = body.reason
        vehicle_bl.updated_at = func.now()
        print(vehicle_bl.reason)
        await db.commit() 
        await db.refresh(vehicle_bl)
        return vehicle_bl
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.VEHICLE_NOT_FOUND)
    
async def get_user_by_license_plate(license_plate: str, db: AsyncSession):
    stmt = (
        select(User.name, User.email, Vehicle.license_plate)
        .join(Vehicle, User.id == Vehicle.owner_id)
        .where(Vehicle.license_plate == license_plate)
    )
    
    result = await db.execute(stmt)
    user_vehicle = result.one_or_none()

    if user_vehicle is None:
        return None

    return user_vehicle