import unittest
from unittest.mock import MagicMock, AsyncMock, Mock, patch
import pytest

from unittest.mock import patch, MagicMock
from src.schemas.photos import RatingSchema, RatingResponseSchema, RatingAVGResponseSchema
from src.repository.ratings import create_rating, get_user_rating_for_photo, get_avg_rating, get_rating, delete_rating

from sqlalchemy.ext.asyncio import AsyncSession


class TestAsyncRating(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        # self.rating = RatingSchema()
        self.session = AsyncMock(spec=AsyncSession)
        self.user_id = "a9b6a9b6-a9b6-a9b6-a9b6-a9b6a9b6a9b6"
        self.photo_id = 1
        self.id = 1
        self.rating: int = 4
        self.avgrating: float = 4.56

    async def test_create_rating(self):
        with patch(
                'src.repository.ratings.create_rating') as mocked_create_rating:
            result = await create_rating(self.rating, self.photo_id, self.user_id, self.session)

        # mocked_create_rating.assert_called_once_with(self.rating, self.photo_id, self.user_id, self.session)

        # self.assertIsInstance(result, RatingResponseSchema)
        # self.assertEquals(result.rating, self.rating)
        # self.assertEquals(result.user_id, self.user_id)
        # self.assertEquals(result.id, self.id)
        self.session.commit.assert_called()
        self.session.refresh.assert_called()
        self.session.commit.assert_called_once()
        self.session.refresh.assert_called_once()

    async def test_create_rating_alternative(self):
        body = RatingSchema(rating=4)
        photo_id = 1
        user_id = "a9b6a9b6-a9b6-a9b6-a9b6-a9b6a9b6a9b6"
        session = MagicMock(spec=AsyncSession)

        with patch('src.repository.ratings.Rating', return_value=MagicMock()) as mock_rating:
            result = await create_rating(body.rating, photo_id, user_id, session)

            mock_rating.assert_called_once_with(rating=body.rating, photo_id=photo_id, user_id=user_id)
            session.add.assert_called_once_with(mock_rating.return_value)
            session.commit.assert_called_once()
            session.refresh.assert_called_once_with(mock_rating.return_value)

    async def test_get_user_rating_for_photo(self):
        expected_rating = RatingResponseSchema(id=self.id, photo_id=self.photo_id, user_id=self.user_id, rating=4)
        mocked_rating = MagicMock()
        mocked_rating.scalar_one_or_none.return_value = expected_rating
        self.session.execute.return_value = mocked_rating
        result = await get_user_rating_for_photo(self.photo_id, self.user_id, self.session)
        self.assertEqual(result, expected_rating)

    async def test_get_avg_rating(self):
        expected_rating = {
            "photo_id": self.photo_id,
            "rating": self.avgrating,
        }
        # RatingAVGResponseSchema(photo_id=self.photo_id, avgrating=self.avgrating)
        mocked_rating = MagicMock()
        mocked_rating.scalar_one_or_none.return_value = expected_rating
        self.session.execute.return_value = mocked_rating
        result = await get_avg_rating(self.photo_id, self.session)
        self.assertEqual(result, expected_rating)

    async def test_get_rating(self):
        expected_rating = RatingResponseSchema(id=self.id, photo_id=self.photo_id, user_id=self.user_id,
                                               rating=self.rating)
        mocked_rating = MagicMock()
        mocked_rating.scalar_one_or_none.return_value = expected_rating
        self.session.execute.return_value = mocked_rating
        result = await get_rating(self.id, self.session)
        self.assertEqual(result, expected_rating)

    async def test_delete_rating(self):
        expected_rating = RatingResponseSchema(id=self.id, photo_id=self.photo_id, user_id=self.user_id,
                                               rating=self.rating)
        mocked_rating = MagicMock()
        mocked_rating.scalar_one_or_none.return_value = expected_rating
        self.session.execute.return_value = mocked_rating
        result = await delete_rating(self.id, self.session)
        self.assertEqual(result, expected_rating)

        self.session.delete.assert_called_once()
        self.session.commit.assert_called_once()

    async def test_delete_not_existing_rating(self):
        mocked_rating = MagicMock()
        mocked_rating.scalars_or_none.return_value = None
        self.session.execute.return_value = mocked_rating
        self.session.execute.return_value.scalar_one_or_none.return_value = None
        result = await delete_rating(100, self.session)
        self.assertIsNone(result)

    async def test_get_not_existing_foto_rating(self):
        mocked_rating = MagicMock()
        mocked_rating.scalars_or_none.return_value = None
        self.session.execute.return_value = mocked_rating
        self.session.execute.return_value.scalar_one_or_none.return_value = None
        result = await get_user_rating_for_photo(100, self.user_id, self.session)
        self.assertIsNone(result)

    async def test_get_not_existing_avg_rating(self):
        mocked_rating = MagicMock()
        mocked_rating.scalars_or_none.return_value = None
        self.session.execute.return_value = mocked_rating
        self.session.execute.return_value.scalar_one_or_none.return_value = None
        result = await get_avg_rating(100, self.session)
        self.assertIsNone(result)
