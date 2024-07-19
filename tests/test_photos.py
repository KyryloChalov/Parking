import unittest
from pathlib import Path
from unittest.mock import AsyncMock, Mock, MagicMock, patch

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.models import User, Photo
from src.schemas.photos import PhotosSchema, PhotosResponse, RatingSchema
from src.conf.messages import (
    PHOTO_SUCCESSFULLY_ADDED,
    PHOTO_NOT_FOUND,
    TAG_SUCCESSFULLY_ADDED,
)
from src.repository.photos import (
    get_all_photos,
    get_or_create_tag,
    check_tags_quantity,
    assembling_tags,
    get_QR_code,
    get_photo_by_id,
    create_photo,
    add_tag_to_photo,
    edit_photo_description,
    delete_photo,
    del_photo_tag,
    change_photo,
    make_avatar_from_photo,
    search_photos,
    search_photos_by_filter,
)


class TestPhotos(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = AsyncMock(spec=AsyncSession)
        self.user = User(
            id="2380f815-f526-4017-a1df-f69ab48b86f9",
            username="test_user",
            email="test@test.com",
            password="qwerty",
            role="admin",
            confirmed=True,
        )
        self.photo = Photo(
            id=1,
            path="tests/test.jpg",
            description="test",
            user_id=User.id,
            # tags=["test", "test2"],
        )

    async def test_get_all_photos(self):
        photos = [Photo(), Photo(), Photo()]
        mocked_photos = MagicMock()
        mocked_photos.scalars.return_value.all.return_value = photos
        self.session.execute.return_value = mocked_photos
        result = await get_all_photos(0, 10, self.session)
        self.assertEqual(result, photos)

    async def test_get_or_create_tag(self):
        tag = "test"
        mocked_tag = MagicMock()
        mocked_tag.first.return_value = None
        self.session.execute.return_value = mocked_tag
        result = await get_or_create_tag(tag, self.session)
        self.assertTrue(result)

    def test_check_tags_quantity(self):
        tags = ["test", "test2"]
        mocked_tag = MagicMock()
        mocked_tag.first.return_value = None
        self.session.execute.return_value = mocked_tag
        result = check_tags_quantity(tags)
        self.assertTrue(result)

    async def test_assembling_tags(self):
        tags = ["test", "test2"]
        mocked_tag = MagicMock()
        mocked_tag.first.return_value = None
        self.session.execute.return_value = mocked_tag
        result = await assembling_tags(tags, self.session)
        self.assertTrue(result)

    async def test_get_QR_code(self):
        photo_id = 1
        mocked_photo = MagicMock()
        mocked_path = MagicMock()
        mocked_photo.first.return_value = self.photo
        self.session.execute.return_value = mocked_photo
        result = await get_QR_code(mocked_path, photo_id, self.session)
        self.assertEqual(type(result), type(str()))

    async def test_get_photo_by_id(self):
        photo_id = 1
        mocked_photo = MagicMock()
        mocked_photo.first.return_value = self.photo
        self.session.execute.return_value = mocked_photo
        result = await get_photo_by_id(photo_id, self.session)
        self.assertTrue(result)

    @patch("cloudinary.uploader.upload")
    async def test_create_photo(self, patch):
        tags = ["tag1", "tag2"]
        mocked_user = MagicMock()
        mocked_user.username = self.user.username
        mocked_user.first.return_value = self.user
        mocked_photo = MagicMock()
        self.session.execute.return_value = mocked_user
        result = await create_photo(
            mocked_photo, self.photo.description, mocked_user.id, self.session, tags
        )
        self.assertEqual(result["success message"], PHOTO_SUCCESSFULLY_ADDED)

    # failed
    async def test_add_tag_to_photo(self):
        tag = "tag5"
        mocked_photo = MagicMock()
        mocked_photo.id = 1
        mocked_photo.tags = ["tag1", "tag2"]
        mocked_photo.first.return_value = self.photo
        self.session.execute.return_value = mocked_photo
        result = await add_tag_to_photo(mocked_photo.id, tag, self.session)
        self.assertEqual(result["success message"], TAG_SUCCESSFULLY_ADDED)

    async def test_edit_photo_description(self):
        description = "test_test"
        mocked_photo = MagicMock()
        mocked_photo.id = 1
        mocked_photo.first.return_value = self.photo
        self.session.execute.return_value = mocked_photo
        result = await edit_photo_description(
            self.user, self.photo.id, description, self.session
        )
        self.assertTrue(result)

    async def test_delete_photo(self):
        mocked_photo = MagicMock()
        mocked_photo.id = 1
        mocked_photo.first.return_value = self.photo
        self.session.execute.return_value = mocked_photo
        result = await delete_photo(self.photo.id, self.user, self.session)
        self.assertIsNone(result)

    async def test_del_photo_tag(self):
        tag_for_del = "test"
        mocked_photo = MagicMock()
        mocked_photo.first.return_value = self.photo
        self.session.execute.return_value = mocked_photo
        result = await del_photo_tag(self.photo.id, tag_for_del, self.session)
        self.assertTrue(result)

    @patch("cloudinary.uploader.upload")
    async def test_change_photo(self, patch):
        mocked_photo = MagicMock()
        mocked_photo.id = 1
        mocked_photo.first.return_value = self.photo
        self.session.execute.return_value = mocked_photo
        result = await change_photo(
            self.user, mocked_photo.id, self.session, 100, 150, "fill", "art"
        )
        self.assertTrue(result)

    @patch("cloudinary.uploader.upload")
    async def test_make_avatar_from_photo(self, patch):
        mocked_photo = MagicMock()
        mocked_photo.first.return_value = self.photo
        self.session.execute.return_value = mocked_photo
        result = await make_avatar_from_photo(
            self.user, self.photo.id, "art", self.session
        )
        self.assertTrue(result)

    async def test_search_photos(self):
        photos = [Photo(), Photo(), Photo()]
        mocked_photos = MagicMock()
        mocked_photos.scalars.return_value.all.return_value = photos
        self.session.execute.return_value = mocked_photos
        result = await search_photos("test", 10, 0, self.session, self.user)
        self.assertTrue(result)
        self.assertEqual(type(result), type(list()))

    async def test_search_photos_by_filter(self):
        photos = [Photo(), Photo(), Photo()]
        mocked_photos = MagicMock()
        mocked_photos.scalars.return_value.all.return_value = photos
        self.session.execute.return_value = mocked_photos
        result = await search_photos_by_filter(
            "test", 0, 5, 10, 0, self.session, self.user
        )
        self.assertTrue(result)

    def test_check_tags_quantity_error(self):
        tags = ["test", "test2", "test3", "test4", "test5", "test6"]
        mocked_tag = MagicMock()
        mocked_tag.first.return_value = None
        self.session.execute.return_value = mocked_tag
        try:
            check_tags_quantity(tags)
        except Exception as result:
            self.assertEqual(result.status_code, 400)
