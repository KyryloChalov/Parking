from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from src.services.auth import auth_service
from src.conf.config import config

conf = ConnectionConfig(
    MAIL_USERNAME=config.MAIL_USERNAME,
    MAIL_PASSWORD=config.MAIL_PASSWORD,
    MAIL_FROM=config.MAIL_FROM,
    MAIL_PORT=config.MAIL_PORT,
    MAIL_SERVER=config.MAIL_SERVER,
    MAIL_FROM_NAME="OK",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / "templates",
)


async def send_email(email: EmailStr, username: str, host: str):
    """
    The send_email function sends an email to the user with a link to confirm their email address.
        The function takes in three parameters:
            -email: the user's email address, which is used as a recipient for the message.
            -username: this is used in the body of the message, and will be displayed in the letter in email-template.html.
            -host: this is where your website lives (e.g., &quot;localhost&quot; or &quot;127.0.0.1&quot;

    :param email: EmailStr: Specify the email address of the recipient
    :param username: str: Pass the username to the template
    :param host: str: Pass the hostname of the server to the template
    :return: A coroutine object that we can await
    :doc-author: Trelent
    """
    try:
        token_verification = auth_service.create_email_token({"sub": email})
        message = MessageSchema(
            subject="Confirm your email ",
            recipients=[email],
            template_body={
                "host": host,
                "username": username,
                "token": token_verification,
            },
            subtype=MessageType.html,
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="email_template.html")
    except ConnectionErrors as err:
        print(err)


async def send_reset_passw_email(email: EmailStr, username: str, host: str):
    """
    The send_reset_passw_email function sends an email to the user with a link to reset their password.
        Args:
            email (str): The user's email address.
            username (str): The username of the account that is requesting a password reset.

    :param email: EmailStr: Check if the email is valid
    :param username: str: Get the username of the user who requested a password reset
    :param host: str: Create the reset password link
    :return: object that we can await
    :doc-author: Trelent
    """
    try:
        token_verification = auth_service.create_email_token({"sub": email})
        message = MessageSchema(
            subject="Confirm reset password !",
            recipients=[email],
            template_body={
                "host": host,
                "username": username,
                "token": token_verification,
            },
            subtype=MessageType.html,
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="email_reset_passw.html")
    except ConnectionErrors as err:
        print(err)


async def send_email_by_license_plate(email: EmailStr, name: str, license_plate: str, days: int):
    """
    The send_email function sends an email to the user with a link to confirm their email address.
        The function takes in three parameters:
            -email: the user's email address, which is used as a recipient for the message.
            -username: this is used in the body of the message, and will be displayed in the letter in email-template.html.
            -host: this is where your website lives (e.g., &quot;localhost&quot; or &quot;127.0.0.1&quot;

    :param email: EmailStr: Specify the email address of the recipient
    :param username: str: Pass the username to the template
    :param host: str: Pass the hostname of the server to the template
    :return: A coroutine object that we can await
    :doc-author: Trelent
    """
    try:
        message = MessageSchema(
            subject=f"Reminder: Parking space rental expires in {days} days",
            recipients=[email],
            template_body={
                "username": name,
                "license_plate": license_plate,
                "days": days
            },
            subtype=MessageType.html,
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="email_user_vehicle.html")
    except ConnectionErrors as err:
        print(err)


async def send_email_info(email: EmailStr, name: str, subject: str, info: str):
    
    try:
        message = MessageSchema(
            subject=subject,
            recipients=[email],
            template_body={
                "username": name,
                "info": info,
            },
            subtype=MessageType.html,
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="email_info.html")
    except ConnectionErrors as err:
        print(err)