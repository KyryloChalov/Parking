import unittest
from unittest.mock import MagicMock, AsyncMock, Mock, patch
import pytest

from unittest.mock import patch, MagicMock
from src.schemas.comments import CommentSchema, CommentUpdateSchema
from src.schemas.photos import PhotosSchema, PhotosResponse
from src.repository.comments import (
    create_comment,
    get_comment,
    get_user_comments_for_photo,
    get_all_comment_for_photo,
    edit_comment,
    delete_comment,
    get_photo_by_id,
)
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from src.conf import messages


@pytest.mark.asyncio
class TestAsyncComment(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.comment = CommentSchema(opinion="Test comment")
        self.session = AsyncMock(spec=AsyncSession)
        self.user_id = "a9b6a9b6-a9b6-a9b6-a9b6-a9b6a9b6a9b6"
        self.photo_id = 1
        self.id = 1

    async def test_create_comment(self):
        with patch(
            "src.repository.comments.Comment", return_value=MagicMock()
        ) as mock_comment:
            result = await create_comment(
                self.comment, self.photo_id, self.user_id, self.session
            )
            # mock_comment.assert_called_once_with(opinion=self.comment, photo_id=self.photo_id, user_id=self.user_id)
            self.session.add.assert_called_once_with(mock_comment.return_value)
            self.session.commit.assert_called_once()
            self.session.refresh.assert_called_once_with(mock_comment.return_value)

    async def test_get_comment(self):
        expected_comment = CommentSchema(opinion="Test comment")
        mocked_comment = MagicMock()
        mocked_comment.scalar_one_or_none.return_value = expected_comment
        self.session.execute.return_value = mocked_comment
        result = await get_comment(self.id, self.session)
        self.assertEqual(result, expected_comment)

    async def test_get_user_comments_for_photo(self):
        comments = [
            CommentSchema(opinion="Test comment one"),
            CommentSchema(opinion="Test comment two"),
        ]
        comments = MagicMock()
        comments.scalars.return_value.all.return_value = comments
        self.session.execute.return_value = comments
        result = await get_user_comments_for_photo(
            self.photo_id, self.user_id, self.session
        )
        self.assertEqual(result, comments)

    async def test_get_all_comment_for_photo(self):
        comments = [
            CommentSchema(opinion="Test comment one"),
            CommentSchema(opinion="Test comment two"),
        ]
        comments = MagicMock()
        comments.scalars.return_value.all.return_value = comments
        self.session.execute.return_value = comments
        result = await get_all_comment_for_photo(self.photo_id, self.session)
        self.assertEqual(result, comments)

    async def test_edit_comment(self):
        body = CommentUpdateSchema(opinion="Test comment")
        mocked_comment = MagicMock()
        mocked_comment.scalars_or_none.return_value = CommentSchema(
            opinion="Test comment"
        )
        self.session.execute.return_value = mocked_comment
        result = await edit_comment(self.id, body, self.session)
        self.assertEqual(result.opinion, body.opinion)
        self.session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_edit_comment_exception(self):
        body = CommentSchema(opinion="Test comment")
        comment_id = 1
        session = MagicMock(spec=AsyncSession)

        mocked_comment = MagicMock()
        mocked_comment.scalar_one_or_none.return_value = CommentSchema(
            opinion="Test comment"
        )
        session.execute.return_value = mocked_comment

        session.commit.side_effect = Exception("Database error")

        with pytest.raises(HTTPException):
            result = await edit_comment(comment_id, body, session)

        session.rollback.assert_called_once()

    async def test_delete_comment(self):
        mocked_comment = MagicMock()
        mocked_comment.scalars_or_none.return_value = CommentSchema(
            opinion="Test comment"
        )
        self.session.execute.return_value = mocked_comment
        result = await delete_comment(self.id, self.session)
        # self.assertIsInstance(result, CommentSchema)
        self.session.delete.assert_called_once()

    async def test_delete_not_existing_comment(self):
        mocked_comment = MagicMock()
        mocked_comment.scalars_or_none.return_value = None
        self.session.execute.return_value = mocked_comment
        self.session.execute.return_value.scalar_one_or_none.return_value = None
        result = await delete_comment(100, self.session)
        self.assertIsNone(result)

    async def test_get_comment_not_existing(self):
        mocked_comment = MagicMock()
        mocked_comment.scalars_or_none.return_value = None
        self.session.execute.return_value = mocked_comment
        self.session.execute.return_value.scalar_one_or_none.return_value = None
        result = await get_comment(100, self.session)
        self.assertIsNone(result)

    async def test_get_comments_no_comments_return(self):
        comments = []
        mocked_comments = MagicMock()
        mocked_comments.scalars.return_value.all.return_value = comments
        self.session.execute.return_value = mocked_comments
        result = await get_user_comments_for_photo(
            self.photo_id, self.user_id, self.session
        )
        self.assertEqual(result, comments)

    async def test_edit_non_existing_comment(self):
        body = CommentUpdateSchema(opinion="Test comment")
        mocked_comment = MagicMock()
        mocked_comment.scalars_or_none.return_value = None
        self.session.execute.return_value = mocked_comment
        self.session.execute.return_value.scalar_one_or_none.return_value = None
        result = await edit_comment(100, body, self.session)
        self.assertIsNone(result)


@pytest.mark.asyncio
async def test_create_comment():
    body = CommentSchema(opinion="Test comment")
    photo_id = 1
    user_id = "a9b6a9b6-a9b6-a9b6-a9b6-a9b6a9b6a9b6"
    session = MagicMock(spec=AsyncSession)

    with patch(
        "src.repository.comments.Comment", return_value=MagicMock()
    ) as mock_comment:
        result = await create_comment(body, photo_id, user_id, session)

        mock_comment.assert_called_once_with(
            opinion=body.opinion, photo_id=photo_id, user_id=user_id
        )
        session.add.assert_called_once_with(mock_comment.return_value)
        session.commit.assert_called_once()
        session.refresh.assert_called_once_with(mock_comment.return_value)
