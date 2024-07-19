"""
Module with functions to work with comments
"""

import uuid

from fastapi import Depends, HTTPException
from sqlalchemy import select, update, func, extract, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.schemas.comments import (
    CommentSchema,
    CommentResposeSchema,
    CommentUpdateSchema,
)
from src.conf import messages
from src.models.models import Comment, Photo
from src.repository.photos import get_photo_by_id


async def create_comment(
    comment: CommentSchema,
    photo_id: int,
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Create comment

    :param: comment: CommentSchema - comment to create
    :param: photo_id: int - id of photo to create comment
    :param: user_id: uuid.UUID - id of user to create comment
    :param: db: AsyncSession - database session
    :return: Comment - created comment
    """

    comment = Comment(
        opinion=comment.opinion,
        photo_id=photo_id,
        user_id=user_id,
    )
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return comment


async def get_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get comment by id

    :param: comment_id: int - id of comment to get
    :param: db: AsyncSession - database session
    :return: Comment - comment with id = comment_id
    """

    stmt = select(Comment).filter_by(id=comment_id)
    comment = await db.execute(stmt)
    return comment.scalar_one_or_none()


async def get_user_comments_for_photo(
    photo_id: int,
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Get comment by photo_id and user_id

    :param: photo_id: int - id of photo to get comment
    :param: user_id: uuid.UUID - id of user to get comment
    :param: db: AsyncSession - database session
    :return: Comment - comment with photo_id = photo_id and user_id = user_id
    """

    stmt = select(Comment).filter_by(photo_id=photo_id, user_id=user_id)
    comment = await db.execute(stmt)
    return comment.scalars().all()


async def get_all_comment_for_photo(
    photo_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get comment by photo_id

    :param: photo_id: int - id of photo to get comment
    :param: db: AsyncSession - database session
    :return: Comment - comment with photo_id = photo_id
    """

    stmt = select(Comment).filter_by(photo_id=photo_id)
    comment = await db.execute(stmt)
    return comment.scalars().all()


async def edit_comment(
    comment_id: int,
    body: CommentUpdateSchema,
    db: AsyncSession = Depends(get_db),
):
    """
    Edit comment

    :param: comment_id: int - id of comment to edit
    :param: body: CommentUpdateSchema - new comment
    :param: db: AsyncSession - database session
    :return: Comment - edited comment or None if comment with comment_id not exist
    """

    stmt = select(Comment).filter_by(id=comment_id)
    result = await db.execute(stmt)
    comment = result.scalar_one_or_none()

    if not comment:
        return None

    if comment.opinion is not None:
        comment.opinion = body.opinion

    try:
        await db.commit()
        await db.refresh(comment)
    except Exception as e:
        await db.rollback()
        print(f"Error: {e}")
        raise HTTPException(status_code=409, detail=messages.ERROR_UPDATING_COMMENT)

    return comment


async def delete_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Delete comment

    :param: comment_id: int - id of comment to delete
    :param: db: AsyncSession - database session
    :return: Comment - deleted comment or None if comment with comment_id not exist
    """

    stmt = select(Comment).filter_by(id=comment_id)
    result = await db.execute(stmt)
    comment = result.scalar_one_or_none()
    if comment:
        await db.delete(comment)
        await db.commit()
    return comment
