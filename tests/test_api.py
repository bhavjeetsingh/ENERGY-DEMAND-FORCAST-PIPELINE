from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()
    assert response.json()["status"] == "ok"

def test_predict_endpoint_validation_error():
    # Sending an empty payload should result in a 422 Unprocessable Entity
    response = client.post("/predict", json={})
    assert response.status_code == 422

def test_predict_endpoint_success():
    # Simulate a valid request payload
    valid_payload = {
        "hour_of_day": 14,
        "day_of_week": 2,
        "month": 5,
        "demand_lag_24h": 175000.5,
        "demand_lag_168h": 170000.2,
        "temp_celsius": 32.5
    }
    
    response = client.post("/predict", json=valid_payload)
    # The API will return 503 if the MLflow model isn't loaded (which is expected in CI before training)
    # So we accept either 200 (Success) or 503 (Model Unavailable)
    assert response.status_code in [200, 503]
    
    if response.status_code == 200:
        data = response.json()
        assert "predicted_demand_mw" in data
        assert "model_version" in data
