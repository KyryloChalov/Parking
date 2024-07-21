# import uuid

from fastapi import Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar

from src.conf import messages
from src.database.db import get_db
from src.models.models import Role, User
from src.schemas.user import UserSchema, UserUpdateSchema


async def get_user_by_email(email: str, db: AsyncSession = Depends(get_db)):
    """
    The get_user_by_email function takes an email address and returns the user object associated with that email.
    If no such user exists, it returns None.

    :param email: str: Specify the email of the user we want to retrieve
    :param db: AsyncSession: Pass the database session to the function
    :return: A user object
    :doc-author: Trelent
    """
    stmt = select(User).filter_by(email=email)
    user = await db.execute(stmt)
    user = user.scalar_one_or_none()
    return user


async def create_user(body: UserSchema, db: AsyncSession = Depends(get_db)):
    """
    The create_user function creates a new user in the database.

    :param body: UserSchema: Validate the request body
    :param db: AsyncSession: Get the database session
    :return: A user object, which is a sqlalchemy model
    :doc-author: Trelent
    """
    # avatar = None
    # try:
    #     g = Gravatar(body.email)
    #     avatar = g.get_image()
    # except Exception as err:
    #     print(err)

    new_user = User(**body.model_dump())
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: AsyncSession):
    """
    The update_token function updates the user's refresh token in the database.

    :param user: User: Identify the user in the database,
    :param token: str | None: Update the user's refresh token
    :param db: AsyncSession: Pass the database session to the function
    :return: The user object
    :doc-author: Trelent
    """
    user.refresh_token = token
    await db.commit()


async def confirmed_email(email: str, db: AsyncSession = Depends(get_db)) -> None:
    """
    The confirmed_email function takes an email address and a database connection as arguments.
    It then uses the get_user_by_email function to retrieve the user with that email address from
    the database. It sets the confirmed field of that user to True, and commits those changes to
    the database.

    :param email: str: Specify the email address of the user to confirm
    :param db: AsyncSession: Pass the database session to the function
    :return: None
    :doc-author: Trelent
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    await db.commit()


async def update_avatar_url(email: str, url: str | None, db: AsyncSession) -> User:
    """
    The update_avatar_url function updates the avatar url for a user.

    :param email: str: Find the user in the database
    :param url: str | None: Specify that the new url avatar parameter can either be a string or none
    :param db: AsyncSession: Pass in the database session
    :return: A user object
    :doc-author: Trelent
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    await db.commit()
    await db.refresh(user)
    return user


async def update_password(user: User, password: str, db: AsyncSession):
    """
    The update_password function takes a user object, a password string, and an async database session.
    It sets the user's password to the new given password and commits it to the database.

    :param user: User: Pass in the user object that we want to update
    :param password: str: Set the new password for the user
    :param db: AsyncSession: Pass the database session into the function
    :return: None
    :doc-author: Trelent
    """
    user.password = password
    await db.commit()


async def get_all_users(limit: int, offset: int, db: AsyncSession):
    """
    The get_all_contacts function returns a list of all contacts in the database.

    :param limit: int: Limit the number of contacts returned
    :param offset: int: Specify the offset of the first row to return
    :param db: AsyncSession: Pass in the database session to use
    :return: A list of contact objects
    :doc-author: Trelent
    """
    stmt = select(User).offset(offset).limit(limit)
    users = await db.execute(stmt)
    return users.scalars().all()


async def get_user_by_username(username: str, db: AsyncSession):
    stmt = select(User).filter_by(username=username)
    user = await db.execute(stmt)
    user = user.scalar_one_or_none()
    return user

# async def get_info_by_username(username: str, db: AsyncSession):
#     user = await get_user_by_username(username, db)
#     if user:
#         statement = select(func.count()).select_from(Photo).filter_by(user_id=user.id)
#         num_photos: int = await db.execute(statement)
#         num_photos = num_photos.scalar()
#         return user, num_photos
#     else:
#         return user, None

async def update_user(user_id: int, body: UserUpdateSchema, db: AsyncSession, current_user: User):
    stmt = select(User).filter_by(id=user_id)
    user = await db.execute(stmt)
    user = user.scalar_one_or_none()
    print(user.id)
    print(current_user.id)
    if current_user.role == Role.admin:
        user.name = body.name
        user.username = body.username
        user.email = body.email
        user.updated_at = func.now()
        await db.commit()
        await db.refresh(user)
        return user
    else:
        print(messages.USER_NOT_HAVE_PERMISSIONS)
        return user
    
async def change_user_role(user_id: int, body: UserUpdateSchema, db: AsyncSession, current_user: User):
    """
    The change_user_role function changes the role of a user.
        Args:
            user_id (uuid): The id of the user to change.
            body (UserUpdateSchema): A schema containing information about what to change in the database.
            db (AsyncSession): An async session for interacting with our database.
            current_user(User): The currently logged in User object, used for checking permissions and roles.
    
    :param user_id: uuid.UUID: Get the user from the database
    :param body: UserUpdateSchema: Validate the request body
    :param db: AsyncSession: Pass the database session to the function
    :param current_user: User: Check if the user is an admin or not
    :return: A user object with the updated role
    """
    stmt = select(User).filter_by(id=user_id)
    user = await db.execute(stmt)
    user = user.scalar_one_or_none()
    if user:
        if current_user.role == Role.admin:
            user.role = body.role
            user.updated_at = func.now()
            await db.commit()
            await db.refresh(user)
        return user
            
    
# async def delete_user(user_id: int, db: AsyncSession, current_user: User):
    
#     """
#     The delete_user function deletes a user from the database.
#         Args:
#             user_id (uuid): The id of the user to delete.
#             db (AsyncSession): An async session object for interacting with the database.
#             current_user (User): The currently logged in User object, used to determine if they have permission to delete this resource or not.
    
#     :param user_id: uuid.UUID: Get the user_id from the url
#     :param db: AsyncSession: Pass the database session to the function
#     :param current_user: User: Check if the user is an admin or not
#     :return: A user object, which is a dictionary
#     :doc-author: Trelent
#     """
#     stmt = select(User).filter_by(id=user_id)
#     user = await db.execute(stmt)
#     user = user.scalar_one_or_none()
#     if user.id == current_user.id or current_user.role == Role.admin:
#         await db.delete(user)
#         await db.commit()
#         return user
#     else:
#         user.username = messages.USER_NOT_HAVE_PERMISSIONS
#         return user

