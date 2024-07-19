from unittest.mock import Mock, patch, MagicMock, AsyncMock
from fastapi_limiter.depends import RateLimiter
import pytest

from src.services.auth import auth_service
from main import app
from src.conf import messages


def test_get_ratings_not_authorize(client, monkeypatch):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        response = client.get('/api/photos/{photo_id}/ratings')
        assert response.status_code == 401, response.text
        data = response.json()
        assert data["detail"] == "Not authenticated"


def test_get_ratings_not_found_by_id(client, get_token, monkeypatch):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        token = get_token
        photo_id = 123
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get(f'/api/photos/{photo_id}/ratings', headers=headers)
        assert response.status_code == 404, response.text
        data = response.json()
