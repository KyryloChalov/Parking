from unittest.mock import Mock

import pytest
from sqlalchemy import select

from src.models.models import User
from src.conf import messages
from conftest import TestingSessionLocal, user_data


def test_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    response = client.post("api/auth/signup", json=user_data)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "password" not in data
    assert "avatar" in data


def test_signup_exist_user(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    response = client.post("api/auth/signup", json=user_data)
    assert response.status_code == 409, response.text
    data = response.json()
    assert data["detail"] == messages.ACCOUNT_EXIST


def test_login_not_confirmed_email(client):
    response = client.post(
        "api/auth/login",
        data={
            "username": user_data.get("email"),
            "password": user_data.get("password"),
        },
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == messages.EMAIL_NOT_CONFIRMED


def test_wrong_login(client):
    response = client.post(
        "api/auth/login",
        data={"username": "invalid@mail.com", "password": user_data.get("password")},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == messages.INVALID_EMAIL


@pytest.mark.asyncio
async def test_confirmed_email(get_email_token, client):
    token = get_email_token
    response = client.get(f"api/auth/confirmed_email/{token}")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == messages.EMAIL_CONFIRMED


@pytest.mark.asyncio
async def test_login(client):
    async with TestingSessionLocal() as session:
        current_user = await session.execute(
            select(User).where(User.email == user_data.get("email"))
        )
        current_user = current_user.scalar_one_or_none()
        if current_user:
            current_user.confirmed = True
            await session.commit()

    response = client.post(
        "api/auth/login",
        data={
            "username": user_data.get("email"),
            "password": user_data.get("password"),
        },
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert "token_type" in data


@pytest.mark.asyncio
async def test_already_confirmed_email(get_email_token, client):
    async with TestingSessionLocal() as session:
        current_user = await session.execute(
            select(User).where(User.email == user_data.get("email"))
        )
        current_user = current_user.scalar_one_or_none()
        if current_user:
            current_user.confirmed = True
            assert current_user.email == user_data.get("email")
            await session.commit()

    token = get_email_token
    response = client.get(f"api/auth/confirmed_email/{token}")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == messages.EMAIL_ALREADY_CONFIRMED


def test_login_wrong_password(client):
    response = client.post(
        "api/auth/login",
        data={"username": user_data.get("email"), "password": "idontknow"},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == messages.INVALID_PASSWORD


def test_login_wrong_email(client):
    response = client.post(
        "api/auth/login",
        data={"username": "email@gmail.com", "password": user_data.get("password")},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == messages.INVALID_EMAIL


def test_confirmed_email_invalid_token(client, get_email_token):
    token = get_email_token
    response = client.get(
        "api/auth/confirmed_email/{token}", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 422, response.text
    data = response.json()
    assert data["detail"] == messages.INVALID_TOKEN


def test_request_reset_password(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.routes.auth.send_reset_passw_email", mock_send_email)
    response = client.post("api/auth/reset_password", json=user_data)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == messages.CHECK_EMAIL_FOR_UPDATE_PASSWORD
    assert "password" not in data


def test_request_reset_password_wrong_user(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.routes.auth.send_reset_passw_email", mock_send_email)
    response = client.post("api/auth/reset_password", json={"email": "wrong@email.com"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == messages.USER_WITH_EMAIL_NOT_EXIST


def test_request_reset_password_wrong_email(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.routes.auth.send_reset_passw_email", mock_send_email)
    response = client.post("api/auth/reset_password", json={"email": "wrong"})
    assert response.status_code == 422, response.text


@pytest.mark.asyncio
async def test_request_email(client, monkeypatch):
    async with TestingSessionLocal() as session:
        current_user = await session.execute(
            select(User).where(User.email == user_data.get("email"))
        )
        current_user = current_user.scalar_one_or_none()
        if current_user:
            current_user.confirmed = False
            await session.commit()
        mock_send_email = Mock()
        monkeypatch.setattr("src.routes.auth.request_email", mock_send_email)
        response = client.post("api/auth/request_email", json=user_data)
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["message"] == messages.CHECK_EMAIL
        assert "password" not in data


@pytest.mark.asyncio
async def test_get_to_reset_password(get_email_token, client):
    token = get_email_token
    response = client.get(f"api/auth/form_reset_password/{token}")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == messages.RECEIVED_CONFIRMATION


def test_reset_password(client, get_email_token):
    token = get_email_token
    response = client.post(
        f"api/auth/form_reset_password/{token}",
        json={"password1": "password", "password2": "password"},
    )
    assert response.status_code == 200, response.text


# It looks like we don't have password.len() check
# def test_reset_password_not_valid(client, get_email_token):
#     token = get_email_token
#     response = client.post(f"api/auth/form_reset_password/{token}",
#                            json={"password1": "newpassword", "password2": "newpassword"})
#     assert response.status_code == 422, response.text
#     assert (
#         response.json()["detail"][0]["msg"]
#         == "String should have at most 8 characters"
#     )
#     assert (
#         response.json()["detail"][0]["type"]
#         == "string_too_long"
#     )


def test_reset_password_not_valid(client, get_email_token):
    token = get_email_token
    response = client.post(
        f"api/auth/form_reset_password/{token}",
        json={"password1": "pass", "password2": "pass"},
    )
    assert response.status_code == 422, response.text
    assert (
        response.json()["detail"][0]["msg"]
        == "String should have at least 5 characters"
    )
    assert response.json()["detail"][0]["type"] == "string_too_short"


def test_reset_password_not_the_same(client, get_email_token):
    token = get_email_token
    response = client.post(
        f"api/auth/form_reset_password/{token}",
        json={"password1": "password", "password2": "pasword"},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == messages.DIFFERENT_PASSWORD


# Oleksandr прибрав це. чекаємо відповіді, чому
# def test_logout(client):
#     response = client.post("api/auth/logout")
#     assert response.status_code == 200, response.text
#     data = response.json()
#     assert data["message"] == messages.LOGOUT
