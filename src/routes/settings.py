from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.schemas.settings import SettingCreateSchema, SettingUpdateSchema, SettingResponseSchema
from src.services.auth import auth_service
from src.models.models import User, Role, Setting
from src.repository import settings as settings_repository
from src.conf import messages

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("/", response_model=SettingResponseSchema)
async def get_settings(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user)
):
    """
    Get settings.

    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Get the current user
    :return: A settings object
    """

    if user.role not in [Role.admin, Role.user]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=messages.USER_NOT_HAVE_PERMISSIONS)

    return await settings_repository.get_settings(db)


@router.post("/", response_model=SettingCreateSchema)
async def create_settings(
    setting: SettingCreateSchema,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user)
):
    """
    Create settings.

    :param setting: SettingCreateSchema: Pass the setting object to the function
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Get the current user
    :return: A settings object
    """

    if user.role != Role.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=messages.USER_NOT_HAVE_PERMISSIONS)

    return await settings_repository.create_settings(setting, db)


@router.put("/{setting_id}", response_model=SettingUpdateSchema)
async def update_settings(
    setting_id: int,
    setting_update: SettingUpdateSchema,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user)
):
    """
    Update settings.

    :param setting_id: int: Specify the setting to be updated
    :param setting_update: SettingUpdateSchema: Validate the request body
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Get the current user
    :return: The updated setting object
    """

    if user.role != Role.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=messages.USER_NOT_HAVE_PERMISSIONS)

    return await settings_repository.update_settings(setting_id, setting_update, db)


@router.delete("/{setting_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_settings(
    setting_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user)
):
    """
    Delete settings.

    :param setting_id: int: Specify the setting to be deleted
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Get the current user
    :return: None
    """
    
    if user.role != Role.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=messages.USER_NOT_HAVE_PERMISSIONS)

    await settings_repository.delete_settings(setting_id, db)

    return None
