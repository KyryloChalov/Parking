import pickle
from typing import Annotated
from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    status,
    Path,
    Query,
    Security,
    BackgroundTasks,
    Request,
)
from fastapi.security import (
    OAuth2PasswordRequestForm,
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.models import User
from src.database.db import get_db
from src.conf import messages
from src.repository import users as repositories_users
from src.schemas.user import (
    UserSchema,
    TokenSchema,
    UserResponse,
    RequestEmail,
    UserResetPassword,
)
from src.services.auth import auth_service
from src.services.email import send_email, send_reset_passw_email
from src.conf.constants import ACCESS_TOKEN_TIME_LIVE

auth_router = APIRouter(prefix="/auth", tags=["auth"])
get_refresh_token = HTTPBearer()


@auth_router.post(
    "/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def signup(
    body: UserSchema,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    The signup function creates a new user in the database.
    It takes a UserSchema object as input, and returns the newly created user.
    If an account with that email already exists, it raises an HTTPException.

    :param body: UserSchema: Validate the request body
    :param background_tasks: BackgroundTasks: Add a task to the background tasks queue
    :param request: Request: Get the base url of the request
    :param db: AsyncSession: Pass the database session to the function
    :return: A user object
    :doc-author: Trelent
    """
    exist_user_email = await repositories_users.get_user_by_email(body.email, db)
    exist_user_username = await repositories_users.get_user_by_username(body.username, db)
    if exist_user_email or exist_user_username:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=messages.ACCOUNT_EXIST
        )
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repositories_users.create_user(body, db)
    auth_service.cache.set(new_user.email, pickle.dumps(new_user))
    auth_service.cache.expire(new_user.email, 300)
    background_tasks.add_task(
        send_email, new_user.email, new_user.username, str(request.base_url)
    )
    return new_user


@auth_router.post("/login", response_model=TokenSchema)
async def login(
    body: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    """
    The login function is used to authenticate a user.
    It takes in the username and password of the user, and returns an access token if successful.
    The access token can be used to make requests on behalf of that user.

    :param body: OAuth2PasswordRequestForm: Get the username and password from the request body
    :param db: AsyncSession: Get the database session
    :return: A dictionary with the access token, refresh token and the type of token
    :doc-author: Trelent
    """
    user = await repositories_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.INVALID_EMAIL
        )
    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=messages.EMAIL_NOT_CONFIRMED,
        )
    if user.banned:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=messages.USER_FORBIDDEN
        )
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.INVALID_PASSWORD
        )
    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repositories_users.update_token(user, refresh_token, db)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@auth_router.post("/logout")
async def logout(
    token: Annotated[str, Depends(auth_service.oauth2_scheme)],
    user: User = Depends(auth_service.get_current_user),
):
    """
    The logout function is used to logout a user.
        It takes in the token of the user and returns a message that says &quot;Successfully logged out.&quot;


    :param token: Annotated[str: Pass the token to the logout function
    :param Depends(auth_service.oauth2_scheme)]: Get the token from the request header
    :param user: User: Get the current user
    :return: The message &quot;logout successful&quot; as a json object
    :doc-author: Trelent
    """

    username = user.username
    # auth_service.cache.set("ban_token", "True")
    auth_service.cache.set(username, pickle.dumps(token))
    auth_service.cache.expire(username, 60*ACCESS_TOKEN_TIME_LIVE)
    return {"message": messages.LOGOUT}


@auth_router.get("/refresh_token", response_model=TokenSchema)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(get_refresh_token),
    db: AsyncSession = Depends(get_db),
):
    """
    The refresh_token function is used to refresh the access token.
    The function takes in a refresh_token and returns an access_token.

    :param credentials: HTTPAuthorizationCredentials: Get the token from the authorization header
    :param db: AsyncSession: Get a database session
    :return: An access_token and a refresh_token
    :doc-author: Trelent
    """
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repositories_users.get_user_by_email(email, db)
    # попитка несанкціонірованого входа - обнуляем refresh_token
    if user.refresh_token != token:
        await repositories_users.update_token(user, None, db)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repositories_users.update_token(user, refresh_token, db)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@auth_router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):
    """
    The confirmed_email function is used to confirm a user's email address.
    It takes in the token that was sent to the user's email and uses it to get their email address.
    Then, it checks if there is a user with that email in the database. If not, then an error message will be returned.
    If there is a user with that email, then we check if they have already confirmed their account or not by checking
    whether or not they are confirmed (True/False). If they are already confirmed, then we return another message saying so;
    otherwise we update them as being confirmed and

    :param token: str: Get the token from the url
    :param db: AsyncSession: Get the database session
    :return: A message that the email has been confirmed
    :doc-author: Trelent
    """
    email = await auth_service.get_email_from_token(token)
    user = await repositories_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=messages.VERIFICATION_ERROR
        )
    if user.confirmed:
        return {"message": messages.EMAIL_ALREADY_CONFIRMED}
    await repositories_users.confirmed_email(email, db)
    return {"message": messages.EMAIL_CONFIRMED}


@auth_router.post("/request_email")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    The request_email function is used to send an email to the user with a link that will allow them
    to confirm their account. The function takes in a RequestEmail object, which contains the user's email address.
    The function then checks if the user exists and if they have already confirmed their account. If they have not,
    the function sends an email containing a link that will allow them to confirm their account.

    :param body: RequestEmail: Get the email from the request body
    :param background_tasks: BackgroundTasks: Add a task to the background tasks queue
    :param request: Request: Get the base url of the application
    :param db: AsyncSession: Pass the database session to the function
    :return: A message that the user can check their email for confirmation
    :doc-author: Trelent
    """
    user = await repositories_users.get_user_by_email(body.email, db)

    if user.confirmed:
        return {"message": messages.EMAIL_ALREADY_CONFIRMED}
    if user:
        background_tasks.add_task(
            send_email, user.email, user.username, str(request.base_url)
        )
    return {"message": messages.CHECK_EMAIL}


@auth_router.post("/reset_password")
async def reset_passw_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    The reset_passw_email function is used to send an email with a link to reset the password.
    The user must enter his email and if it exists, he will receive an email with a link that
    will take him to the page where he can update his password.

    :param body: RequestEmail: Get the email from the request body
    :param background_tasks: BackgroundTasks: Run the function asynchronously
    :param request: Request: Get the base_url of the server
    :param db: AsyncSession: Get the database session
    :return: A message to the user
    :doc-author: Trelent
    """
    user = await repositories_users.get_user_by_email(body.email, db)

    if user:
        background_tasks.add_task(
            send_reset_passw_email, user.email, user.username, str(request.base_url)
        )
        return {"message": messages.CHECK_EMAIL_FOR_UPDATE_PASSWORD}
    else:
        return {"message": messages.USER_WITH_EMAIL_NOT_EXIST}


@auth_router.get("/form_reset_password/{token}")
async def recieve_conf_reset_passw():
    """
    The recieve_conf_reset_passw function is used to recieve confirmation for update password.
    It returns a JSON object with the message &quot;We recieved confirmation for update password&quot;.

    :return: A dictionary with a message
    :doc-author: Trelent
    """
    return {"message": messages.RECEIVED_CONFIRMATION}


@auth_router.post("/form_reset_password/{token}")
async def confirmed_reset_passw(
    body: UserResetPassword, token: str, db: AsyncSession = Depends(get_db)
):
    """
    The confirmed_reset_passw function is used to reset a user's password.
        It takes in the following parameters:
            body: UserResetPassword - The new password for the user.
            token: str - The verification token sent to the user's email address.

    :param body: UserResetPassword: Get the password from the user
    :param token: str: Get the email from the token
    :param db: AsyncSession: Get the database session
    :return: A dictionary with a message
    :doc-author: Trelent
    """
    email = await auth_service.get_email_from_token(token)
    user = await repositories_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=messages.VERIFICATION_ERROR
        )
    new_password = auth_service.get_password_hash(body.password2)
    if not auth_service.verify_password(body.password1, new_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.DIFFERENT_PASSWORD
        )
    await repositories_users.update_password(user, new_password, db)
    return {"message": messages.PASSWORD_UPDATE_SUCCESSFULLY}
