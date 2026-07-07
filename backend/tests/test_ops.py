"""Tests for the FIFA Operations Platform."""

import typing
import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def mock_httpx_client() -> typing.Generator[AsyncMock, None, None]:
    """Mocks the httpx.AsyncClient context manager to prevent outbound requests."""
    with patch("httpx.AsyncClient", autospec=True) as mock_class:
        mock_instance = mock_class.return_value
        # Mock the async context manager enter/exit methods
        mock_instance.__aenter__.return_value = mock_instance
        mock_instance.__aexit__.return_value = None
        yield mock_instance


@pytest.fixture(autouse=True)
def mock_ai_service() -> typing.Generator[AsyncMock, None, None]:
    """Mocks the AI operations service call."""
    with patch("app.main.analyze_stadium_operations", new_callable=AsyncMock) as mock_analyze:
        from app.services.ai_ops_service import GeminiOpsInsights
        mock_analyze.return_value = GeminiOpsInsights(
            stadium_zone_id="ZONE_A",
            crowd_density_index=0.8,
            transit_bottleneck_risk="MEDIUM",
            multilingual_dispatch_es="Mocked Spanish dispatch alert",
            fifa_safety_compliance=True
        )
        yield mock_analyze


def test_app_lifespan() -> None:
    """Verifies that the application lifespan initializes the HTTPX client correctly."""
    from fastapi import FastAPI
    with TestClient(app) as tc:
        assert isinstance(tc.app, FastAPI)
        assert tc.app.state.client is not None


def test_health_check() -> None:
    """Verifies the health check endpoint returns 200 and healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_analyze_stadium_operations_success() -> None:
    """Verifies a valid operations payload returns successfully with AI insights."""
    payload = {
        "stadium_zone_id": "ZONE_A",
        "current_crowd_count": 12000,
        "active_transit_vehicles": 15
    }
    response = client.post("/api/v1/operations/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["stadium_zone_id"] == "ZONE_A"
    assert data["crowd_density_index"] == 0.8
    assert data["transit_bottleneck_risk"] == "MEDIUM"
    assert "multilingual_dispatch_es" in data
    assert data["fifa_safety_compliance"] is True


def test_validation_error_negative_values() -> None:
    """Verifies that negative values trigger a 422 validation error."""
    payload = {
        "stadium_zone_id": "ZONE_A",
        "current_crowd_count": -500,
        "active_transit_vehicles": 10
    }
    response = client.post("/api/v1/operations/analyze", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert data["status"] == "error"
    assert "errors" in data
