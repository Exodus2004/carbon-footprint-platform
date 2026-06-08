from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

AUTH_HEADERS = {"Authorization": "Bearer mock_local_token"}


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


# ---------------------------------------------------------------------------
# Successful submission
# ---------------------------------------------------------------------------

def test_submit_carbon_data_success():
    payload = {
        "transportation_miles": 120.5,
        "energy_kwh": 350.0,
        "diet_meat_meals": 5
    }
    response = client.post("/api/v1/carbon", json=payload, headers=AUTH_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "insights" in data
    assert len(data["insights"]) > 0


def test_submit_zero_values():
    """All-zero values are valid and should not trigger a validation error."""
    payload = {
        "transportation_miles": 0,
        "energy_kwh": 0,
        "diet_meat_meals": 0
    }
    response = client.post("/api/v1/carbon", json=payload, headers=AUTH_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"


# ---------------------------------------------------------------------------
# Negative value edge cases (Pydantic ge=0 constraint)
# ---------------------------------------------------------------------------

def test_negative_transportation_miles():
    payload = {
        "transportation_miles": -10,
        "energy_kwh": 350.0,
        "diet_meat_meals": 5
    }
    response = client.post("/api/v1/carbon", json=payload, headers=AUTH_HEADERS)
    assert response.status_code == 422
    body = response.json()
    assert body["status"] == "error"
    assert any("transportation_miles" in e["field"] for e in body["errors"])


def test_negative_energy_kwh():
    payload = {
        "transportation_miles": 50,
        "energy_kwh": -999.9,
        "diet_meat_meals": 3
    }
    response = client.post("/api/v1/carbon", json=payload, headers=AUTH_HEADERS)
    assert response.status_code == 422
    body = response.json()
    assert body["status"] == "error"
    assert any("energy_kwh" in e["field"] for e in body["errors"])


def test_negative_diet_meat_meals():
    payload = {
        "transportation_miles": 50,
        "energy_kwh": 100,
        "diet_meat_meals": -1
    }
    response = client.post("/api/v1/carbon", json=payload, headers=AUTH_HEADERS)
    assert response.status_code == 422
    body = response.json()
    assert body["status"] == "error"
    assert any("diet_meat_meals" in e["field"] for e in body["errors"])


def test_all_negative_values():
    """Every single metric is negative — all three should be flagged."""
    payload = {
        "transportation_miles": -5,
        "energy_kwh": -20,
        "diet_meat_meals": -3
    }
    response = client.post("/api/v1/carbon", json=payload, headers=AUTH_HEADERS)
    assert response.status_code == 422
    body = response.json()
    assert len(body["errors"]) >= 3


# ---------------------------------------------------------------------------
# Empty / malformed payload edge cases
# ---------------------------------------------------------------------------

def test_empty_json_body():
    """An empty JSON object should fail validation for all required fields."""
    response = client.post("/api/v1/carbon", json={}, headers=AUTH_HEADERS)
    assert response.status_code == 422
    body = response.json()
    assert body["status"] == "error"
    assert len(body["errors"]) >= 3


def test_completely_empty_request_body():
    """Sending no body at all should fail with a 422."""
    response = client.post(
        "/api/v1/carbon",
        headers={**AUTH_HEADERS, "Content-Type": "application/json"},
        content=""
    )
    assert response.status_code == 422


def test_wrong_data_types():
    """String values instead of numbers should trigger validation errors."""
    payload = {
        "transportation_miles": "not_a_number",
        "energy_kwh": "bad",
        "diet_meat_meals": "oops"
    }
    response = client.post("/api/v1/carbon", json=payload, headers=AUTH_HEADERS)
    assert response.status_code == 422


def test_missing_partial_fields():
    """Only one field provided — the other two required fields should fail."""
    payload = {
        "transportation_miles": 100.0
    }
    response = client.post("/api/v1/carbon", json=payload, headers=AUTH_HEADERS)
    assert response.status_code == 422
    body = response.json()
    assert len(body["errors"]) >= 2


# ---------------------------------------------------------------------------
# Authorization edge cases
# ---------------------------------------------------------------------------

def test_missing_authorization_header():
    """No Authorization header at all."""
    payload = {
        "transportation_miles": 120.5,
        "energy_kwh": 350.0,
        "diet_meat_meals": 5
    }
    response = client.post("/api/v1/carbon", json=payload)
    assert response.status_code == 401


def test_empty_authorization_header():
    """Authorization header present but completely empty."""
    payload = {
        "transportation_miles": 120.5,
        "energy_kwh": 350.0,
        "diet_meat_meals": 5
    }
    response = client.post("/api/v1/carbon", json=payload, headers={"Authorization": ""})
    assert response.status_code == 401


def test_malformed_bearer_token():
    """Authorization header without 'Bearer' prefix."""
    payload = {
        "transportation_miles": 120.5,
        "energy_kwh": 350.0,
        "diet_meat_meals": 5
    }
    response = client.post("/api/v1/carbon", json=payload, headers={"Authorization": "Token abc123"})
    assert response.status_code == 401


def test_bearer_without_token():
    """Authorization header with 'Bearer' but no token string after it."""
    payload = {
        "transportation_miles": 120.5,
        "energy_kwh": 350.0,
        "diet_meat_meals": 5
    }
    response = client.post("/api/v1/carbon", json=payload, headers={"Authorization": "Bearer "})
    assert response.status_code == 401
