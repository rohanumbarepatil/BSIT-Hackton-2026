import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.main import app

def test_list_bins():
    with TestClient(app) as client:
        response = client.get("/api/v1/bins")
        assert response.status_code == 200
        assert len(response.json()) >= 5

def test_telemetry_and_status_calculation():
    with TestClient(app) as client:
        # Update bin to 75% -> WARNING
        payload = {"fill_percent": 75.0}
        response = client.post("/api/v1/bins/BIN-001/telemetry", json=payload)
        assert response.status_code == 200
        assert response.json()["status"] == "WARNING"

def test_overflow():
    with TestClient(app) as client:
        # Update bin to 100% -> OVERFLOW
        payload = {"fill_percent": 105.0}
        response = client.post("/api/v1/bins/BIN-001/telemetry", json=payload)
        assert response.status_code == 200
        assert response.json()["status"] == "OVERFLOW"

def test_prediction():
    with TestClient(app) as client:
        # BIN-003 was seeded with 2 readings: 10% 2 hours ago, and 80% now
        # Prediction should calculate the high fill rate and warn PREDICTED_FULL
        response = client.get("/api/v1/bins/BIN-003/prediction")
        assert response.status_code == 200
        data = response.json()
        assert data["prediction_status"] == "PREDICTED_FULL"
        assert data["fill_rate_per_hour"] == 35.0
        assert data["hours_to_full"] > 0

def test_collection_reset():
    with TestClient(app) as client:
        response = client.post("/api/v1/bins/BIN-005/collect")
        assert response.status_code == 200
        
        # Verify it reset to 0% and NORMAL
        bin_response = client.get("/api/v1/bins/BIN-005")
        assert bin_response.json()["current_fill_percent"] == 0.0
        assert bin_response.json()["status"] == "NORMAL"
