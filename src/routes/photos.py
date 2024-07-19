import pickle
import time
from typing import Annotated, List


from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    Query,
    status,
    UploadFile,
    File,
    Form,
)

from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from src.schemas.photos import PhotosResponse
from src.database.db import get_db
from src.models.models import User, Photo
from src.schemas.user import UserResponse
from src.services.auth import auth_service
from src.conf.config import config
from src.repository import users as repositories_users
from src.repository import photos as repositories_photos
from src.conf.messages import NO_PHOTO_BY_ID, PHOTO_SUCCESSFULLY_DELETED
from src.conf.constants import CropMode, EffectMode, Effect
from src.routes.ratings import access_delete


router = APIRouter(prefix="/photos", tags=["photos"])


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RateLimiter(times=5, seconds=20))],
)
async def get_all_photos(
    skip_photos: int = 0,
    photos_per_page: int = 10,
    user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    The get_all_photos function returns a list of all photos in the database.
        The function takes three arguments: skip_photos, photos_per_page and user.
        The skip_photos argument is an integer that specifies how many photos to skip before returning results.
        The default value for this argument is 0, which means no skipping will occur and the first photo will be returned.

    The photos_per_page argument is an integer that specifies how many results to return per page (i.e., per request).
    The default value for this argument is 10, which means 10 results will be

    :param skip_photos: int: Skip the first n photos
    :param photos_per_page: int: Specify how many photos will be displayed on one page
    :param user: User: Get the current user from the database
    :param db: AsyncSession: Get a database connection
    :return: A list of photos
    """
    all_photos = await repositories_photos.get_all_photos(
        skip_photos, photos_per_page, db
    )
    return all_photos


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    description="No more than 1 request per 20 second",
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def post_photo(
    photo_description: str | None = Form(
        None, description="Add a description to your photo (string)"
    ),
    file: UploadFile = File(),
    tags: list[str] = Form(
        None, description="Tags to associate with the photo (list of strings)"
    ),
    user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    The post_photo function is used to add a photo.
        201 or error

    :param photo_description: str | None: Describe the photo
    :param description: Add a description to the photo
    :param file: UploadFile: Get the file from the request
    :param tags: list[str]: Get a list of tags from the request separated by ','
    :param description: Add a description to the photo
    :param user: User: Get the current user from the database
    :param db: AsyncSession: Pass the database session to the repository function
    :return: A new_photo object
    """
    list_tags = tags[0].split(",")

    new_photo = await repositories_photos.create_photo(
        file,
        photo_description,
        user,
        db,
        list_tags,
    )
    extention = file.filename.split(".")[-1]
    size = file.size / 1024 / 1024
    if size > 5:
        raise HTTPException(
            status_code=400, detail="Wrong file size (it need less than 5 Mb)!"
        )
    if extention not in ["jpg", "jpeg", "bmp", "gif", "png", "raw", "tiff", "psd"]:
        raise HTTPException(
            status_code=400, detail="Wrong file type (only pictures needed)!"
        )

    return new_photo


@router.get(
    "/{photo_id}",
    name="get_photo",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def get_photo(
    photo_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    """
    The get_photo function is used to get a photo by its id.
        The function returns the photo with all of its data (description, comments, link and QR-code).


    :param photo_id: int: Get the photo by its id
    :param db: AsyncSession: Pass the database connection to the function
    :param user: User: Get the current user from the database
    :return: A photo with a description, comments, link and qr code
    """
    photo = await repositories_photos.get_photo_by_id(photo_id, db)

    if photo:
        return photo

    raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail=NO_PHOTO_BY_ID)


@router.delete(
    "/{photo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def del_photo(
    photo_id: int,
    user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    The del_photo function deletes a photo from the database.
        Args:
            photo_id (int): The id of the photo to be deleted.
            user (User): The current user
            db (AsyncSession): A connection to the database, as determined by get_db().

    :param photo_id: int: Identify the photo to be deleted
    :param user: User: Get the user who is currently logged in
    :param db: AsyncSession: Get the database session
    :return: A dict with one key and value
    :doc-author: Trelent
    """
    result = await repositories_photos.delete_photo(photo_id, user, db)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=NO_PHOTO_BY_ID
        )

    return


@router.patch(
    "/{photo_id}",
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def edit_photo_record(
    photo_id: int,
    new_description: str,
    user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    The edit_photo_record function allows a user to edit the description of an existing photo.
        It also allows them to add tags to the photo.


    :param photo_id: int: Identify the photo record to update
    :param new_description: str: Pass the new description of the photo
    :param user: User: Get the user who is making the request
    :param db: AsyncSession: Get the database connection
    :return: The updated_photo object
    :doc-author: Trelent
    """
    updated_photo = await repositories_photos.edit_photo_description(
        user, photo_id, new_description, db
    )

    if updated_photo:
        return updated_photo

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NO_PHOTO_BY_ID)


@router.post(
    "/{photo_id}/changes/",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def change_photo(
    photo_id: int,
    width: int | None,
    height: int | None,
    crop_mode: CropMode = Form(
        None, description="The cropping mode: fill, thumb, fit, limit, pad, scale"
    ),
    effect: Effect = Form(None, description="The art effects"),
    user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    The change_photo function changes the photo.
        round, high, width, face, cartoonify, vignette, borders

    :param photo_id: int: Identify the photo to be changed
    :param width: int | None: Set the width of the image
    :param height: int | None: Set the height of the photo
    :param crop_mode: CropMode: Specify the cropping mode: fill, thumb, fit, limit, pad or scale
    :param description: Describe the parameter in the documentation
    :param thumb: Crop the image to a square
    :param fit: Fit the image to a certain size
    :param limit: Limit the number of photos returned in a single request
    :param pad: Add padding to the image
    :param scale: Scale the image
    :param effect: Effect: Apply the effect to the photo
    :param description: Describe the endpoint
    :param user: User: Get the user who is making the request
    :param db: AsyncSession: Get the database connection
    :return: A dictionary with the following keys: 'transformed_url', 'QR code'
    :doc-author: Trelent
    """
    if crop_mode is not None:
        crop_mode = crop_mode.name
    else:
        crop_mode = None
    if effect is not None:
        effect = effect.value
    else:
        effect = None

    url_QR = await repositories_photos.change_photo(
        user,
        photo_id,
        db,
        width,
        height,
        crop_mode,
        effect,
    )

    return url_QR


@router.post(
    "/{photo_id}/avatar/",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def make_avatar(
    photo_id: int,
    effect_mode: EffectMode = Form(
        None, description="The cropping mode: fill, thumb, fit, limit, pad, scale"
    ),
    user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    The make_avatar function is used to create a QR code from the photo_id.
        The effect_mode parameter can be used to specify how the image should be cropped.
        If no effect mode is specified, then it will default to None.

    :param photo_id: int: Get the photo_id from the request
    :param effect_mode: EffectMode: Set the cropping mode of the avatar
    :param description: Document the api
    :param thumb: Crop the image in a square shape
    :param fit: Crop the image to a certain size
    :param limit: Limit the number of photos returned
    :param pad: Add padding to the image
    :param scale: Resi the image
    :param user: User: Get the user from the database
    :param db: AsyncSession: Pass the database session to the repository
    :return: A url
    :doc-author: Trelent
    """
    if effect_mode is not None:
        effect_mode = effect_mode.name
    else:
        effect_mode = None

    url_QR = await repositories_photos.make_avatar_from_photo(
        user,
        photo_id,
        effect_mode,
        db,
    )

    return url_QR


@router.post(
    "/tags/{photo_id}",
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def add_tag(
    photo_id: int,
    tag: str,
    user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    The add_tag function adds a tag to the photo with the given id.
        If there is no such tag, it will be created.
        If there is already such a tag under this photo, an error message will be displayed.

    :param photo_id: int: Identify the photo to which we want to add a tag
    :param tag: str: Specify the tag that will be added to the photo
    :param user: User: Get the current user
    :param db: AsyncSession: Get the database session
    :return: A tag, which is added to the photo
    """
    tag = await repositories_photos.add_tag_to_photo(photo_id, tag, db)
    return tag


@router.delete(
    "/tags/{photo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(access_delete)],
)
async def delete_tag(
    photo_id: int,
    tag: str,
    user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    The delete_tag function deletes a tag of the photo_id from the database.
        Args:
            photo_id (int): The id of the photo to delete a tag from.
            tag (str): The name of the tag to be deleted.
        Returns:
            dict: A dictionary containing information about whether or not
                deleting was successful and if it wasn't, why it failed.

    :param photo_id: int: Identify the photo to delete a tag from
    :param tag: str: Specify the tag to be deleted
    :param user: User: Get the current user from the auth_service
    :param db: AsyncSession: Pass the database connection to the function
    :return: A tag object
    :doc-author: Trelent
    """
    tag = await repositories_photos.del_photo_tag(photo_id, tag, db)
    return tag


@router.get(
    "/search/",
    response_model=list[PhotosResponse],
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def search_photo(
    photos_per_page: int = Query(10, ge=10, le=500),
    skip_photos: int = Query(0, ge=0),
    search_keyword: str = Query(),
    rate_min: float = Query(None, ge=0, le=5),
    rate_max: float = Query(None, ge=0, le=5),
    user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    The search_photo function searches for photos in the database.
        The search_photo function takes in a keyword, and returns all photos that contain the keyword.
        If no photo is found with the specified parameters, an HTTP 204 No Content error is raised.

    :param photos_per_page: int: Specify how many photos should be returned per page
    :param ge: Specify the minimum value of a parameter
    :param le: Specify the maximum value of a parameter
    :param skip_photos: int: Skip the first n photos in the database
    :param search_keyword: str: Search for photos with the specified keyword
    :param rate_min: float: Specify the minimum rating of a photo
    :param rate_max: float: Filter photos by the maximum rating
    :param user: User: Get the user from the database
    :param db: AsyncSession: Get the database session
    :return: A list of photos
    """
    if rate_min is None and rate_max is None:
        photos = await repositories_photos.search_photos(
            search_keyword, photos_per_page, skip_photos, db, user
        )
    else:
        photos = await repositories_photos.search_photos_by_filter(
            search_keyword, rate_min, rate_max, photos_per_page, skip_photos, db, user
        )
    if photos == []:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail="Photo with the specified search parameters was not found",
        )
    return photos
