from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from fastapi import HTTPException, status

from src.conf import messages
from src.models.models import Setting
from src.schemas.settings import SettingCreateSchema, SettingUpdateSchema, SettingResponseSchema


async def get_settings(db: AsyncSession) -> SettingResponseSchema:
    """
    Get the settings from the database.

    :param db: AsyncSession
    :return: Setting
    """

    result = await db.execute(select(Setting))
    setting = result.scalars().first()
    if setting is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=messages.SETTINGS_NOT_FOUND)
    return setting


async def create_settings(
        setting_data: SettingCreateSchema, 
        db: AsyncSession) -> SettingResponseSchema:
    """
    Create a new setting in the database.

    :param setting_data: SettingCreateSchema
    :param db: AsyncSession
    :return: Setting
    """

    existing_setting = await db.execute(select(Setting))

    if existing_setting.scalars().first() is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=messages.SETTINGS_ALREADY_EXIST)

    new_setting = Setting(
        capacity=setting_data.capacity,
        num_days_reminder=setting_data.num_days_reminder,
        num_days_benefit=setting_data.num_days_benefit
    )
    db.add(new_setting)
    await db.commit()
    await db.refresh(new_setting)

    return new_setting


async def update_settings(
        setting_id: int, 
        setting_update: SettingUpdateSchema, 
        db: AsyncSession):
    """
    Update an existing setting in the database.

    :param setting_id: int
    :param setting_update: SettingUpdateSchema
    :param db: AsyncSession
    :return: Setting
    """

    stmt = select(Setting).filter_by(id=setting_id)
    result = await db.execute(stmt)
    existing_setting = result.scalar_one_or_none()

    if existing_setting is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=messages.SETTINGS_NOT_FOUND)

    update_stmt = (
        update(Setting)
        .where(Setting.id == setting_id)
        .values(
            capacity=setting_update.capacity,
            num_days_reminder=setting_update.num_days_reminder,
            num_days_benefit=setting_update.num_days_benefit
            # updated_at=func.now()
        )
        .execution_options(synchronize_session="fetch")
    )

    await db.execute(update_stmt)
    await db.commit()

    result = await db.execute(select(Setting).filter_by(id=setting_id))

    return result.scalar_one()


async def delete_settings(
        setting_id: int, 
        db: AsyncSession):
    """
    Delete a setting by its ID.

    :param setting_id: int
    :param db: AsyncSession
    :return: None
    """

    stmt = select(Setting).filter_by(id=setting_id)
    result = await db.execute(stmt)
    setting = result.scalar_one_or_none()

    if setting is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=messages.SETTINGS_NOT_FOUND)

    delete_stmt = delete(Setting).where(Setting.id == setting_id)
    await db.execute(delete_stmt)
    await db.commit()
    
