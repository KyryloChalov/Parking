"""
Module with functions to work with rating
"""

import uuid

from fastapi import Depends, HTTPException
from sqlalchemy import select, update, func, extract, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.conf import messages
from src.models.models import Photo, Rating


async def create_rating(rating: int,
                        photo_id: int,
                        user_id: uuid.UUID,
                        db: AsyncSession = Depends(get_db), ):
    """
    Create rating

    :param: rating: int - rating to create
    :param: photo_id: int - id of photo to create rating
    :param: user_id: uuid.UUID - id of user to create rating
    :param: db: AsyncSession - database session
    :return: Rating - created rating
    """

    rating = Rating(rating=rating,
                    photo_id=photo_id,
                    user_id=user_id,
                    )
    db.add(rating)
    await db.commit()
    await db.refresh(rating)
    return rating


async def get_user_rating_for_photo(photo_id: int,
                                    user_id: uuid.UUID,
                                    db: AsyncSession = Depends(get_db),
                                    ):
    """
    Get user rating for photo

    :param: photo_id: int - id of photo to get rating
    :param: user_id: uuid.UUID - id of user to get rating
    :param: db: AsyncSession - database session
    :return: Rating - rating for photo with photo_id = photo_id and user_id = user_id or None if rating not found
    """

    # also used for check if user already set rating for photo

    stmt = select(Rating).filter_by(photo_id=photo_id, user_id=user_id)
    rating = await db.execute(stmt)
    return rating.scalar_one_or_none()


async def get_avg_rating(photo_id: int,
                         db: AsyncSession = Depends(get_db),
                         ):
    stmt = select(func.avg(Rating.rating)).filter_by(photo_id=photo_id)
    rating = await db.execute(stmt)
    return rating.scalar_one_or_none()


async def get_rating(rating_id: int,
                     db: AsyncSession = Depends(get_db),
                     ):
    """
    Get rating by id

    :param: rating_id: int - id of rating to get
    :param: db: AsyncSession - database session
    :return: Rating - rating with id = rating_id or None if rating not found
    """

    stmt = select(Rating).filter_by(id=rating_id)
    rating = await db.execute(stmt)
    return rating.scalar_one_or_none()


async def delete_rating(rating_id: int,
                        db: AsyncSession = Depends(get_db),
                        ):
    """
    Delete rating by id

    :param: rating_id: int - id of rating to delete
    :param: db: AsyncSession - database session
    :return: Rating - deleted rating or None if rating not found and rating not deleted
    """

    stmt = select(Rating).filter_by(id=rating_id)
    result = await db.execute(stmt)
    rating = result.scalar_one_or_none()

    if rating:
        await db.delete(rating)
        await db.commit()
    return rating
