from datetime import datetime
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

from src.database.db import get_db
from src.models.models import User, Role
from src.schemas.vehicles import (
    Reminder,
    VehicleResponse,
)
from src.services.auth import auth_service
from src.conf import messages
from src.conf.config import config
from src.services.roles import RoleAccess
from src.repository import vehicles as repositories_vehicles
from src.services.email import send_email_by_license_plate

router = APIRouter(prefix="/utilities", tags=["utilities"])

access_to_route_all = RoleAccess([Role.admin])

@router.post("/email_reminder")#, response_model=list[VehicleResponse])
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
                status_code=status.HTTP_404_NOT_FOUND, detail=messages.VEHICLE_NOT_FOUND)
    
    try:
        for v in vehicles:
            days_reminder = v.ended_at - datetime.now().date()
            user_vehicle = await repositories_vehicles.get_user_by_license_plate(
                v.license_plate, db)
            background_tasks.add_task(
            send_email_by_license_plate,
            user_vehicle.email,
            user_vehicle.name,
            v.license_plate,
            days_reminder.days,
        )
        return f"E-mails was sent to owner of vehicles"
    except Exception as e:
        raise HTTPException(detail=f"Failed to send email: {e}")