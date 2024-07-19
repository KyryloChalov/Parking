from unittest.mock import Mock, MagicMock, patch, AsyncMock

import pytest
from sqlalchemy import select

from src.models.models import User
from src.conf import messages
from conftest import user_data, TestingSessionLocal


def test_signup(client, monkeypatch):
    mock_send_email = Mock(return_value=None)
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    response = client.post(
        "api/auth/signup",
        json=user_data,
    )
    assert response.status_code == 201, response.text
    data = response.json()

    assert user_data["email"] == data["email"]
    assert user_data["password"] not in data
    assert "avatar" in data
    
@pytest.mark.asyncio
async def test_login(client):
    async with TestingSessionLocal() as session:
        current_user = await session.execute(select(User).where(User.email == user_data.get("email")))
        current_user = current_user.scalar_one_or_none()
        if current_user:
            current_user.confirmed = True
            await session.commit()

    response = client.post("api/auth/login",
                           data={"username": user_data.get("email"), "password": user_data.get("password")})
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert "token_type" in data


# @pytest.mark.asyncio
# async def test_logout(client, get_email_token):
#     async with TestingSessionLocal() as session:
#         current_user = await session.execute(select(User).where(User.email == user_data.get("email")))
#         current_user = current_user.scalar_one_or_none()
#         if current_user:
#             current_user.confirmed = True
#             await session.commit()

#     # client.post("api/auth/login", data={"username": user_data.get("email"), "password": user_data.get("password")})
#     # tocken = get_email_token
#     print(user_data)
#     response = client.post("api/auth/logout", json=user_data)
#     assert response.status_code == 200, response.text
#     data = response.json()
#     assert data["message"] == messages.LOGOUT
    
