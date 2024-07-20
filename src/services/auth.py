import pickle
from datetime import datetime, timedelta
from typing import Optional

from fastapi.responses import JSONResponse
import redis
from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt

from src.database.db import get_db
from src.repository import users as repository_users
from src.conf.config import config
from src.conf.constants import ACCESS_TOKEN_TIME_LIVE


class Auth:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = config.SECRET_KEY_JWT
    ALGORITHM = config.ALGORITHM
    cache = redis.Redis(
        host=config.REDIS_DOMAIN,
        port=config.REDIS_PORT,
        db=0,
        password=config.REDIS_PASSWORD,
    )

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        return self.pwd_context.hash(password)

    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

    # define a function to generate a new access token
    async def create_access_token(
        self, data: dict, expires_delta: Optional[float] = None
    ):
        """
        The create_access_token function creates a new access token.

        :param self: Refer to the class itself
        :param data: dict: Store the data that is to be encoded in the jwt
        :param expires_delta: Optional[float]: Set the time for which the token is valid
        :return: A string of the encoded access token
        :doc-author: Trelent
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_TIME_LIVE)
        to_encode.update(
            {"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"}
        )
        encoded_access_token = jwt.encode(
            to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM
        )
        return encoded_access_token

    # define a function to generate a new refresh token
    async def create_refresh_token(
        self, data: dict, expires_delta: Optional[float] = None
    ):
        """
        The create_refresh_token function creates a refresh token for the user.
        The function takes in two parameters: data and expires_delta.
        Data is a dictionary containing the user's id, username, email address, and password hash.
        Expires_delta is an optional parameter that determines how long the refresh token will be valid for.

        :param self: Represent the instance of the class
        :param data: dict: Pass the user's data to be encoded in the token
        :param expires_delta: Optional[float]: Set the expiry time of the refresh token
        :return: A jwt token with the following claims:
        :doc-author: Trelent
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update(
            {"iat": datetime.utcnow(), "exp": expire, "scope": "refresh_token"}
        )
        encoded_refresh_token = jwt.encode(
            to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM
        )
        return encoded_refresh_token

    async def decode_refresh_token(self, refresh_token: str):
        """
        The decode_refresh_token function is used to decode the refresh token.
        It takes in a refresh_token as an argument and returns the email of the user if successful.
        If not, it raises an HTTPException with status code 401 (Unauthorized) and detail 'Invalid scope for token' or 'Could not validate credentials'.

        :param self: Represent the instance of a class
        :param refresh_token: str: Pass the refresh token to the function
        :return: A string
        :doc-author: Trelent
        """
        try:
            payload = jwt.decode(
                refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM]
            )
            if payload["scope"] == "refresh_token":
                email = payload["sub"]
                return email
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid scope for token",
            )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )

    async def get_current_user(
        self, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
    ):
        """
        The get_current_user function is a dependency that will be called by FastAPI to
        retrieve the current user for each request. It uses the OAuth2PasswordBearer
        to validate and decode the JWT token in the Authorization header of each request.

        :param self: Access the class variables
        :param token: str: Get the token from the request header
        :param db: AsyncSession: Get the database connection
        :return: A user object
        :doc-author: Trelent
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            # Decode JWT
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload["scope"] == "access_token":
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError as e:
            raise credentials_exception

        user_hash = str(email)
        user = self.cache.get(user_hash)

        if user is None:
            print("User from database")
            user = await repository_users.get_user_by_email(email, db)
            if user is None:
                raise credentials_exception

            # add check that user is logout
            logout_user = self.cache.get(user.username)
            if logout_user:
                logout_user = pickle.loads(logout_user)
                # print(logout_user)
                # print(token)
                if logout_user == token:
                    print("Current user is logout")
                    raise credentials_exception

            self.cache.set(user_hash, pickle.dumps(user))
            self.cache.expire(user_hash, 60)
        else:
            print("User from cache")
            user = pickle.loads(user)
            # add check that user is logout
            logout_user = self.cache.get(user.username)
            if logout_user:
                logout_user = pickle.loads(logout_user)
                print(logout_user)
                print(token)
                if logout_user == token:
                    raise credentials_exception
        return user

    def create_email_token(self, data: dict):
        """
        The create_email_token function creates a token that is used to verify the user's email address.
            The token contains the following information:
                - iat (issued at): The time when the token was created.
                - exp (expiration): The time when this token will expire and no longer be valid. This is set to 1 day from creation by default, but can be changed in config.py if desired.

        :param self: Make the method a bound method, which means that the first parameter will always be
        :param data: dict: Pass the data to be encoded into a token
        :return: A token that is encoded with the data passed to it
        :doc-author: Trelent
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=1)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire})
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token

    async def get_email_from_token(self, token: str):
        """
        The get_email_from_token function takes a token as an argument and returns the email address associated with that token.
        The function first tries to decode the token using jwt.decode, which will raise a JWTError if it fails to decode the token.
        If decoding is successful, then we return the email address from within the payload of our decoded JSON Web Token.

        :param self: Represent the instance of the class
        :param token: str: Pass in the token that was sent to the user's email
        :return: The email address of the user who is requesting a password reset
        :doc-author: Trelent
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            email = payload["sub"]
            return email
        except JWTError as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid token for email verification",
            )


auth_service = Auth()
