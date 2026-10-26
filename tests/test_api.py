"""Integration tests for FastAPI endpoints using TestClient."""

from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["dataset_ready"] is True
    assert data["total_restaurants"] > 10000


def test_get_cities_metadata():
    response = client.get("/api/v1/metadata/cities")
    assert response.status_code == 200
    data = response.json()
    assert "cities" in data
    assert "top_localities" in data
    assert "top_cuisines" in data
    assert len(data["top_localities"]) > 0
    assert len(data["top_cuisines"]) > 0


def test_get_localities():
    response = client.get("/api/v1/metadata/localities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 20
    assert "Indiranagar" in data or "Koramangala" in data


def test_get_cuisines():
    response = client.get("/api/v1/metadata/cuisines")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 20
    assert "Italian" in data or "North Indian" in data


def test_get_stats():
    response = client.get("/api/v1/metadata/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total_restaurants"] > 10000
    assert data["average_rating"] > 3.0


def test_recommendations_endpoint_success():
    payload = {
        "location": "Koramangala",
        "budget_tier": "medium",
        "cuisines": ["Italian", "Pizza"],
        "min_rating": 3.8,
        "special_preferences": "Casual dining with great pizza",
    }
    response = client.post("/api/v1/recommendations", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "recommendations" in data
    assert "summary" in data
    assert "provider_used" in data
    assert len(data["recommendations"]) > 0

    first_rec = data["recommendations"][0]
    assert "restaurant_id" in first_rec
    assert "restaurant_name" in first_rec
    assert "rating" in first_rec
    assert "estimated_cost_for_two" in first_rec
    assert "ai_explanation" in first_rec
    assert len(first_rec["ai_explanation"]) > 10


def test_recommendations_endpoint_validation_error():
    # min_rating exceeds 5.0 constraint -> should return 422 Unprocessable Entity
    invalid_payload = {
        "location": "Indiranagar",
        "min_rating": 8.5,
    }
    response = client.post("/api/v1/recommendations", json=invalid_payload)
    assert response.status_code == 422
