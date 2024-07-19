# import pytest
#
# from conftest import client
#
# @pytest.mark.asyncio
# async def test_get_all_photos():
#     response = await client.get("api/photos/")
#     assert response.status_code == 200
#
# @pytest.mark.asyncio
# async def test_post_photo():
#     # Assuming you have a test image file available
#     with open("tests/test.jpg", "rb") as file:
#         response = await client.post(
#             "api/photos/",
#             files={"file": ("tests/test.jpg", file)},
#             data={"photo_description": "Test description", "tags": "tag1,tag2"},
#         )
#     assert response.status_code == 201
#
# @pytest.mark.asyncio
# async def test_get_photo():
#     response = await client.get("api/photos/1")
#     assert response.status_code == 200
#
# @pytest.mark.asyncio
# async def test_del_photo():
#     response = await client.delete("api/photos/1")
#     assert response.status_code == 204
#
# @pytest.mark.asyncio
# async def test_edit_photo_record():
#     response = await client.patch("api/photos/1", json={"new_description": "New description"})
#     assert response.status_code == 404  # Assuming there's no photo with ID 1 in the test database
#
# @pytest.mark.asyncio
# async def test_change_photo():
#     response = await client.post("api/photos/1/changes/")
#     assert response.status_code == 201  # Assuming it returns 201 on success
#
# @pytest.mark.asyncio
# async def test_make_avatar():
#     response = await client.post("api/photos/1/avatar/")
#     assert response.status_code == 201  # Assuming it returns 201 on success
#
# @pytest.mark.asyncio
# async def test_add_tag():
#     response = await client.post("api/photos/tags/1", json={"tag": "new_tag"})
#     assert response.status_code == 200  # Assuming it returns 200 on success
#
# @pytest.mark.asyncio
# async def test_delete_tag():
#     response = await client.delete("api/photos/tags/1", json={"tag": "new_tag"})
#     assert response.status_code == 204  # Assuming it returns 204 on success
#
# @pytest.mark.asyncio
# async def test_search_photo():
#     response = await client.get("api/photos/search/?search_keyword=test")
#     assert response.status_code == 204  # Assuming it returns 204 if no photos found
