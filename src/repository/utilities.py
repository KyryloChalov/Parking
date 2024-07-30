from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased
from datetime import datetime
from src.models.models import Parking_session, Payment, Vehicle, User


async def get_parking_data(start_date: datetime, end_date_: datetime, db: AsyncSession):
    end_date = end_date_.replace(hour=23, minute=59, second=59)
    VehicleAlias = aliased(Vehicle)
    UserAlias = aliased(User)
    PaymentAlias = aliased(Payment)
    stmt = (
        select(
            Parking_session.id,
            Parking_session.created_at.label("session_created_at"),
            VehicleAlias.license_plate,
            UserAlias.username,
            UserAlias.email,
            PaymentAlias.created_at.label("payment_created_at"),
            PaymentAlias.amount,
        )
        .join(VehicleAlias, Parking_session.vehicle_id == VehicleAlias.id)
        .join(UserAlias, VehicleAlias.owner_id == UserAlias.id, isouter=True)
        .join(PaymentAlias, PaymentAlias.session_id == Parking_session.id, isouter=True)
        .where(
            and_(
                Parking_session.created_at >= start_date,
                Parking_session.created_at <= end_date,
            )
        )
    )
    results = await db.execute(stmt)
    sessions = results.fetchall()
    return sessions



# from sqlalchemy import select
# from sqlalchemy.ext.asyncio import AsyncSession
# from datetime import datetime
# from src.models.models import Parking_session, Payment, Vehicle, User


# async def get_parking_data(start_date: datetime, end_date: datetime, db: AsyncSession):
#     query = (
#         select(
#             Parking_session.id,
#             Vehicle.license_plate,
#             User.username,
#             Parking_session.created_at,
#             Parking_session.updated_at,
#             Payment.amount,
#             Payment.created_at,
#         )
#         .join(Vehicle, Parking_session.vehicle_id == Vehicle.id)
#         .join(User, Vehicle.owner_id == User.id)
#         .join(Payment, Payment.session_id == Parking_session.id)
#         .where(Payment.created_at >= start_date)
#         .where(Payment.created_at <= end_date)
#     )
#     # result = await db.execute(query)
#     # return result.all()
#     result = await db.execute(query)
#     records = result.all()
#     print(f"1. {records = }")

#     return records