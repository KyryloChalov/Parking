"""
Rating API Routes
Provides API routes for creating, retrieving, updating, and deleting rating
"""

import uuid
from typing import List

from fastapi_limiter.depends import RateLimiter
from fastapi import APIRouter, HTTPException, Depends, status, Path, Query, Body, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.models.models import Photo, User, Role, Rating
from src.schemas.photos import RatingSchema, RatingResponseSchema, RatingAVGResponseSchema

from src.services.auth import auth_service
from src.services.roles import RoleAccess
from src.conf import messages, constants
from src.repository import comments as repositories_comments
from src.repository import ratings as repositories_ratings
from src.repository import photos as repositories_photos

router = APIRouter(prefix="/photos", tags=["ratings"])

# Access to the operations by roles
access_get = RoleAccess([Role.admin, Role.moderator, Role.user])
# access_update = RoleAccess([Role.user]) # No need to update rating
access_create = RoleAccess([Role.user])
access_delete = RoleAccess([Role.admin, Role.moderator])


@router.post(
    "/{photo_id}/ratings",
    response_model=RatingResponseSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(access_create)],
)
async def create_rating(photo_id: int,
                        rate: int = Query(ge=1, le=5),
                        db: AsyncSession = Depends(get_db),
                        user: User = Depends(auth_service.get_current_user), ):
    # print(f'{rate=}')
    """
    Function creates a rating for a photo with photo_id.
    If photo with photo_id does not exist, function raises HTTPException.
    If user already set rating for photo, function raises HTTPException.

    :param photo_id: int: The id of the photo to rate.
    :param rate: int: The rating value.
    :param db: AsyncSession: The database session.
    :param user: User: The current user.
    :return: A RatingResponseSchema object containing the created rating.
    :raises HTTPException: If photo with photo_id does not exist, or if user already set rating for photo.
    :raises HTTPException: If rate is not between 1 and 5.
    :raises HTTPException: If user is not authenticated.
    :raises HTTPException: If user is not authorized to access the operation.
    """

    photo_exists: Photo | None = await repositories_photos.get_photo_by_id(photo_id, db)

    if photo_exists is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.PHOTO_NOT_FOUND)

    if photo_exists.user_id == user.id:
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=messages.RATING_OWN_PHOTO,
        )

    is_rating = await repositories_ratings.get_user_rating_for_photo(photo_id, user.id, db)
    if is_rating:
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=messages.RATING_ALREADY_SET,
        )

    new_rating = await repositories_ratings.create_rating(rate, photo_id, user.id, db)
    return new_rating


@router.get(
    "/{photo_id}/user/ratings",
    response_model=RatingResponseSchema,
    dependencies=[Depends(access_get)]
)
async def get_user_rating(
        photo_id: int = Path(ge=1),
        user_id: uuid.UUID = None,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(auth_service.get_current_user),
):
    """
    Function returns a user rating for a photo with photo_id.
    If user not specified, function returns a user rating for the current user for the photo with photo_id.
    If user rating does not exist, function raises HTTPException.

    :param photo_id: int: Get the photo_id from the url
    :param user_id: uuid.UUID: Get the user_id from the url
    :param db: Session: Get the database session
    :param user: User: Get the current user's id
    :return: A RatingResponseSchema object containing the user rating.
    :raises HTTPException: If photo with photo_id does not exist.
    :raises HTTPException: If user rating does not exist.
    """

    photo_exists: Photo | None = await repositories_photos.get_photo_by_id(photo_id, db)

    if photo_exists is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.PHOTO_NOT_FOUND)

    if user_id is None:
        user_id = user.id

    rating = await repositories_ratings.get_user_rating_for_photo(photo_id, user_id, db)

    if rating is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.RATING_NOT_FOUND)
    return rating


@router.get(
    "/{photo_id}/ratings",
    response_model=RatingAVGResponseSchema,
    dependencies=[Depends(access_get)],
)
async def get_avg_rating(photo_id: int = Path(ge=1),
                         db: AsyncSession = Depends(get_db),
                         ):
    """
    Function returns the average rating for a photo with photo_id.
    If photo with photo_id does not exist, function raises HTTPException.

    :param photo_id: int: Get the photo_id from the url
    :param db: Session: Get the database session
    :return: A RatingAVGResponseSchema object containing the average rating.
    :raises HTTPException: If photo with photo_id does not exist.
    """

    avg_rating = await repositories_ratings.get_avg_rating(photo_id, db)

    if avg_rating is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.RATING_NOT_FOUND)

    avg_rating_response = {
        "photo_id": photo_id,
        "rating": round(avg_rating, constants.RATING_DECIMAL_DIGITS)
    }
    return avg_rating_response


@router.delete(
    "/ratings/{rating_id}",
    # status_code=status.HTTP_204_NO_CONTENT,
    response_model=RatingResponseSchema,
    dependencies=[Depends(access_delete)],
)
async def delete_rating(rating_id: int = Path(ge=1),
                        db: AsyncSession = Depends(get_db)):
    """
    Function deletes a rating with rating_id from the database.
    If rating with rating_id does not exist, function raises HTTPException.

    :param rating_id: int: Get the rating_id from the url
    :param db: Session: Get the database session
    :return: A RatingResponseSchema object containing the deleted rating.
    :raises HTTPException: If rating with rating_id does not exist.
    """

    rating = await repositories_ratings.get_rating(rating_id, db)

    if not rating:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.RATING_NOT_FOUND)

    rating = await repositories_ratings.delete_rating(rating_id, db)
    return rating
