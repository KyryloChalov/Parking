"""
Comments API Routes
Provides API routes for creating, retrieving, updating, and deleting comments.
"""

import uuid
from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File
from typing import List
from sqlalchemy import select, or_, and_, extract
from datetime import datetime

from fastapi_limiter.depends import RateLimiter
from fastapi import APIRouter, HTTPException, Depends, status, Path, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.models.models import User, Role, Comment
from src.schemas.comments import CommentSchema, CommentResposeSchema, CommentUpdateSchema

from src.services.auth import auth_service
from src.services.roles import RoleAccess
from src.conf.config import config
from src.conf import messages
from src.repository import comments as repositories_comments
from src.repository import photos as repositories_photos

router = APIRouter(prefix="/photos", tags=["comments"])

# Access to the operations by roles
access_get = RoleAccess([Role.admin, Role.moderator, Role.user])
access_update = RoleAccess([Role.user])
access_create = RoleAccess([Role.user])
access_delete = RoleAccess([Role.admin, Role.moderator])


@router.post(
    "/{photo_id}/comments",
    response_model=CommentResposeSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(access_create)],
)
async def create_comment(photo_id: int,
                         comment: CommentSchema,
                         db: AsyncSession = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    """
    Function creates a comment for the photo with photo_id.

    :param photo_id: int: Get the photo_id from the url
    :param comment: CommentSchema: Get the comment from the request body
    :param db: Session: Get the database session
    :param user: User: Get the current user's id
    :return: A CommentResposeSchema object containing the created comment.
    """

    photo_exists = await repositories_photos.get_photo_by_id(photo_id, db)
    if photo_exists is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.PHOTO_NOT_FOUND)

    new_comment = await repositories_comments.create_comment(comment, photo_id, user.id, db)

    return new_comment


@router.get(
    "/{photo_id}/comments",
    response_model=List[CommentResposeSchema],
    dependencies=[Depends(access_get)],
)
async def get_all_comments(limit: int = Query(10, ge=10, le=100),
                           offset: int = Query(0, ge=0),
                           photo_id: int = Path(ge=1),
                           db: AsyncSession = Depends(get_db), ):
    """
    Function returns a list of comments for the photo with photo_id

    :limit: int: Get the limit from the query parameters
    :offset: int: Get the offset from the query parameters
    :param photo_id: int: Get the photo_id from the url
    :param db: Session: Get the database session
    :return: A list of comments for the photo with photo_id. If the photo with photo_id is not found, an HTTPException is raised.
    """

    comments = await repositories_comments.get_all_comment_for_photo(photo_id, db)
    if not comments:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.COMMENT_NOT_FOUND)
    return comments


@router.get(
    "/{photo_id}/user/comments",
    response_model=list[CommentResposeSchema],
    dependencies=[Depends(access_get)]
)
async def get_user_comments(
        photo_id: int = Path(ge=1),
        user_id: uuid.UUID = None,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(auth_service.get_current_user),
):
    """
    Function returns a list of users comments with user_id for the photo with photo_id
    If user not specified, function returns a list of comments for the current user for the photo with photo_id.

    :param db: Session: Get the database session
    :param user_id: int: Get the comments of a specific user
    :param photo_id: int: Get the photo_id from the url
    :param user: User: Get the current user's id
    :return: A list of comments
    """

    if user_id is None:
        user_id = user.id

    comments = await repositories_comments.get_user_comments_for_photo(photo_id, user_id, db)

    if comments is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.COMMENT_NOT_FOUND)
    return comments


# @router.put(
@router.patch(
    "/comments/{comment_id}",
    response_model=CommentUpdateSchema,
    dependencies=[Depends(access_update)],
)
async def update_comment(comment_id: int = Path(ge=1),
                         body: CommentUpdateSchema = Body(...),
                         db: AsyncSession = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    """
    Function updates a comment with comment_id in the database.

    :param comment_id: int: Get the comment_id from the url
    :param body: CommentUpdateSchema: Get the comment from the request body
    :param db: Session: Get the database session
    :param user: User: Get the current user's id
    :return: A CommentUpdateSchema object containing the updated comment.
    """

    comment = await repositories_comments.get_comment(comment_id, db)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.COMMENT_NOT_FOUND)

    updated_comment = await repositories_comments.edit_comment(comment_id, body, db)
    updated_comment.updated_at = datetime.now()
    return updated_comment


@router.delete(
    "/comments/{comment_id}",
    # status_code=status.HTTP_204_NO_CONTENT,
    response_model=CommentResposeSchema,
    dependencies=[Depends(access_delete)],
)
async def delete_comment(comment_id: int = Path(ge=1),
                         user: User = Depends(auth_service.get_current_user),
                         db: AsyncSession = Depends(get_db)):
    """
    Function deletes a comment with comment_id from the database.

    :param comment_id: int: Get the comment_id from the url
    :param user: User: Get the current user's id
    :param db: Session: Get the database session
    :return: A CommentResposeSchema object containing the deleted comment.
    """

    comment = await repositories_comments.get_comment(comment_id, db)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.COMMENT_NOT_FOUND)

    comment = await repositories_comments.delete_comment(comment_id, db)
    return comment
